#!/usr/bin/env python3
"""
Memory Directory Management
============================

Functions for managing memory directory structure.
"""

from pathlib import Path


def get_memory_dir(case_dir: Path) -> Path:
    """
    Get the memory directory for a case, creating it if needed.

    Args:
        case_dir: Path to case directory (e.g., .auto-sleuth/cases/001-case-name/)

    Returns:
        Path to memory directory
    """
    memory_dir = case_dir / "memory"
    memory_dir.mkdir(exist_ok=True)
    return memory_dir


def get_session_insights_dir(case_dir: Path) -> Path:
    """
    Get the session insights directory, creating it if needed.

    Args:
        case_dir: Path to case directory

    Returns:
        Path to session_insights directory
    """
    insights_dir = get_memory_dir(case_dir) / "session_insights"
    insights_dir.mkdir(parents=True, exist_ok=True)
    return insights_dir


def clear_memory(case_dir: Path) -> None:
    """
    Clear all memory for a case.

    WARNING: This deletes all session insights, codebase map, patterns, and gotchas.
    Use with caution - typically only needed when starting completely fresh.

    Args:
        case_dir: Path to case directory
    """
    memory_dir = get_memory_dir(case_dir)

    if memory_dir.exists():
        import shutil

        shutil.rmtree(memory_dir)
