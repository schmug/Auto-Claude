"""
Prerequisites Validator
========================

Validates that required prerequisites exist before case creation.
"""

from pathlib import Path

from ..models import ValidationResult


class PrereqsValidator:
    """Validates prerequisites exist."""

    def __init__(self, case_dir: Path):
        """Initialize the prerequisites validator.

        Args:
            case_dir: Path to the case directory
        """
        self.case_dir = Path(case_dir)

    def validate(self) -> ValidationResult:
        """Validate prerequisites exist.

        Returns:
            ValidationResult with errors, warnings, and suggested fixes
        """
        errors = []
        warnings = []
        fixes = []

        # Check case directory exists
        if not self.case_dir.exists():
            errors.append(f"Case directory does not exist: {self.case_dir}")
            fixes.append(f"Create directory: mkdir -p {self.case_dir}")
            return ValidationResult(False, "prereqs", errors, warnings, fixes)

        # Check project_index.json
        project_index = self.case_dir / "project_index.json"
        if not project_index.exists():
            # Check if it exists at auto-sleuth level
            auto_build_index = self.case_dir.parent.parent / "project_index.json"
            if auto_build_index.exists():
                warnings.append(
                    "project_index.json exists at auto-sleuth/ but not in case folder"
                )
                fixes.append(f"Copy: cp {auto_build_index} {project_index}")
            else:
                errors.append("project_index.json not found")
                fixes.append(
                    "Run: python auto-sleuth/analyzer.py --output auto-sleuth/project_index.json"
                )

        return ValidationResult(
            valid=len(errors) == 0,
            checkpoint="prereqs",
            errors=errors,
            warnings=warnings,
            fixes=fixes,
        )
