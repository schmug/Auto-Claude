"""
Data models for the implementation planner.
"""

from dataclasses import dataclass

@dataclass
class PlannerContext:
    """Context gathered for planning."""

    case_content: str
    project_index: dict
    task_context: dict
    evidence_sources: list[str]
    investigation_type: str
    files_to_modify: list[dict]
    files_to_reference: list[dict]
