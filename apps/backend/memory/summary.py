#!/usr/bin/env python3
"""
Memory Summary Utilities
========================

Functions for getting summaries of memory data.
"""

from pathlib import Path
from typing import Any

from .codebase_map import load_codebase_map
from .patterns import load_gotchas, load_patterns
from .sessions import load_all_insights


def get_memory_summary(case_dir: Path) -> dict[str, Any]:
    """
    Get a summary of all memory data for a case.

    Useful for understanding what the system has learned so far.

    Args:
        case_dir: Path to case directory

    Returns:
        Dictionary with memory summary:
            - total_sessions: int
            - total_files_mapped: int
            - total_patterns: int
            - total_gotchas: int
            - recent_insights: list[dict] (last 3 sessions)
    """
    insights = load_all_insights(case_dir)
    codebase_map = load_codebase_map(case_dir)
    patterns = load_patterns(case_dir)
    gotchas = load_gotchas(case_dir)

    return {
        "total_sessions": len(insights),
        "total_files_mapped": len(codebase_map),
        "total_patterns": len(patterns),
        "total_gotchas": len(gotchas),
        "recent_insights": insights[-3:] if len(insights) > 3 else insights,
    }
