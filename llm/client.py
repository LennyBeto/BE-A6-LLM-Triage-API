import os
import time
from pathlib import Path

from openai import OpenAI

from .cost_log import log_call
from .retry import call_with_retry

PROMPT_VERSION = "triage-v1"
PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / f"{PROMPT_VERSION}.md"

_client: OpenAI | None = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            base_url=os.environ["LLM_BASE_URL"],
            api_key=os.environ["OPENAI_API_KEY"],
            timeout=30.0,
            max_retries=0,
        )
    return _client


def load_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def call_model(user_text: str, extra_messages: list[dict] | None = None, repaired: bool = False) -> str:
    """Sends the versioned system prompt + user text (+ optional repair messages)."""
    client = get_client()
    messages = [{"role": "system", "content": load_prompt()}, {"role": "user", "content": user_text}]
    if extra_messages:
        messages.extend(extra_messages)

    start = time.monotonic()
    response = call_with_retry(
        client.chat.completions.create,
        model=os.environ["LLM_MODEL"],
        temperature=0.2,
        messages=messages,
    )
    duration_ms = (time.monotonic() - start) * 1000

    usage = response.usage
    log_call(
        prompt_version=PROMPT_VERSION,
        model=os.environ["LLM_MODEL"],
        input_tokens=usage.prompt_tokens if usage else 0,
        output_tokens=usage.completion_tokens if usage else 0,
        duration_ms=duration_ms,
        repaired=repaired,
    )

    return response.choices[0].message.content
