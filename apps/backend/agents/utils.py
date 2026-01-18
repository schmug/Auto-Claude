"""
Utility Functions for Agent System - Auto-Sleuth DFIR
======================================================

Helper functions for git operations, investigation plan management, and file syncing.
"""

import json
import logging
import shutil
from pathlib import Path

from core.git_executable import run_git

logger = logging.getLogger(__name__)


def get_latest_commit(project_dir: Path) -> str | None:
    """Get the hash of the latest git commit."""
    result = run_git(
        ["rev-parse", "HEAD"],
        cwd=project_dir,
        timeout=10,
    )
    if result.returncode == 0:
        return result.stdout.strip()
    return None


def get_commit_count(project_dir: Path) -> int:
    """Get the total number of commits."""
    result = run_git(
        ["rev-list", "--count", "HEAD"],
        cwd=project_dir,
        timeout=10,
    )
    if result.returncode == 0:
        try:
            return int(result.stdout.strip())
        except ValueError:
            return 0
    return 0


def load_investigation_plan(case_dir: Path) -> dict | None:
    """Load the investigation plan JSON."""
    plan_file = case_dir / "investigation_plan.json"
    if not plan_file.exists():
        return None
    try:
        with open(plan_file) as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def _get_phase_tasks(phase: dict) -> list[dict]:
    """Return the list of tasks for a phase."""
    tasks = phase.get("analysis_tasks")
    return tasks if isinstance(tasks, list) else []


def find_subtask_in_plan(plan: dict, subtask_id: str) -> dict | None:
    """Find a subtask by ID in the plan."""
    for phase in plan.get("phases", []):
        for subtask in _get_phase_tasks(phase):
            if subtask.get("id") == subtask_id:
                return subtask
    return None


def find_phase_for_subtask(plan: dict, subtask_id: str) -> dict | None:
    """Find the phase containing a subtask."""
    for phase in plan.get("phases", []):
        for subtask in _get_phase_tasks(phase):
            if subtask.get("id") == subtask_id:
                return phase
    return None


def find_step_in_plan(plan: dict, step_id: str) -> dict | None:
    """Find an investigation step by ID in the plan."""
    for phase in plan.get("phases", []):
        for step in _get_phase_tasks(phase):
            if step.get("id") == step_id:
                return step
    return None


def find_phase_for_step(plan: dict, step_id: str) -> dict | None:
    """Find the phase containing a step."""
    for phase in plan.get("phases", []):
        for step in _get_phase_tasks(phase):
            if step.get("id") == step_id:
                return phase
    return None


# DFIR aliases

def find_analysis_task_in_plan(plan: dict, task_id: str) -> dict | None:
    """Alias for find_subtask_in_plan for DFIR context."""
    return find_subtask_in_plan(plan, task_id)


def find_phase_for_analysis_task(plan: dict, task_id: str) -> dict | None:
    """Alias for find_phase_for_subtask for DFIR context."""
    return find_phase_for_subtask(plan, task_id)


def sync_case_to_source(case_dir: Path, source_case_dir: Path | None) -> bool:
    """
    Sync ALL case files from worktree back to source case directory.

    When running in isolated mode (worktrees), the agent creates and updates
    many files inside the worktree's case directory. This function syncs ALL
    of them back to the main project's case directory.

    IMPORTANT: Since .auto-sleuth/ is gitignored, this sync happens to the
    local filesystem regardless of what branch the user is on. The worktree
    may be on a different branch (e.g., auto-sleuth/093-task), but the sync
    target is always the main project's .auto-sleuth/cases/ directory.

    Files synced (all files in case directory):
    - investigation_plan.json - Task status and subtask completion
    - build-progress.txt - Session-by-session progress notes
    - task_logs.json - Execution logs
    - review_state.json - QA review state
    - critique_report.json - Case critique findings
    - suggested_commit_message.txt - Commit suggestions
    - REGRESSION_TEST_REPORT.md - Test regression report
    - case.md, context.json, etc. - Original case files (for completeness)
    - memory/ directory - Codebase map, patterns, gotchas, session insights

    Args:
        case_dir: Current case directory (inside worktree)
        source_case_dir: Original case directory in main project (outside worktree)

    Returns:
        True if sync was performed, False if not needed or failed
    """
    # Skip if no source caseified or same path (not in worktree mode)
    if not source_case_dir:
        return False

    # Resolve paths and check if they're different
    case_dir_resolved = case_dir.resolve()
    source_case_dir_resolved = source_case_dir.resolve()

    if case_dir_resolved == source_case_dir_resolved:
        return False  # Same directory, no sync needed

    synced_any = False

    # Ensure source directory exists
    source_case_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Sync all files and directories from worktree case to source case
        for item in case_dir.iterdir():
            # Skip symlinks to prevent path traversal attacks
            if item.is_symlink():
                logger.warning(f"Skipping symlink during sync: {item.name}")
                continue

            source_item = source_case_dir / item.name

            if item.is_file():
                # Copy file (preserves timestamps)
                shutil.copy2(item, source_item)
                logger.debug(f"Synced {item.name} to source")
                synced_any = True

            elif item.is_dir():
                # Recursively sync directory
                _sync_directory(item, source_item)
                synced_any = True

    except Exception as e:
        logger.warning(f"Failed to sync case directory to source: {e}")

    return synced_any


def _sync_directory(source_dir: Path, target_dir: Path) -> None:
    """
    Recursively sync a directory from source to target.

    Args:
        source_dir: Source directory (in worktree)
        target_dir: Target directory (in main project)
    """
    # Create target directory if needed
    target_dir.mkdir(parents=True, exist_ok=True)

    for item in source_dir.iterdir():
        # Skip symlinks to prevent path traversal attacks
        if item.is_symlink():
            logger.warning(
                f"Skipping symlink during sync: {source_dir.name}/{item.name}"
            )
            continue

        target_item = target_dir / item.name

        if item.is_file():
            shutil.copy2(item, target_item)
            logger.debug(f"Synced {source_dir.name}/{item.name} to source")
        elif item.is_dir():
            # Recurse into subdirectories
            _sync_directory(item, target_item)


# Keep the old name as an alias for backward compatibility

def sync_plan_to_source(case_dir: Path, source_case_dir: Path | None) -> bool:
    """Alias for sync_case_to_source for backward compatibility."""
    return sync_case_to_source(case_dir, source_case_dir)
