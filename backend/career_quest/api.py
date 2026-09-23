from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .errors import WorkflowError
from .http_api import router
from .settings import load_settings

app = FastAPI(
    title="Career Quest Backend",
    version="0.2.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)
app.include_router(router)
_settings = load_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(_settings.allowed_origins),
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "X-CSRF-Token", "Idempotency-Key"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "career-quest-backend"}


@app.exception_handler(WorkflowError)
def handle_workflow_error(request: Request, exc: WorkflowError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.code,
            "message": exc.message,
            "details": exc.details,
        },
    )


@app.exception_handler(RequestValidationError)
def handle_validation_error(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={
            "code": "validation_error",
            "message": "Request validation failed.",
            "details": {
                "errors": [
                    {"loc": list(error["loc"]), "type": error["type"]}
                    for error in exc.errors()
                ]
            },
        },
    )
