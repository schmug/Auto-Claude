"""
Pipeline Module
================

Refactored case creation pipeline with modular components.

Components:
- models: Data structures and utility functions
- agent_runner: Agent execution logic
- orchestrator: Main CaseOrchestrator class
"""

from init import init_auto_sleuth_dir

from .models import get_cases_dir
from .orchestrator import CaseOrchestrator

__all__ = [
    "CaseOrchestrator",
    "get_cases_dir",
    "init_auto_sleuth_dir",
]
