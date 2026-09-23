from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from datetime import date
from pathlib import Path
from typing import Sequence

from .engine import EmployeeNotFoundError, audit_dataset, employee_diagnostic
from .loader import DatasetValidationError, load_dataset


def _json_default(value: object) -> object:
    if isinstance(value, date):
        return value.isoformat()
    raise TypeError(f"cannot serialize {type(value).__name__}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate Career Quest data and print deterministic employee facts."
        )
    )
    parser.add_argument(
        "dataset_path",
        type=Path,
        help="directory containing the four official dataset files",
    )
    parser.add_argument(
        "employee_id",
        nargs="?",
        help="employee to diagnose; arbitrary valid dataset IDs are accepted",
    )
    parser.add_argument(
        "--audit",
        action="store_true",
        help="also recalculate aggregate counts and skill growth",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.employee_id is None and not args.audit:
        parser.error("employee_id is required unless --audit is used")

    try:
        dataset = load_dataset(args.dataset_path)
        payload: dict[str, object] = {
            "dataset": {
                "name": dataset.name,
                "version": dataset.version,
                "as_of_date": dataset.as_of_date,
            }
        }
        if args.employee_id is not None:
            payload["employee"] = asdict(
                employee_diagnostic(dataset, args.employee_id)
            )
        if args.audit:
            payload["audit"] = audit_dataset(dataset)
    except (DatasetValidationError, EmployeeNotFoundError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(
        json.dumps(
            payload,
            default=_json_default,
            ensure_ascii=False,
            indent=2,
            sort_keys=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
