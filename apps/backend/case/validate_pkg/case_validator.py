"""
Case Validator
==============

Main validator class that orchestrates all validation checkpoints.
"""

from pathlib import Path

from .models import ValidationResult
from .validators import (
    ContextValidator,
    InvestigationPlanValidator,
    PrereqsValidator,
    CaseDocumentValidator,
)


class CaseValidator:
    """Validates case outputs at each checkpoint."""

    def __init__(self, case_dir: Path):
        """Initialize the case validator.

        Args:
            case_dir: Path to the case directory
        """
        self.case_dir = Path(case_dir)

        # Initialize individual validators
        self._prereqs_validator = PrereqsValidator(self.case_dir)
        self._context_validator = ContextValidator(self.case_dir)
        self._case_document_validator = CaseDocumentValidator(self.case_dir)
        self._investigation_plan_validator = InvestigationPlanValidator(self.case_dir)

    def validate_all(self) -> list[ValidationResult]:
        """Run all validations.

        Returns:
            List of validation results for all checkpoints
        """
        results = [
            self.validate_prereqs(),
            self.validate_context(),
            self.validate_case_document(),
            self.validate_investigation_plan(),
        ]
        return results

    def validate_prereqs(self) -> ValidationResult:
        """Validate prerequisites exist.

        Returns:
            ValidationResult for prerequisites checkpoint
        """
        return self._prereqs_validator.validate()

    def validate_context(self) -> ValidationResult:
        """Validate context.json exists and has required structure.

        Returns:
            ValidationResult for context checkpoint
        """
        return self._context_validator.validate()

    def validate_case_document(self) -> ValidationResult:
        """Validate case.md exists and has required sections.

        Returns:
            ValidationResult for case document checkpoint
        """
        return self._case_document_validator.validate()

    def validate_investigation_plan(self) -> ValidationResult:
        """Validate investigation_plan.json exists and has valid schema.

        Returns:
            ValidationResult for implementation plan checkpoint
        """
        return self._investigation_plan_validator.validate()
