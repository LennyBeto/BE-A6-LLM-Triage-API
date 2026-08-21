import random
import time

import openai

MAX_ATTEMPTS = 3  # 1 initial call + 2 retries


def call_with_retry(fn, *args, **kwargs):
    """Calls fn(*args, **kwargs), retrying on timeouts, 429, and 5xx only.

    Never retries 400/401/403 — those will still be wrong on the next attempt,
    and on a metered free tier every pointless retry burns real quota.
    """
    last_exception = None

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            return fn(*args, **kwargs)

        except openai.APITimeoutError as e:
            last_exception = e
            should_retry = True

        except openai.RateLimitError as e:
            last_exception = e
            should_retry = True
            retry_after = _extract_retry_after(e)
            if retry_after is not None:
                time.sleep(retry_after)
                continue  # obey Retry-After instead of our own backoff

        except openai.APIStatusError as e:
            last_exception = e
            should_retry = e.status_code >= 500

        except (openai.AuthenticationError, openai.PermissionDeniedError, openai.BadRequestError) as e:
            # 401 / 403 / 400 — never retried, fail fast
            raise

        if not should_retry or attempt == MAX_ATTEMPTS:
            raise last_exception

        backoff = (2 ** (attempt - 1)) + random.uniform(0, 0.5)  # 1s, 2s, 4s + jitter
        time.sleep(backoff)

    raise last_exception


def _extract_retry_after(exc) -> float | None:
    try:
        header_value = exc.response.headers.get("retry-after")
        return float(header_value) if header_value else None
    except Exception:
        return None