"""Curated official-source cards. No runtime web fetching or user-provided sources."""

from dataclasses import dataclass
from datetime import date
from urllib.parse import urlparse


@dataclass(frozen=True)
class Source:
    id: str
    title: str
    url: str
    reviewed_on: date
    jurisdiction: str


SOURCES = {
    "ui": Source(
        "ui",
        "TWC Unemployment Benefits Handbook",
        "https://www.twc.texas.gov/sites/default/files/ui/docs/unemployment-benefits-handbook-twc.pdf",
        date(2026, 10, 27),
        "Texas",
    ),
    "wioa": Source(
        "wioa",
        "TWC WIOA Guidelines (August 2025)",
        "https://www.twc.texas.gov/sites/default/files/wf/docs/wioa-guidelines-twc.pdf",
        date(2026, 10, 27),
        "Texas",
    ),
    "dol": Source(
        "dol",
        "DOL Adult and Dislocated Worker Program",
        "https://www.dol.gov/agencies/eta/workforce-investment/adult",
        date(2026, 10, 27),
        "Federal program overview; local service details vary",
    ),
    "etpl": Source(
        "etpl",
        "TWC Statewide ETPL policy update",
        "https://www.twc.texas.gov/policy-letters/statewide-eligible-training-providers-list-update",
        date(2026, 10, 27),
        "Texas; not a live provider-status lookup",
    ),
    "gulf": Source(
        "gulf",
        "Workforce Solutions Gulf Coast training scholarships",
        "https://www.wrksolutions.com/job-seekers/career-development-and-training/training-and-education-scholarships",
        date(2026, 10, 27),
        "Gulf Coast only; example, not statewide requirements",
    ),
}


def source_is_current(source: Source, today: date) -> bool:
    host = urlparse(source.url).hostname
    return (
        host in {"www.twc.texas.gov", "www.dol.gov", "www.wrksolutions.com"}
        and source.url.startswith("https://")
        and 0 <= (today - source.reviewed_on).days <= 30
    )


@dataclass(frozen=True)
class Card:
    title: str
    text: str
    source_ids: tuple[str, ...]
    question: str


CARDS = {
    "start": Card(
        "Start with two separate tracks",
        "Use TWC's own instructions for unemployment claims and work-search responsibilities. "
        "For career and training support, contact your local Workforce Solutions office and ask about "
        "WIOA Adult or Dislocated Worker services. Funding is not promised by this guide.",
        ("ui", "dol"),
        "Which unemployment and training steps should I complete next, and by what dates?",
    ),
    "work_search": Card(
        "Prepare your weekly work-search record",
        "Follow the minimum and any exemption TWC communicates to you; this guide will not guess a number. "
        "Keep a dated record of actual activities and be ready to provide it when TWC requests it. "
        "Our organizer is a preparation aid, not a substitute for every field on TWC's official log.",
        ("ui",),
        "What weekly minimum applies to me, what activities count, and which log fields must I keep?",
    ),
    "plan": Card(
        "Prepare for your employment plan",
        "TWC's WIOA guidance describes assessment and an Individual Employment Plan connecting goals "
        "with services. Ask your advisor which assessments and tasks apply to your case.",
        ("wioa",),
        "What goals, assessments, documents and completion dates belong in my employment plan?",
    ),
    "literacy": Card(
        "Confirm the financial-literacy step",
        "Financial literacy is among the services described in TWC's WIOA guidance. "
        "That does not establish that every Texas applicant must complete the same class. "
        "Ask your advisor whether it applies, how to register, and what completion proof is needed.",
        ("wioa",),
        "Is a financial-literacy class required in my plan, and what is the deadline?",
    ),
    "training": Card(
        "Check the exact training program with your advisor",
        "Texas maintains a statewide Eligible Training Providers List. Listing alone is not a funding "
        "award to you. Ask your advisor to verify the exact program, location, delivery format, "
        "local approval and funding before you commit to costs. This version cannot verify a school's live status.",
        ("etpl", "dol"),
        "Is this exact program currently approved for my local funding pathway, and what costs are covered?",
    ),
    "meeting": Card(
        "Arrive with a preparation checklist",
        "Prepare your career goals, training questions, appointment instructions and a list of documents "
        "your advisor requested. Ask how sensitive documents must be delivered through the official channel; "
        "do not upload them here. As a regional example only, Gulf Coast lists age, work authorization, "
        "income/public-assistance and applicable Selective Service documentation for certain services. "
        "Your local advisor must confirm your own checklist.",
        ("dol", "gulf"),
        "What should I bring, how should I submit it securely, and what happens after our meeting?",
    ),
    "bid": Card(
        "Ask about the local bid-letter process",
        "This source set does not establish a statewide bid-letter rule. Ask your advisor whether a "
        "school cost quote or bid letter is required, what it must contain, and how many options to obtain.",
        ("dol",),
        "Do I need a bid letter or itemized quote, and is there an approved format?",
    ),
    "earnings": Card(
        "Ask TWC how to report a work change",
        "TWC's handbook explains reporting work and earnings. Use its official reporting instructions; "
        "a message to a career advisor does not replace a required TWC report. Do not share account or ID numbers here.",
        ("ui",),
        "How should I report my work change to TWC and update my training plan?",
    ),
}
