"""
Context loading and workflow detection for implementation planner.
"""

import json
import re
from pathlib import Path

from .models import PlannerContext


def _normalize_workflow_type(value: str) -> str:
    """Normalize workflow type strings for consistent mapping.

    Strips whitespace, lowercases the value and removes underscores so variants
    like 'bug_fix' or 'BugFix' map to the same key.
    """
    normalized = (value or "").strip().lower()
    return normalized.replace("_", "")


_WORKFLOW_TYPE_MAPPING: dict[str, str] = {
    "feature": "feature",
    "refactor": "refactor",
    "investigation": "investigation",
    "intrusion": "intrusion",
    "malware": "malware",
    "insiderthreat": "insider_threat",
    "databreach": "data_breach",
    "triage": "triage",
    "incidentresponse": "incident_response",
    "incidentanalysis": "incident_analysis",
    "ransomware": "ransomware",
    "phishing": "phishing",
    "threathunting": "threat_hunting",
    "migration": "migration",
    "simple": "simple",
    "bugfix": "investigation",
}


class ContextLoader:
    """Loads context files and determines workflow type."""

    def __init__(self, case_dir: Path):
        self.case_dir = case_dir

    def load_context(self) -> PlannerContext:
        """Load all context files from case directory."""
        # Read case.md
        case_file = self.case_dir / "case.md"
        case_content = case_file.read_text() if case_file.exists() else ""

        # Read project_index.json
        index_file = self.case_dir / "project_index.json"
        project_index = {}
        if index_file.exists():
            with open(index_file) as f:
                project_index = json.load(f)

        # Read context.json
        context_file = self.case_dir / "context.json"
        task_context = {}
        if context_file.exists():
            with open(context_file) as f:
                task_context = json.load(f)

        # Determine services involved
        services = task_context.get("scoped_services", [])
        if not services:
            services = list(project_index.get("services", {}).keys())

        # Determine investigation type from multiple sources (priority order)
        investigation_type = self._determine_investigation_type(case_content)

        return PlannerContext(
            case_content=case_content,
            project_index=project_index,
            task_context=task_context,
            services_involved=services,
            investigation_type=investigation_type,
            files_to_modify=task_context.get("files_to_modify", []),
            files_to_reference=task_context.get("files_to_reference", []),
        )

    def _determine_investigation_type(self, case_content: str) -> str:
        """Determine investigation type from multiple sources.

        Priority order (highest to lowest):
        1. requirements.json - User's explicit intent
        2. complexity_assessment.json - AI's assessment
        3. case.md explicit declaration - Case writer's declaration
        4. Keyword-based detection - Last resort fallback
        """

        # 1. Check requirements.json (user's explicit intent)
        requirements_file = self.case_dir / "requirements.json"
        if requirements_file.exists():
            try:
                with open(requirements_file) as f:
                    requirements = json.load(f)
                declared_type = _normalize_workflow_type(
                    requirements.get("investigation_type")
                    or requirements.get("workflow_type", "")
                )
                if declared_type in _WORKFLOW_TYPE_MAPPING:
                    return _WORKFLOW_TYPE_MAPPING[declared_type]
            except (json.JSONDecodeError, KeyError):
                pass

        # 2. Check complexity_assessment.json (AI's assessment)
        assessment_file = self.case_dir / "complexity_assessment.json"
        if assessment_file.exists():
            try:
                with open(assessment_file) as f:
                    assessment = json.load(f)
                declared_type = _normalize_workflow_type(
                    assessment.get("investigation_type")
                    or assessment.get("workflow_type", "")
                )
                if declared_type in _WORKFLOW_TYPE_MAPPING:
                    return _WORKFLOW_TYPE_MAPPING[declared_type]
            except (json.JSONDecodeError, KeyError):
                pass

        # 3. & 4. Fall back to case content detection
        return self._detect_investigation_type_from_case(case_content)

    def _detect_investigation_type_from_case(self, case_content: str) -> str:
        """Detect investigation type from case content (fallback method).

        Priority:
        1. Explicit Type: declaration in case.md
        2. Keyword-based detection (last resort)
        """
        content_lower = case_content.lower()

        # Check for explicit workflow type declaration in case
        # Look for patterns like "**Type**: feature" or "Type: refactor"
        explicit_type_patterns = [
            r"\*\*type\*\*:\s*(\w+)",  # **Type**: feature
            r"type:\s*(\w+)",  # Type: feature
            r"workflow\s*type:\s*(\w+)",  # Workflow Type: feature
        ]

        for pattern in explicit_type_patterns:
            match = re.search(pattern, content_lower)
            if match:
                declared_type = _normalize_workflow_type(match.group(1))
                if declared_type in _WORKFLOW_TYPE_MAPPING:
                    return _WORKFLOW_TYPE_MAPPING[declared_type]

        # FALLBACK: Keyword-based detection (only if no explicit type found)
        # Investigation indicators
        investigation_keywords = [
            "bug",
            "fix",
            "issue",
            "broken",
            "not working",
            "investigate",
            "debug",
        ]
        if any(kw in content_lower for kw in investigation_keywords):
            # Check if it's clearly a bug investigation
            if (
                "unknown" in content_lower
                or "intermittent" in content_lower
                or "random" in content_lower
            ):
                    return _WORKFLOW_TYPE_MAPPING["investigation"]

        # Refactor indicators - only match if the INTENT is to refactor, not incidental mentions
        # These should be in headings or task descriptions, not implementation notes
        refactor_keywords = [
            "migrate",
            "refactor",
            "convert",
            "upgrade",
            "replace",
            "move from",
            "transition",
        ]
        # Check if refactor keyword appears in a heading or workflow type context
        for line in case_content.split("\n"):
            line_lower = line.lower().strip()
            # Only trigger on headings or explicit task descriptions
            if line_lower.startswith(("#", "**", "- [ ]", "- [x]")):
                if any(kw in line_lower for kw in refactor_keywords):
                    return _WORKFLOW_TYPE_MAPPING["refactor"]

        # Migration indicators (data)
        migration_keywords = [
            "data migration",
            "migrate data",
            "import",
            "export",
            "batch",
        ]
        if any(kw in content_lower for kw in migration_keywords):
            return _WORKFLOW_TYPE_MAPPING["migration"]

        # Default to feature
        return _WORKFLOW_TYPE_MAPPING["feature"]
