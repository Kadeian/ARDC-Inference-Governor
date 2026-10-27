"""Stateless organizer: caller owns the returned file; no database or server sessions."""

from datetime import date, timedelta
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from c4l.workforce.knowledge import SOURCES
from c4l.workforce.privacy import contains_sensitive


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class WorkEntry(StrictModel):
    activity_date: date
    organization: str = Field(min_length=1, max_length=100)
    role_or_activity: str = Field(min_length=1, max_length=120)
    method: Literal["application", "interview", "workshop", "other"]
    outcome: Literal["pending", "completed", "no_response", "not_selected", "offer"]

    @field_validator("organization", "role_or_activity")
    @classmethod
    def no_sensitive_fields(cls, value):
        if contains_sensitive(value):
            raise ValueError("Remove sensitive information")
        return value


class Deadline(StrictModel):
    task: Literal[
        "advisor_meeting",
        "employment_plan",
        "financial_literacy",
        "bid_letter",
        "training_approval",
        "training_start",
        "twc_notice_response",
        "payment_request",
    ]
    due_date: date
    confirmation: Literal["advisor_confirmed", "official_notice", "user_entered_unverified"]
    completed: bool = False


class OrganizerRequest(StrictModel):
    week_start: date
    work_search: list[WorkEntry] = Field(default_factory=list, max_length=100)
    deadlines: list[Deadline] = Field(default_factory=list, max_length=50)
    documents: dict[
        Literal[
            "resume",
            "employment_plan",
            "cost_quote",
            "class_completion",
            "advisor_checklist",
            "approval_notice",
        ],
        bool,
    ] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_week(self):
        if self.week_start.weekday() != 6:
            raise ValueError("Use a Sunday week start")
        end = self.week_start + timedelta(days=6)
        if any(not self.week_start <= entry.activity_date <= end for entry in self.work_search):
            raise ValueError("Activity outside the selected week")
        if any(entry.activity_date > date.today() for entry in self.work_search):
            raise ValueError("Only record activities that actually occurred")
        return self


def organize(record: OrganizerRequest, today: date | None = None) -> dict:
    today = today or date.today()
    return {
        "organizer": record.model_dump(mode="json"),
        "summary": {
            "recorded_activities": len(record.work_search),
            "missed_confirmed_deadlines": sum(
                not d.completed and d.due_date < today and d.confirmation != "user_entered_unverified"
                for d in record.deadlines
            ),
            "completed_tasks": sum(d.completed for d in record.deadlines),
        },
        "notice": "Preparation aid only. No activity is certified as qualifying. No deadline is inferred. "
        "No documents or identifiers are collected. Save this response yourself if you want "
        "to keep it; the server does not save it or send reminders. Follow TWC's official log fields.",
        "citations": [{"title": SOURCES["ui"].title, "url": SOURCES["ui"].url}],
    }
