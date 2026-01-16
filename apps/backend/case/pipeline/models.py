"""
Pipeline Models and Utilities
==============================

Data structures, helper functions, and utilities for the case creation pipeline.
"""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING

from init import init_auto_sleuth_dir
from task_logger import update_task_logger_path
from ui import Icons, highlight, print_status

if TYPE_CHECKING:
    from core.workspace.models import CaseNumberLock


def get_cases_dir(project_dir: Path) -> Path:
    """Get the cases directory path.

    IMPORTANT: Only .auto-sleuth/ is considered an "installed" auto-sleuth.
    The auto-sleuth/ folder (if it exists) is SOURCE CODE being developed,
    not an installation. This allows Auto Sleuth to be used to develop itself.

    This function also ensures .auto-sleuth is added to .gitignore on first use.

    Args:
        project_dir: The project root directory

    Returns:
        Path to the cases directory within .auto-sleuth/
    """
    # Initialize .auto-sleuth directory and ensure it's in .gitignore
    init_auto_sleuth_dir(project_dir)

    # Return the cases directory path
    return project_dir / ".auto-sleuth" / "cases"


def cleanup_orphaned_pending_folders(cases_dir: Path) -> None:
    """Remove orphaned pending folders that have no substantial content.

    Args:
        cases_dir: The cases directory to clean up
    """
    if not cases_dir.exists():
        return

    orphaned = []
    for folder in cases_dir.glob("[0-9][0-9][0-9]-pending"):
        if not folder.is_dir():
            continue

        # Check if folder has substantial content
        requirements_file = folder / "requirements.json"
        case_file = folder / "case.md"
        plan_file = folder / "investigation_plan.json"

        if requirements_file.exists() or case_file.exists() or plan_file.exists():
            continue

        # Check folder age - only clean up folders older than 10 minutes
        try:
            folder_mtime = datetime.fromtimestamp(folder.stat().st_mtime)
            if datetime.now() - folder_mtime < timedelta(minutes=10):
                continue
        except OSError:
            continue

        orphaned.append(folder)

    # Clean up orphaned folders
    for folder in orphaned:
        try:
            shutil.rmtree(folder)
        except OSError:
            pass


def create_case_dir(cases_dir: Path, lock: CaseNumberLock | None = None) -> Path:
    """Create a new case directory with incremented number and placeholder name.

    Args:
        cases_dir: The parent cases directory
        lock: Optional CaseNumberLock for coordinated numbering across worktrees.
              If provided, uses global scan to prevent case number collisions.
              If None, uses local scan only (legacy behavior for single process).

    Returns:
        Path to the new case directory
    """
    if lock is not None:
        # Use global coordination via lock - scans main project + all worktrees
        next_num = lock.get_next_case_number()
    else:
        # Legacy local scan (fallback for cases without lock)
        existing = list(cases_dir.glob("[0-9][0-9][0-9]-*"))

        if existing:
            # Find the HIGHEST folder number
            numbers = []
            for folder in existing:
                try:
                    num = int(folder.name[:3])
                    numbers.append(num)
                except ValueError:
                    pass
            next_num = max(numbers) + 1 if numbers else 1
        else:
            next_num = 1

    # Start with placeholder - will be renamed after requirements gathering
    name = "pending"
    return cases_dir / f"{next_num:03d}-{name}"


def generate_case_name(task_description: str) -> str:
    """Generate a clean kebab-case name from task description.

    Args:
        task_description: The task description to convert

    Returns:
        A kebab-case name suitable for a directory
    """
    skip_words = {
        "a",
        "an",
        "the",
        "to",
        "for",
        "of",
        "in",
        "on",
        "at",
        "by",
        "with",
        "and",
        "or",
        "but",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "will",
        "would",
        "could",
        "should",
        "may",
        "might",
        "must",
        "can",
        "this",
        "that",
        "these",
        "those",
        "i",
        "you",
        "we",
        "they",
        "it",
        "add",
        "create",
        "make",
        "implement",
        "build",
        "new",
        "using",
        "use",
        "via",
        "from",
    }

    # Clean and tokenize
    text = task_description.lower()
    text = "".join(c if c.isalnum() or c == " " else " " for c in text)
    words = text.split()

    # Filter out skip words and short words
    meaningful = [w for w in words if w not in skip_words and len(w) > 2]

    # Take first 4 meaningful words
    name_parts = meaningful[:4]

    if not name_parts:
        name_parts = words[:4]

    return "-".join(name_parts) if name_parts else "case"


def rename_case_dir_from_requirements(case_dir: Path) -> bool:
    """Rename case directory based on requirements.json task description.

    Args:
        case_dir: The current case directory

    Returns:
        Tuple of (success, new_case_dir). If success is False, new_case_dir is the original.
    """
    requirements_file = case_dir / "requirements.json"

    if not requirements_file.exists():
        return False

    try:
        with open(requirements_file) as f:
            req = json.load(f)

        task_desc = req.get("task_description", "")
        if not task_desc:
            return False

        # Generate new name
        new_name = generate_case_name(task_desc)

        # Extract the number prefix from current dir
        current_name = case_dir.name
        if current_name[:3].isdigit():
            prefix = current_name[:4]  # "001-"
        else:
            prefix = ""

        new_dir_name = f"{prefix}{new_name}"
        new_case_dir = case_dir.parent / new_dir_name

        # Don't rename if it's already a good name (not "pending")
        if "pending" not in current_name:
            return True

        # Don't rename if target already exists
        if new_case_dir.exists():
            return True

        # Rename the directory
        shutil.move(str(case_dir), str(new_case_dir))

        # Update the global task logger to use the new path
        update_task_logger_path(new_case_dir)

        print_status(f"Case folder: {highlight(new_dir_name)}", "success")
        return True

    except (json.JSONDecodeError, OSError) as e:
        print_status(f"Could not rename case folder: {e}", "warning")
        return False


# Phase display configuration
PHASE_DISPLAY: dict[str, tuple[str, str]] = {
    "discovery": ("CASE DISCOVERY", Icons.FOLDER),
    "historical_context": ("HISTORICAL CONTEXT", Icons.SEARCH),
    "requirements": ("CASE REQUIREMENTS", Icons.FILE),
    "complexity_assessment": ("COMPLEXITY ASSESSMENT", Icons.GEAR),
    "research": ("INVESTIGATION RESEARCH", Icons.SEARCH),
    "context": ("CONTEXT DISCOVERY", Icons.FOLDER),
    "quick_case": ("QUICK CASE", Icons.LIGHTNING),
    "case_writing": ("CASE DOCUMENT CREATION", Icons.FILE),
    "self_critique": ("CASE SELF-CRITIQUE", Icons.GEAR),
    "evidence_preprocessing": ("EVIDENCE PREPROCESSING", Icons.SEARCH),  # DFIR phase
    "planning": ("INVESTIGATION PLANNING", Icons.SUBTASK),
    "validation": ("FINAL VALIDATION", Icons.SUCCESS),
}
