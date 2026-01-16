"""
Case Validation System
======================

Validates case outputs at each checkpoint to ensure reliability.
This is the enforcement layer that catches errors before they propagate.

The case creation process has mandatory checkpoints:
1. Prerequisites (project_index.json exists)
2. Context (context.json created with required fields)
3. Case document (case.md with required sections)
4. Investigation plan (investigation_plan.json with valid schema)
"""

from .auto_fix import auto_fix_plan
from .models import ValidationResult
from .case_validator import CaseValidator

__all__ = ["CaseValidator", "ValidationResult", "auto_fix_plan"]
