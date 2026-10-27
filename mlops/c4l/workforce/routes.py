"""Dedicated Navigator routes; blocked raw text never enters the orchestration state."""

import os
import time
import uuid

from fastapi import APIRouter, HTTPException, Request
from pydantic import Field

from c4l.contracts import Limits
from c4l.engine import run
from c4l.telemetry import LATENCY, REQUESTS
from c4l.workforce.navigator import NavigatorAdapter, NavigatorStopPolicy, handoff, prepare
from c4l.workforce.organizer import OrganizerRequest, StrictModel, organize


def reference_gate():
    if os.getenv("ENVIRONMENT", "local") != "local":
        raise HTTPException(
            503, "Navigator reference version requires source and policy approval before live use"
        )


router = APIRouter()


class NavigationRequest(StrictModel):
    question: str = Field(min_length=1, max_length=6000)
    state: str = Field(default="TX", min_length=2, max_length=30)


@router.post("/v1/navigator")
async def navigate(body: NavigationRequest, request: Request):
    reference_gate()
    if request.app.state.slots.locked():
        raise HTTPException(429, "Capacity reached", headers={"Retry-After": "5"})
    reply = prepare(body.question, body.state)
    request_id = str(uuid.uuid4())
    if reply.status != "answered":
        REQUESTS.labels("handoff").inc()
        return {"request_id": request_id, **reply.public()}
    started = time.monotonic()
    try:
        # No user text is needed beyond the deterministic preflight; pass an opaque constant.
        async with request.app.state.slots:
            result = await run(
                "reviewed_workforce_card", NavigatorAdapter(reply), NavigatorStopPolicy(reply), Limits()
            )
        if result["status"] != "completed":
            safe = handoff(
                "governance_stop",
                "The evidence or output check did not pass. Please ask a human advisor to confirm this step.",
                "Can you confirm the next step?",
            )
            REQUESTS.labels("handoff").inc()
            return {"request_id": request_id, **safe.public()}
        REQUESTS.labels("completed").inc()
        return {"request_id": request_id, **reply.public()}
    except Exception:
        REQUESTS.labels("error").inc()
        raise HTTPException(
            503, {"request_id": request_id, "reason_code": "navigation_unavailable"}
        ) from None
    finally:
        LATENCY.observe(time.monotonic() - started)


@router.post("/v1/navigator/organizer")
async def organizer(body: OrganizerRequest):
    reference_gate()
    return organize(body)
