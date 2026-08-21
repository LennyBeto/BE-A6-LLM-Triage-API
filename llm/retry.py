import time
from functools import wraps


def call_with_retry(fn, *args, max_attempts=3, delay=1.0, **kwargs):
    """Retry a callable on transient exceptions with a simple backoff."""
    last_error = None
    for attempt in range(1, max_attempts + 1):
        try:
            return fn(*args, **kwargs)
        except Exception as exc:  # pragma: no cover - simple retry wrapper
            last_error = exc
            if attempt == max_attempts:
                raise
            time.sleep(delay)
    if last_error is not None:
        raise last_error
    raise RuntimeError("call_with_retry failed without an error")
