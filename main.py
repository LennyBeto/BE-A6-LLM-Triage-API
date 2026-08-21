import sys
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from routes.triage import router as triage_router
except ModuleNotFoundError:  # pragma: no cover
    from .routes.triage import router as triage_router

load_dotenv()

app = FastAPI(title="LLM Triage API", version="1.0")

app.include_router(triage_router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Convert FastAPI's default 422 into the 400-naming-the-field shape the brief wants.
    first_error = exc.errors()[0]
    field = first_error["loc"][-1]
    return JSONResponse(
        status_code=400,
        content={"error": f"invalid or missing field: {field}", "detail": first_error["msg"]},
    )


@app.get("/health")
async def health():
    return {"status": "ok"}