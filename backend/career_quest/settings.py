from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy.engine.url import make_url

from .errors import WorkflowError

ALLOWED_DATABASES = frozenset({"career_quest_dev", "career_quest_test"})
DEMO_VARIABLES = (
    "DEMO_EMPLOYEE_ONE_USERNAME",
    "DEMO_EMPLOYEE_ONE_PASSWORD",
    "DEMO_EMPLOYEE_ONE_ID",
    "DEMO_EMPLOYEE_TWO_USERNAME",
    "DEMO_EMPLOYEE_TWO_PASSWORD",
    "DEMO_EMPLOYEE_TWO_ID",
    "DEMO_HR_USERNAME",
    "DEMO_HR_PASSWORD",
)


@dataclass(frozen=True)
class DemoAccounts:
    employee_one_username: str
    employee_one_password: str
    employee_one_id: str
    employee_two_username: str
    employee_two_password: str
    employee_two_id: str
    hr_username: str
    hr_password: str


@dataclass(frozen=True)
class Settings:
    database_url: str | None
    dataset_path: str | None
    allowed_origins: tuple[str, ...]
    cookie_secure: bool
    session_ttl_hours: int
    demo_accounts: DemoAccounts | None


def load_local_env() -> None:
    if getattr(load_local_env, "done", False):
        return
    setattr(load_local_env, "done", True)
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=False)


def load_settings() -> Settings:
    load_local_env()
    origins = tuple(
        item.strip()
        for item in os.environ.get(
            "ALLOWED_ORIGINS",
            "http://127.0.0.1:5173,http://localhost:5173",
        ).split(",")
        if item.strip()
    )
    ttl_text = os.environ.get("SESSION_TTL_HOURS", "12")
    try:
        ttl = int(ttl_text)
    except ValueError as exc:
        raise WorkflowError(
            500,
            "configuration_error",
            "SESSION_TTL_HOURS must be an integer.",
        ) from exc
    if ttl <= 0:
        raise WorkflowError(
            500,
            "configuration_error",
            "SESSION_TTL_HOURS must be positive.",
        )
    return Settings(
        database_url=os.environ.get("DATABASE_URL") or None,
        dataset_path=os.environ.get("DATASET_PATH") or None,
        allowed_origins=origins,
        cookie_secure=os.environ.get("COOKIE_SECURE", "false").lower()
        == "true",
        session_ttl_hours=ttl,
        demo_accounts=_demo_accounts(),
    )


def _demo_accounts() -> DemoAccounts | None:
    values = {name: os.environ.get(name, "") for name in DEMO_VARIABLES}
    if not any(values.values()):
        return None
    missing = [name for name, value in values.items() if not value]
    if missing:
        raise WorkflowError(
            500,
            "configuration_error",
            "Demo account configuration is incomplete.",
            {"missing": missing},
        )
    return DemoAccounts(
        employee_one_username=values["DEMO_EMPLOYEE_ONE_USERNAME"],
        employee_one_password=values["DEMO_EMPLOYEE_ONE_PASSWORD"],
        employee_one_id=values["DEMO_EMPLOYEE_ONE_ID"],
        employee_two_username=values["DEMO_EMPLOYEE_TWO_USERNAME"],
        employee_two_password=values["DEMO_EMPLOYEE_TWO_PASSWORD"],
        employee_two_id=values["DEMO_EMPLOYEE_TWO_ID"],
        hr_username=values["DEMO_HR_USERNAME"],
        hr_password=values["DEMO_HR_PASSWORD"],
    )


def assert_safe_database(database_url: str) -> str:
    name = make_url(database_url).database
    if name not in ALLOWED_DATABASES:
        raise WorkflowError(
            500,
            "database_not_allowed",
            "Refusing to use a database outside the local Career Quest set.",
            {"allowed": sorted(ALLOWED_DATABASES)},
        )
    return name
