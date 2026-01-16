"""
Case Creation Pipeline Orchestrator
====================================

Main orchestration logic for case creation with dynamic complexity adaptation.

This module has been refactored into smaller components:
- pipeline/models.py: Data structures and utility functions
- pipeline/agent_runner.py: Agent execution logic
- pipeline/orchestrator.py: Main CaseOrchestrator class

For backward compatibility, this module re-exports the main classes and functions.
"""

# Re-export main classes and functions for backward compatibility
from .pipeline import CaseOrchestrator, get_cases_dir

__all__ = [
    "CaseOrchestrator",
    "get_cases_dir",
]
