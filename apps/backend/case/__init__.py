"""
Case Creation Module
====================

Modular case creation pipeline with complexity-based phase selection.

Main Components:
- complexity: Task complexity assessment (AI and heuristic)
- requirements: Interactive and automated requirements gathering
- discovery: Project structure analysis
- context: Relevant file discovery
- writer: Case document and plan creation
- validator: Validation helpers
- phases: Individual phase implementations
- pipeline: Main orchestration logic

Usage:
    from case import CaseOrchestrator

    orchestrator = CaseOrchestrator(
        project_dir=Path.cwd(),
        task_description="Add user authentication",
    )

    success = await orchestrator.run()
"""

from .complexity import (
    Complexity,
    ComplexityAnalyzer,
    ComplexityAssessment,
    run_ai_complexity_assessment,
    save_assessment,
)
from .phases import PhaseExecutor, PhaseResult
from .pipeline import CaseOrchestrator, get_cases_dir

__all__ = [
    # Main orchestrator
    "CaseOrchestrator",
    "get_cases_dir",
    # Complexity assessment
    "Complexity",
    "ComplexityAnalyzer",
    "ComplexityAssessment",
    "run_ai_complexity_assessment",
    "save_assessment",
    # Phase execution
    "PhaseExecutor",
    "PhaseResult",
]
