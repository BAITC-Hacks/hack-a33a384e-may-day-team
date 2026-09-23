"""Validated deterministic core for Career Quest."""

from .engine import (
    analyze_candidates,
    calculate_current_skills,
    employee_diagnostic,
)
from .loader import DatasetValidationError, load_dataset

__all__ = [
    "DatasetValidationError",
    "analyze_candidates",
    "calculate_current_skills",
    "employee_diagnostic",
    "load_dataset",
]
