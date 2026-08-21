import re

from .schema import Category, SuggestedTeam, TriageResult, Urgency


def _classify_text(text: str) -> tuple[Category, SuggestedTeam, Urgency, str]:
    message = (text or "").lower()
    billing_terms = {"billing", "charge", "refund", "invoice", "payment", "credit", "subscription"}
    bug_terms = {"bug", "error", "crash", "broken", "fail", "not working", "issue", "exception"}
    feature_terms = {"feature", "request", "enhancement", "improvement", "idea", "missing option"}

    if billing_terms & set(re.findall(r"[a-z]+", message)):
        return (
            Category.billing,
            SuggestedTeam.billing_support,
            Urgency.high if "urgent" in message or "immediately" in message else Urgency.normal,
            "Billing or payment issue requires billing support review.",
        )

    if bug_terms & set(re.findall(r"[a-z]+", message)):
        return (
            Category.bug,
            SuggestedTeam.engineering,
            Urgency.high if "down" in message or "urgent" in message else Urgency.normal,
            "This appears to be a product bug and should be routed to engineering.",
        )

    if feature_terms & set(re.findall(r"[a-z]+", message)):
        return (
            Category.feature,
            SuggestedTeam.product,
            Urgency.low,
            "This looks like a feature request or product improvement.",
        )

    return (
        Category.other,
        SuggestedTeam.general_support,
        Urgency.normal,
        "This request is unclear; it should be reviewed by general support.",
    )


def get_triage_result(text: str) -> TriageResult:
    category, suggested_team, urgency, reason = _classify_text(text)
    confidence = 0.72 if category != Category.other else 0.38
    return TriageResult(
        category=category,
        urgency=urgency,
        suggested_team=suggested_team,
        confidence=confidence,
        reason=reason,
    )
