from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class DatasetStateRow(Base):
    __tablename__ = "dataset_state"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    fingerprint: Mapped[str] = mapped_column(String(64))
    dataset_name: Mapped[str] = mapped_column(String(128))
    version: Mapped[str] = mapped_column(String(32))
    as_of_date: Mapped[date] = mapped_column(Date)


class EmployeeRow(Base):
    __tablename__ = "employees"

    employee_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    source: Mapped[str] = mapped_column(String(16))
    payload: Mapped[dict] = mapped_column(JSONB)


class HistoryRow(Base):
    __tablename__ = "activity_history"

    record_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    employee_id: Mapped[str] = mapped_column(
        ForeignKey("employees.employee_id"), index=True
    )
    event_id: Mapped[str] = mapped_column(String(64), index=True)
    activity_date: Mapped[date] = mapped_column(Date)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(32))
    completion_pct: Mapped[int] = mapped_column(Integer)
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    feedback_rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    assigned_by: Mapped[str] = mapped_column(String(16))
    source_row: Mapped[int] = mapped_column(Integer)
    origin: Mapped[str] = mapped_column(String(16))
    counts_in_replay: Mapped[bool] = mapped_column(Boolean)


class AccountRow(Base):
    __tablename__ = "accounts"

    username: Mapped[str] = mapped_column(String(128), primary_key=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(16))
    employee_id: Mapped[str | None] = mapped_column(
        ForeignKey("employees.employee_id"), nullable=True
    )


class SessionRow(Base):
    __tablename__ = "sessions"

    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    username: Mapped[str] = mapped_column(ForeignKey("accounts.username"), index=True)
    csrf_token: Mapped[str] = mapped_column(String(128))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class IdempotencyRow(Base):
    __tablename__ = "idempotency_keys"
    __table_args__ = (
        UniqueConstraint("employee_id", "idempotency_key", name="uq_employee_idempotency"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employee_id: Mapped[str] = mapped_column(ForeignKey("employees.employee_id"), index=True)
    idempotency_key: Mapped[str] = mapped_column(String(200))
    request_hash: Mapped[str] = mapped_column(String(64))
    record_id: Mapped[str] = mapped_column(ForeignKey("activity_history.record_id"))
