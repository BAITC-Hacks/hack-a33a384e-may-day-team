import os

import pytest

pytestmark = pytest.mark.skipif(
    not os.environ.get("DATABASE_URL"),
    reason="PostgreSQL integration NOT RUN: DATABASE_URL is not configured",
)


def test_postgres_login_logout_and_authorization() -> None:
    pytest.fail("PostgreSQL integration was not executed in this environment.")


def test_postgres_completion_is_durable_and_idempotent() -> None:
    pytest.fail("PostgreSQL integration was not executed in this environment.")


def test_postgres_parallel_completion_applies_once() -> None:
    pytest.fail("PostgreSQL integration was not executed in this environment.")


def test_postgres_repeatable_session_is_distinct_from_retry() -> None:
    pytest.fail("PostgreSQL integration was not executed in this environment.")


def test_postgres_import_is_atomic() -> None:
    pytest.fail("PostgreSQL integration was not executed in this environment.")
