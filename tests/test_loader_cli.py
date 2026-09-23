from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path

import pytest

from backend.career_quest.cli import main
from backend.career_quest.engine import audit_dataset
from backend.career_quest.loader import DatasetValidationError, load_dataset


def test_loader_accepts_arbitrary_employee_ids(
    synthetic_dataset_path: Path,
) -> None:
    dataset = load_dataset(synthetic_dataset_path)

    assert "EMP-new-alpha" in dataset.employees
    assert len(dataset.employees) == 3


def test_unknown_skill_reports_file_record_field_and_reason(
    synthetic_dataset_path: Path, tmp_path: Path
) -> None:
    broken_path = tmp_path / "broken_reference"
    shutil.copytree(synthetic_dataset_path, broken_path)
    employees_file = broken_path / "employees.json"
    payload = json.loads(employees_file.read_text(encoding="utf-8"))
    payload["employees"][0]["skills"]["S_DOES_NOT_EXIST"] = 2
    employees_file.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(DatasetValidationError) as caught:
        load_dataset(broken_path)

    message = str(caught.value)
    assert "employees.json" in message
    assert "EMP-new-alpha" in message
    assert "skills.S_DOES_NOT_EXIST" in message
    assert "unknown skill reference" in message


def test_invalid_history_status_has_explainable_error(
    synthetic_dataset_path: Path, tmp_path: Path
) -> None:
    broken_path = tmp_path / "broken_status"
    shutil.copytree(synthetic_dataset_path, broken_path)
    history_file = broken_path / "activity_history.csv"
    with history_file.open(encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source))
    rows[0]["status"] = "mysterious"
    with history_file.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    with pytest.raises(DatasetValidationError) as caught:
        load_dataset(broken_path)

    message = str(caught.value)
    assert "activity_history.csv" in message
    assert "R_BEFORE" in message
    assert "field=status" in message
    assert "unsupported value" in message


def test_duplicate_nested_json_key_is_rejected(
    synthetic_dataset_path: Path, tmp_path: Path
) -> None:
    broken_path = tmp_path / "duplicate_json_key"
    shutil.copytree(synthetic_dataset_path, broken_path)
    employees_file = broken_path / "employees.json"
    source = employees_file.read_text(encoding="utf-8")
    original = '"S_CODE": 2,'
    assert source.count(original) == 1
    employees_file.write_text(
        source.replace(
            original,
            '"S_CODE": 0,\n        "S_CODE": 2,',
            1,
        ),
        encoding="utf-8",
    )

    with pytest.raises(DatasetValidationError) as caught:
        load_dataset(broken_path)

    message = str(caught.value)
    assert "employees.json" in message
    assert "field=json" in message
    assert "duplicate JSON object key 'S_CODE'" in message


def test_duplicate_csv_header_is_rejected(
    synthetic_dataset_path: Path, tmp_path: Path
) -> None:
    broken_path = tmp_path / "duplicate_csv_header"
    shutil.copytree(synthetic_dataset_path, broken_path)
    history_file = broken_path / "activity_history.csv"
    with history_file.open(encoding="utf-8", newline="") as source:
        rows = list(csv.reader(source))
    duplicate_index = rows[0].index("employee_id") + 1
    rows[0].insert(duplicate_index, "employee_id")
    for row in rows[1:]:
        row.insert(duplicate_index, row[duplicate_index - 1])
    with history_file.open("w", encoding="utf-8", newline="") as target:
        csv.writer(target).writerows(rows)

    with pytest.raises(DatasetValidationError) as caught:
        load_dataset(broken_path)

    message = str(caught.value)
    assert "activity_history.csv" in message
    assert "record=header" in message
    assert "duplicate column names: employee_id" in message


@pytest.mark.parametrize(
    "duration",
    ["NaN", "Infinity", "-Infinity", "1e400"],
)
def test_non_finite_duration_is_rejected(
    synthetic_dataset_path: Path, tmp_path: Path, duration: str
) -> None:
    broken_path = tmp_path / f"non_finite_{duration}"
    shutil.copytree(synthetic_dataset_path, broken_path)
    events_file = broken_path / "events.json"
    source = events_file.read_text(encoding="utf-8")
    original = '"duration_hours": 2,'
    assert original in source
    events_file.write_text(
        source.replace(
            original,
            f'"duration_hours": {duration},',
            1,
        ),
        encoding="utf-8",
    )

    with pytest.raises(DatasetValidationError) as caught:
        load_dataset(broken_path)

    message = str(caught.value)
    assert "events.json" in message
    assert "field=duration_hours" in message
    assert "must be a finite number" in message


def test_dates_require_exact_yyyy_mm_dd_format(
    synthetic_dataset_path: Path, tmp_path: Path
) -> None:
    broken_path = tmp_path / "broken_date"
    shutil.copytree(synthetic_dataset_path, broken_path)
    skills_file = broken_path / "skills.json"
    payload = json.loads(skills_file.read_text(encoding="utf-8"))
    payload["meta"]["as_of_date"] = "20260120"
    skills_file.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(DatasetValidationError) as caught:
        load_dataset(broken_path)

    message = str(caught.value)
    assert "skills.json" in message
    assert "field=as_of_date" in message
    assert "YYYY-MM-DD" in message


def test_invalid_utf8_is_wrapped_as_dataset_error(
    synthetic_dataset_path: Path, tmp_path: Path
) -> None:
    broken_path = tmp_path / "broken_encoding"
    shutil.copytree(synthetic_dataset_path, broken_path)
    (broken_path / "employees.json").write_bytes(b"\xff\xfe\x00")

    with pytest.raises(DatasetValidationError) as caught:
        load_dataset(broken_path)

    message = str(caught.value)
    assert "employees.json" in message
    assert "field=encoding" in message
    assert "invalid UTF-8" in message


def test_audit_recalculates_counts_and_growth(
    synthetic_dataset_path: Path,
) -> None:
    audit = audit_dataset(load_dataset(synthetic_dataset_path))

    assert audit["counts"] == {
        "skills": 5,
        "role_profiles": 8,
        "employees": 3,
        "events": 14,
        "history_records": 11,
    }
    assert audit["recalculated_growth"] == {
        "completed_records_after_review_through_as_of": 3,
        "employees_with_positive_growth": 1,
        "positive_skill_change_trace_entries": 2,
        "total_skill_level_gain": 2,
    }


def test_cli_outputs_diagnostic_and_audit(
    synthetic_dataset_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    exit_code = main(
        [str(synthetic_dataset_path), "EMP-new-alpha", "--audit"]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["dataset"]["as_of_date"] == "2026-01-20"
    assert payload["employee"]["primary_target"] == {
        "role": "Engineer",
        "grade": "Middle",
    }
    assert payload["audit"]["counts"]["employees"] == 3
