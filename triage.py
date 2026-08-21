import os

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import openai

from llm.schema import TriageResult, Category, Urgency, SuggestedTeam
from llm.parse import get_triage_result

router = APIRouter()


class TriageInput(BaseModel):
    text: str = Field(min_length=1, max_length=2000)


STUB_RESULT = TriageResult(
    category=Category.bug,
    urgency=Urgency.normal,
    suggested_team=SuggestedTeam.engineering,
    confidence=0.42,
    reason="Stub mode — no model was called.",
)

FALLBACK_RESULT = TriageResult(
    category=Category.other,
    urgency=Urgency.normal,
    suggested_team=SuggestedTeam.general_support,
    confidence=0.0,
    reason="LLM_ENABLED is false — routed to general support for manual triage.",
)


@router.post("/triage")
async def triage(payload: TriageInput):
    if os.environ.get("LLM_STUB") == "1":
        return STUB_RESULT.model_dump()

    if os.environ.get("LLM_ENABLED", "true").lower() == "false":
        return FALLBACK_RESULT.model_dump()

    try:
        result = get_triage_result(payload.text)
    except openai.APITimeoutError:
        return JSONResponse(status_code=504, content={"error": "model call timed out"})

    if result is None:
        return JSONResponse(
            status_code=422,
            content={"error": "model could not produce a valid result after one repair attempt"},
        )

    return result.model_dump()