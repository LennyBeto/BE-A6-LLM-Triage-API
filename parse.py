import json
import re
from datetime import datetime, timezone
from pathlib import Path

from pydantic import ValidationError

from llm.schema import TriageResult
from llm.client import call_model, load_prompt, PROMPT_VERSION

QUARANTINE_PATH = Path(__file__).resolve().parent.parent.parent / "logs" / "quarantine.jsonl"


def extract_json(raw_text: str) -> dict:
    """Strips code fences / preamble text models sometimes add, then parses JSON.

    Raises json.JSONDecodeError if no valid JSON object can be found.
    """
    # Strip a ```json ... ``` or ``` ... ``` fence if present
    fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw_text, re.DOTALL)
    if fence_match:
        candidate = fence_match.group(1)
    else:
        # Fall back to the first {...} block found anywhere in the text
        brace_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        candidate = brace_match.group(0) if brace_match else raw_text

    return json.loads(candidate)


def _quarantine(user_text: str, raw_output: str, error: str) -> None:
    QUARANTINE_PATH.parent.mkdir(exist_ok=True)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "input": user_text,
        "raw_output": raw_output,
        "error": error,
        "prompt_version": PROMPT_VERSION,
    }
    with QUARANTINE_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def get_triage_result(user_text: str) -> TriageResult | None:
    """Calls the model, parses + validates the answer, repairs once on failure.

    Returns a validated TriageResult, or None if both attempts failed
    (in which case the failure has already been quarantined).
    """
    raw = call_model(user_text)

    try:
        parsed = extract_json(raw)
        return TriageResult(**parsed)
    except (json.JSONDecodeError, ValidationError) as first_error:
        repaired = _repair(user_text, raw, str(first_error))
        if repaired is not None:
            return repaired

        _quarantine(user_text, raw, str(first_error))
        return None


def _repair(user_text: str, broken_output: str, error_message: str) -> TriageResult | None:
    """One extra call: hand the model its own broken output and the exact error, ask again."""
    repair_messages = [
        {"role": "assistant", "content": broken_output},
        {
            "role": "user",
            "content": (
                f"Your previous answer was rejected for this reason: {error_message}. "
                "Return only corrected JSON matching the schema."
            ),
        },
    ]
    raw_retry = call_model(user_text, extra_messages=repair_messages, repaired=True)

    try:
        parsed = extract_json(raw_retry)
        return TriageResult(**parsed)
    except (json.JSONDecodeError, ValidationError):
        return None  # give up cleanly — caller quarantines