from __future__ import annotations

import secrets
from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, Request, Response, UploadFile
from pydantic import BaseModel, ConfigDict

from .errors import WorkflowError
from .settings import Settings, load_settings
from .store import Actor, PostgresStore
from .workflow import MAX_IMPORT_BYTES

router = APIRouter()
SESSION_COOKIE = "cq_session"
CSRF_COOKIE = "cq_csrf"


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    username: str
    password: str


class DemoLoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    role: Literal["employee", "hr"]


class CompleteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    session_date: date | None = None


def get_settings() -> Settings:
    return load_settings()


def get_store(settings: Settings = Depends(get_settings)) -> PostgresStore:
    return PostgresStore(settings)


def get_actor(
    request: Request,
    store: PostgresStore = Depends(get_store),
) -> Actor:
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        raise WorkflowError(
            401, "not_authenticated", "Authentication is required."
        )
    actor = store.actor_from_token(token)
    if actor is None:
        raise WorkflowError(
            401, "not_authenticated", "Authentication is required."
        )
    return actor


def require_csrf(
    request: Request,
    actor: Actor = Depends(get_actor),
    settings: Settings = Depends(get_settings),
) -> Actor:
    header = request.headers.get("x-csrf-token", "")
    cookie = request.cookies.get(CSRF_COOKIE, "")
    if not _same(header, cookie) or not _same(header, actor.csrf_token):
        raise WorkflowError(403, "csrf_failed", "CSRF validation failed.")
    origin = request.headers.get("origin")
    if origin and origin not in settings.allowed_origins:
        raise WorkflowError(403, "csrf_failed", "Origin is not allowed.")
    return actor


def _same(left: str, right: str) -> bool:
    left_bytes = left.encode("utf-8")
    right_bytes = right.encode("utf-8")
    if len(left_bytes) != len(right_bytes) or not left_bytes:
        return False
    return secrets.compare_digest(left_bytes, right_bytes)


def _set_auth_cookies(
    response: Response, settings: Settings, token: str, csrf: str
) -> None:
    max_age = settings.session_ttl_hours * 3600
    response.set_cookie(
        SESSION_COOKIE,
        token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        max_age=max_age,
        path="/",
    )
    response.set_cookie(
        CSRF_COOKIE,
        csrf,
        httponly=False,
        secure=settings.cookie_secure,
        samesite="lax",
        max_age=max_age,
        path="/",
    )


def _clear_auth_cookies(response: Response, settings: Settings) -> None:
    response.delete_cookie(
        SESSION_COOKIE,
        path="/",
        secure=settings.cookie_secure,
        samesite="lax",
    )
    response.delete_cookie(
        CSRF_COOKIE,
        path="/",
        secure=settings.cookie_secure,
        samesite="lax",
    )


def _own_employee(actor: Actor, employee_id: str) -> None:
    if actor.role == "hr":
        return
    if actor.role == "employee" and actor.employee_id == employee_id:
        return
    raise WorkflowError(404, "not_found", "Employee was not found.")


def _require_hr(actor: Actor) -> None:
    if actor.role != "hr":
        raise WorkflowError(403, "forbidden", "HR permission is required.")


@router.get("/api/ready")
def ready(store: PostgresStore = Depends(get_store)) -> dict[str, str]:
    store.ping()
    return {"status": "ready"}


@router.post("/api/auth/login")
def login(
    body: LoginRequest,
    response: Response,
    settings: Settings = Depends(get_settings),
    store: PostgresStore = Depends(get_store),
) -> dict[str, object]:
    actor, token = store.login(body.username, body.password)
    _set_auth_cookies(response, settings, token, actor.csrf_token)
    return {
        "username": actor.username,
        "role": actor.role,
        "employee_id": actor.employee_id,
        "csrf_token": actor.csrf_token,
    }


