from __future__ import annotations

from pathlib import Path

import uvicorn
from alembic import command
from alembic.config import Config

from .settings import load_settings
from .store import PostgresStore


def main() -> None:
    settings = load_settings()
    root = Path(__file__).resolve().parents[2]
    command.upgrade(Config(str(root / "alembic.ini")), "head")
    PostgresStore(settings).seed()
    uvicorn.run(
        "backend.career_quest.api:app",
        host="127.0.0.1",
        port=8000,
    )


if __name__ == "__main__":
    main()
