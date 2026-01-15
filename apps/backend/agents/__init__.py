"""
Agents Module
=============

Modular agent system for autonomous DFIR investigations and coding.

This module provides:
- run_autonomous_agent: Main coder agent loop (legacy)
- run_autonomous_analyst: Main evidence analyst loop (DFIR)
- run_followup_planner: Follow-up planner for completed specs
- run_followup_case_planner: Follow-up planner for completed cases (DFIR)
- run_evidence_validator: Evidence validation agent (DFIR)
- Memory management (Graphiti + file-based fallback)
- Session management and post-processing
- Utility functions for git and plan management

Uses lazy imports to avoid circular dependencies.
"""

# Explicit import required by CodeQL static analysis
# (CodeQL doesn't recognize __getattr__ dynamic exports)
from .utils import sync_spec_to_source, sync_case_to_source

__all__ = [
    # Main API - Legacy (Coding)
    "run_autonomous_agent",
    "run_followup_planner",
    # Main API - DFIR
    "run_autonomous_analyst",
    "run_followup_case_planner",
    "run_initial_case_planning",
    "run_evidence_validator",
    "run_validation_loop",
    "verify_evidence_integrity",
    "verify_chain_of_custody",
    # Memory
    "debug_memory_system_status",
    "get_graphiti_context",
    "save_session_memory",
    "save_session_to_graphiti",
    # Session
    "run_agent_session",
    "post_session_processing",
    # Utils
    "get_latest_commit",
    "get_commit_count",
    "load_implementation_plan",
    "load_investigation_plan",
    "find_subtask_in_plan",
    "find_phase_for_subtask",
    "find_step_in_plan",
    "find_phase_for_step",
    "sync_spec_to_source",
    "sync_case_to_source",
    # Constants
    "AUTO_CONTINUE_DELAY_SECONDS",
    "HUMAN_INTERVENTION_FILE",
]


def __getattr__(name):
    """Lazy imports to avoid circular dependencies."""
    if name in ("AUTO_CONTINUE_DELAY_SECONDS", "HUMAN_INTERVENTION_FILE"):
        from .base import AUTO_CONTINUE_DELAY_SECONDS, HUMAN_INTERVENTION_FILE

        return locals()[name]
    elif name == "run_autonomous_agent":
        from .coder import run_autonomous_agent

        return run_autonomous_agent
    elif name == "run_autonomous_analyst":
        from .evidence_analyst import run_autonomous_analyst

        return run_autonomous_analyst
    elif name in ("run_followup_case_planner", "run_initial_case_planning"):
        from .case_planner import run_followup_case_planner, run_initial_case_planning

        return locals()[name]
    elif name in ("run_evidence_validator", "run_validation_loop", "verify_evidence_integrity", "verify_chain_of_custody"):
        from .evidence_validator import (
            run_evidence_validator,
            run_validation_loop,
            verify_evidence_integrity,
            verify_chain_of_custody,
        )

        return locals()[name]
    elif name in (
        "debug_memory_system_status",
        "get_graphiti_context",
        "save_session_memory",
        "save_session_to_graphiti",
    ):
        from .memory_manager import (
            debug_memory_system_status,
            get_graphiti_context,
            save_session_memory,
            save_session_to_graphiti,
        )

        return locals()[name]
    elif name == "run_followup_planner":
        from .planner import run_followup_planner

        return run_followup_planner
    elif name in ("post_session_processing", "run_agent_session"):
        from .session import post_session_processing, run_agent_session

        return locals()[name]
    elif name in (
        "find_phase_for_subtask",
        "find_subtask_in_plan",
        "find_phase_for_step",
        "find_step_in_plan",
        "get_commit_count",
        "get_latest_commit",
        "load_implementation_plan",
        "load_investigation_plan",
        "sync_spec_to_source",
        "sync_case_to_source",
    ):
        from .utils import (
            find_phase_for_subtask,
            find_subtask_in_plan,
            find_phase_for_step,
            find_step_in_plan,
            get_commit_count,
            get_latest_commit,
            load_implementation_plan,
            load_investigation_plan,
            sync_spec_to_source,
            sync_case_to_source,
        )

        return locals()[name]
    raise AttributeError(f"module 'agents' has no attribute '{name}'")
