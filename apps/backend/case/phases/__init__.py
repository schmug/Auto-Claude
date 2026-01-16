"""
Phase Execution Module
=======================

Individual phase implementations for case creation pipeline.

This module is organized into several submodules for better maintainability:
- models: PhaseResult dataclass and constants
- discovery_phases: Project discovery and context gathering
- requirements_phases: Requirements, historical context, and research
- case_phases: Case writing and self-critique
- planning_phases: Investigation planning and validation
- utils: Helper utilities for phase execution
"""

from .executor import PhaseExecutor
from .models import MAX_RETRIES, PhaseResult

__all__ = ["PhaseExecutor", "PhaseResult", "MAX_RETRIES"]
