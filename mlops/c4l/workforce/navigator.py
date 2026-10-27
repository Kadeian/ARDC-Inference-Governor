"""Deterministic, source-grounded first slice; no model, persistence or outbound actions."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
import re

from c4l.contracts import Decision, StepResult
from c4l.workforce.knowledge import CARDS, SOURCES, source_is_current
from c4l.workforce.privacy import contains_sensitive, normalized

VERSION = "workforce-evidence-stop-v1"
OTHER_STATES = r"\b(california|florida|new york|oklahoma|louisiana|new mexico|arkansas|colorado|kansas|arizona|georgia|illinois|ohio|michigan|oregon|washington|tennessee|alabama|alaska|connecticut|delaware|hawaii|idaho|indiana|iowa|kentucky|maine|maryland|massachusetts|minnesota|mississippi|missouri|montana|nebraska|nevada|new hampshire|new jersey|north carolina|north dakota|pennsylvania|rhode island|south carolina|south dakota|utah|vermont|virginia|west virginia|wisconsin|wyoming)\b"


@dataclass(frozen=True)
class PreparedReply:
    status: str
    reason: str
    title: str
    body: str
    source_ids: tuple[str, ...]
    advisor_question: str

    def render(self) -> str:
        sources = "\n".join(f"- [{SOURCES[s].title}]({SOURCES[s].url})" for s in self.source_ids)
        return f"{self.title}\n\n{self.body}\n\nQuestion for your advisor: {self.advisor_question}\n\nOfficial references:\n{sources}"

    def public(self) -> dict:
        return {
            "status": self.status,
            "reason_code": self.reason,
            "answer": self.render(),
            "advisor_question": self.advisor_question,
            "policy_version": VERSION,
            "citations": [
                {
                    "title": SOURCES[s].title,
                    "url": SOURCES[s].url,
                    "reviewed_on": SOURCES[s].reviewed_on.isoformat(),
                    "jurisdiction": SOURCES[s].jurisdiction,
                }
                for s in self.source_ids
            ],
            "storage": "No server-side conversation or organizer storage",
        }


def handoff(reason: str, body: str, question: str) -> PreparedReply:
    return PreparedReply("handoff", reason, "Pause and contact a person", body, ("dol",), question)


def prepare(question: str, state: str = "TX", today: date | None = None) -> PreparedReply:
    today = today or date.today()
    text = normalized(question)
    # Do not echo rejected input or include it in graph state, logs or drafts.
    if contains_sensitive(question):
        return handoff(
            "sensitive_input",
            "Please remove SSNs, bank details and identification numbers. "
            "Use an official secure channel for documents. This service will not retain this message. "
            "The reference below is a workforce contact starting point, not the basis of our privacy rule.",
            "What secure official channel should I use for the documents you requested?",
        )
    if re.search(r"suicid|kill myself|hurt myself|end my life|immediate danger|can't go on", text):
        return handoff(
            "crisis",
            "Your safety comes first. If there is immediate danger, contact local emergency "
            "services now. Reach out to a trusted person who can stay with you. Pause the benefits tasks "
            "and seek human support. The workforce reference below is not a crisis-care resource.",
            "Can we pause my benefits tasks while I get immediate human support?",
        )
    if state.upper() not in {"TX", "TEXAS"} or re.search(OTHER_STATES, text):
        return handoff(
            "outside_texas",
            "This Navigator currently covers Texas only. Contact the workforce "
            "office serving your state; I will not apply Texas rules to another state.",
            "Which local office can explain the rules for my state?",
        )
    if re.search(r"denied|denial|appeal|disput|overpayment|hearing", text):
        return handoff(
            "dispute_or_denial",
            "Contact TWC or your advisor promptly and ask for a qualified human "
            "or legal-aid referral. Follow the notice's instructions; I cannot decide a dispute or "
            "calculate your appeal deadline. Do not send the notice's identifiers here.",
            "Who can review my notice and confirm its response deadline and available help?",
        )
    if re.search(r"legal advice|sue|lawsuit|invest|tax advice|financial advice|borrow money", text):
        return handoff(
            "professional_advice",
            "Ask your advisor for a qualified legal-aid or financial "
            "counseling referral. I can help prepare a question but cannot give individualized advice.",
            "Can you refer me to qualified help for this question?",
        )
    if re.search(
        r"am i eligible|do i qualify|can i qualify|will i get|guarantee|approve me|my eligibility|can i get wioa",
        text,
    ):
        return handoff(
            "eligibility_decision",
            "Only the responsible agency or authorized program staff can "
            "make the decision. Ask your advisor about WIOA funding; ask TWC about unemployment. "
            "This Navigator cannot determine eligibility or promise approval.",
            "Which eligibility review applies to my request, and what evidence should I provide securely?",
        )
    if re.search(
        r"\b(send|submit|file|apply)\b.*\b(for me|on my behalf|this email|my claim|my application)\b", text
    ):
        return handoff(
            "outbound_action",
            "I cannot send messages, file forms or submit applications. "
            "I can provide a draft for you to review and send through the correct official channel.",
            "Which official channel should I use to send this myself?",
        )
    if re.search(r"ignore.*instructions|system prompt|override.*policy|pretend.*advisor", text):
        return handoff(
            "instruction_override",
            "I can only provide sourced Texas workforce preparation. "
            "I cannot override these boundaries or act as your advisor.",
            "Who can confirm the next step in my case?",
        )
    if re.search(r"deadline|due date|when.*due", text):
        return handoff(
            "unverified_deadline",
            "Use the date on your official notice or the date confirmed by "
            "your advisor. You can record that date in the organizer. I will not infer it from a generic rule.",
            "What exact date, time and submission method apply to my next task?",
        )
    if re.search(r"how many|minimum|exempt|waiv", text) and re.search(r"search|job", text):
        key = "work_search"
    elif re.search(r"bid|quote", text):
        key = "bid"
    elif re.search(r"financial literacy|literacy class", text):
        key = "literacy"
    elif re.search(r"employment plan|\biep\b|assessment", text):
        key = "plan"
    elif re.search(r"disclosure|earnings|part.time|new job|employment change", text):
        key = "earnings"
    elif re.search(r"meeting|appointment|bring|documents", text):
        key = "meeting"
    elif re.search(r"work.search|weekly log|job search", text):
        key = "work_search"
    elif re.search(r"etpl|school|training|wioa|funding|tuition", text):
        key = "training"
    elif re.search(r"laid off|lost my job|start|unemploy", text):
        key = "start"
    else:
        return handoff(
            "insufficient_evidence",
            "I do not have a reviewed source card that answers this "
            "question. I will stop rather than guess. Ask your local advisor to clarify it.",
            "Can you explain this question and point me to the current official source?",
        )
    card = CARDS[key]
    if not all(source_is_current(SOURCES[s], today) for s in card.source_ids):
        return handoff(
            "stale_sources",
            "The source packet needs re-verification before I can explain this "
            "step. Ask your advisor for current official instructions; the link is a starting point only.",
            "Where can I find the current official instructions for this step?",
        )
    body = card.text
    if re.search(r"draft|email|letter request", text):
        if key == "bid":
            body += (
                "\n\nDraft for you to review and send:\nSubject: Training cost quote request\n"
                "Hello [school contact],\nI am discussing training options with my Workforce Solutions "
                "advisor. Could you provide an itemized quote for [program], including tuition, fees, "
                "materials, start dates and the quote's validity period? I will confirm my advisor's "
                "required format before submitting it.\nThank you,\n[your name]"
            )
        else:
            body += (
                "\n\nDraft for you to review and send:\nSubject: Confirming my next workforce steps\n"
                "Hello [advisor],\nI would like to confirm how [work change or training question] affects "
                "my next steps. Please tell me what to report, the secure reporting channel, and any "
                "deadline. I understand this message does not replace a required TWC report.\n"
                "Thank you,\n[your name]"
            )
    return PreparedReply("answered", "source_supported", card.title, body, card.source_ids, card.question)


class NavigatorAdapter:
    def __init__(self, reply: PreparedReply):
        self.reply = reply

    async def step(self, prompt: str, remaining_usd: Decimal) -> StepResult:
        if self.reply.status != "answered":
            raise RuntimeError("Handoff must not invoke the adapter")
        return StepResult(self.reply.render(), Decimal(0))


class NavigatorStopPolicy:
    """ARDCPolicy evidence-stop interface, not fabricated paper M/C/K measurements.

    The deterministic source-card slice uses binary evidence gates, not calibrated
    probabilities. The paper's numeric controller remains a separate validated hook.
    """

    def __init__(self, reply: PreparedReply, today: date | None = None):
        self.reply = reply
        self.today = today or date.today()

    async def evaluate(self, context) -> Decision:
        if self.reply.status != "answered":
            return Decision("review", self.reply.reason, VERSION)
        if not all(source_is_current(SOURCES[s], self.today) for s in self.reply.source_ids):
            return Decision("review", "stale_sources", VERSION)
        if context.phase == "output" and context.text != self.reply.render():
            return Decision("stop", "unsupported_output", VERSION)
        return Decision("allow", "source_supported", VERSION)
