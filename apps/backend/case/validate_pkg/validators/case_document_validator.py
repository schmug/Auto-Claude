"""
Case Document Validator
========================

Validates case.md document structure and required sections.
"""

import re
from pathlib import Path

from ..models import ValidationResult
from ..schemas import SPEC_RECOMMENDED_SECTIONS, SPEC_REQUIRED_SECTIONS


class CaseDocumentValidator:
    """Validates case.md exists and has required sections."""

    def __init__(self, case_dir: Path):
        """Initialize the case document validator.

        Args:
            case_dir: Path to the case directory
        """
        self.case_dir = Path(case_dir)

    def validate(self) -> ValidationResult:
        """Validate case.md or spec.md exists and has required sections.

        Returns:
            ValidationResult with errors, warnings, and suggested fixes
        """
        errors = []
        warnings = []
        fixes = []

        case_file = self.case_dir / "case.md"
        spec_file = self.case_dir / "spec.md"  # Legacy alternative

        # Check for either case.md or spec.md (DFIR workflows use case.md)
        if case_file.exists():
            doc_file = case_file
        elif spec_file.exists():
            doc_file = spec_file
        else:
            errors.append("case.md or spec.md not found")
            fixes.append("Create case.md (DFIR) or spec.md (legacy) with required sections")
            return ValidationResult(False, "case", errors, warnings, fixes)

        content = doc_file.read_text()

        # Section alternatives: (required_section, [alternatives])
        # DFIR workflows use different section names than coding workflows
        section_alternatives = {
            "Investigation Type": ["Workflow Type"],  # Legacy alternative
            "Incident Scope": ["Task Scope"],  # Legacy alternative
            "Evidence Sources": ["Services Involved"],  # Legacy alternative
            "Initial IOCs": ["IOCs"],  # Legacy alternative
        }

        # Check for required sections (with alternatives for DFIR)
        for section in SPEC_REQUIRED_SECTIONS:
            # Build pattern to match section OR any alternatives
            alternatives = section_alternatives.get(section, [])
            all_options = [section] + alternatives
            
            found = False
            for option in all_options:
                # Look for ## Section or # Section
                pattern = rf"^##?\s+{re.escape(option)}"
                if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                    found = True
                    break
            
            if not found:
                if alternatives:
                    errors.append(f"Missing required section: '{section}' (or '{alternatives[0]}')")
                    fixes.append(f"Add '## {section}' or '## {alternatives[0]}' section")
                else:
                    errors.append(f"Missing required section: '{section}'")
                    fixes.append(f"Add '## {section}' section")

        # Check for recommended sections
        for section in SPEC_RECOMMENDED_SECTIONS:
            pattern = rf"^##?\s+{re.escape(section)}"
            if not re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                warnings.append(f"Missing recommended section: '{section}'")

        # Check minimum content length
        if len(content) < 500:
            warnings.append("case.md seems too short (< 500 chars)")

        return ValidationResult(
            valid=len(errors) == 0,
            checkpoint="case",
            errors=errors,
            warnings=warnings,
            fixes=fixes,
        )
