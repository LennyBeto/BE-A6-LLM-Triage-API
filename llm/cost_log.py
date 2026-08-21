import json
from datetime import datetime, timezone
from pathlib import Path

_LOG_PATH = Path(__file__).resolve().parent.parent / "cost_log.jsonl"


def log_call(prompt_version: str, model: str, input_tokens: int, output_tokens: int, duration_ms: float, repaired: bool):
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "prompt_version": prompt_version,
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "duration_ms": round(duration_ms, 2),
        "repaired": repaired,
    }

    with _LOG_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=True) + "\n")