@router.post("/api/auth/demo-login")
def demo_login(
    body: DemoLoginRequest,
    response: Response,
    settings: Settings = Depends(get_settings),
    store: PostgresStore = Depends(get_store),
) -> dict[str, object]:
    demo = settings.demo_accounts
    if demo is None:
        raise WorkflowError(
            500,
            "configuration_error",
            "Demo login is not configured.",
        )
    if body.role == "employee":
        username = demo.employee_one_username
        password = demo.employee_one_password
    else:
        username = demo.hr_username
        password = demo.hr_password
    actor, token = store.login(username, password)
    if actor.role != body.role:
        store.logout(token)
        raise WorkflowError(
            500,
            "configuration_error",
            "Demo account role does not match its configuration.",
        )
    _set_auth_cookies(response, settings, token, actor.csrf_token)
    return {
        "username": actor.username,
        "role": actor.role,
        "employee_id": actor.employee_id,
        "csrf_token": actor.csrf_token,
    }


@router.get("/api/auth/me")
def me(actor: Actor = Depends(get_actor)) -> dict[str, object]:
    return {
        "username": actor.username,
        "role": actor.role,
        "employee_id": actor.employee_id,
        "csrf_token": actor.csrf_token,
    }


@router.post("/api/auth/logout")
def logout(
    request: Request,
    response: Response,
    settings: Settings = Depends(get_settings),
    actor: Actor = Depends(require_csrf),
    store: PostgresStore = Depends(get_store),
) -> dict[str, str]:
    token = request.cookies.get(SESSION_COOKIE, "")
    store.logout(token)
    _clear_auth_cookies(response, settings)
    return {"status": "logged_out"}


@router.get("/api/employees/{employee_id}")
def employee_profile(
    employee_id: str,
    actor: Actor = Depends(get_actor),
    store: PostgresStore = Depends(get_store),
) -> dict[str, object]:
    _own_employee(actor, employee_id)
    return store.profile(employee_id)


@router.get("/api/employees/{employee_id}/candidates")
def employee_candidates(
    employee_id: str,
    actor: Actor = Depends(get_actor),
    store: PostgresStore = Depends(get_store),
) -> dict[str, object]:
    _own_employee(actor, employee_id)
    return store.candidates(employee_id)


@router.get("/api/employees/{employee_id}/recommendations")
def employee_recommendations(
    employee_id: str,
    actor: Actor = Depends(get_actor),
    store: PostgresStore = Depends(get_store),
) -> dict[str, object]:
    _own_employee(actor, employee_id)
    return store.recommendations(employee_id)


@router.post("/api/employees/{employee_id}/activities/{event_id}/complete")
def complete_activity(
    employee_id: str,
    event_id: str,
    body: CompleteRequest,
    request: Request,
    actor: Actor = Depends(require_csrf),
    store: PostgresStore = Depends(get_store),
) -> dict[str, object]:
    _own_employee(actor, employee_id)
    idempotency_key = request.headers.get("idempotency-key", "").strip()
    if not idempotency_key:
        raise WorkflowError(
            400,
            "validation_error",
            "Idempotency-Key header is required.",
        )
    return store.complete(
        employee_id, event_id, idempotency_key, body.session_date
    )


@router.get("/api/hr/employees")
def hr_employees(
    actor: Actor = Depends(get_actor),
    store: PostgresStore = Depends(get_store),
) -> dict[str, object]:
    _require_hr(actor)
    return {"employees": store.employees()}


@router.get("/api/hr/overview")
def hr_overview(
    actor: Actor = Depends(get_actor),
    store: PostgresStore = Depends(get_store),
) -> dict[str, object]:
    _require_hr(actor)
    return store.overview()


@router.post("/api/hr/import")
async def hr_import(
    employees_file: UploadFile,
    history_file: UploadFile,
    actor: Actor = Depends(require_csrf),
    store: PostgresStore = Depends(get_store),
) -> dict[str, int]:
    _require_hr(actor)
    employees_payload = await _limited(employees_file)
    history_payload = await _limited(history_file)
    return store.import_package(employees_payload, history_payload)


async def _limited(upload: UploadFile) -> bytes:
    payload = await upload.read(MAX_IMPORT_BYTES + 1)
    if len(payload) > MAX_IMPORT_BYTES:
        raise WorkflowError(
            413, "payload_too_large", "An import file exceeds 1 MiB."
        )
    return payload
