"""
Progress Tracking Utilities
===========================

Functions for tracking and displaying progress of the autonomous coding agent.
Uses task-based investigation plans (investigation_plan.json).

Enhanced with colored output, icons, and better visual formatting.
"""

import json
from pathlib import Path

from ui import (
    Icons,
    bold,
    box,
    highlight,
    icon,
    muted,
    print_phase_status,
    print_status,
    progress_bar,
    success,
    warning,
)


def _get_phase_tasks(phase: dict) -> list[dict]:
    """Return the list of tasks for a phase."""
    tasks = phase.get("analysis_tasks")
    if isinstance(tasks, list):
        return tasks
    tasks = phase.get("subtasks") or phase.get("chunks") or []
    return tasks if isinstance(tasks, list) else []


def count_subtasks(case_dir: Path) -> tuple[int, int]:
    """
    Count completed and total tasks in investigation_plan.json.

    Args:
        case_dir: Directory containing investigation_plan.json

    Returns:
        (completed_count, total_count)
    """
    plan_file = case_dir / "investigation_plan.json"

    if not plan_file.exists():
        return 0, 0

    try:
        with open(plan_file) as f:
            plan = json.load(f)

        total = 0
        completed = 0

        for phase in plan.get("phases", []):
            for subtask in _get_phase_tasks(phase):
                total += 1
                if subtask.get("status") == "completed":
                    completed += 1

        return completed, total
    except (OSError, json.JSONDecodeError):
        return 0, 0


def count_subtasks_detailed(case_dir: Path) -> dict:
    """
    Count tasks by status.

    Returns:
        Dict with completed, in_progress, pending, failed counts
    """
    plan_file = case_dir / "investigation_plan.json"

    result = {
        "completed": 0,
        "in_progress": 0,
        "pending": 0,
        "failed": 0,
        "total": 0,
    }

    if not plan_file.exists():
        return result

    try:
        with open(plan_file) as f:
            plan = json.load(f)

        for phase in plan.get("phases", []):
            for subtask in _get_phase_tasks(phase):
                result["total"] += 1
                status = subtask.get("status", "pending")
                if status in result:
                    result[status] += 1
                else:
                    result["pending"] += 1

        return result
    except (OSError, json.JSONDecodeError):
        return result


def is_build_complete(case_dir: Path) -> bool:
    """
    Check if all tasks are completed.

    Args:
        case_dir: Directory containing investigation_plan.json

    Returns:
        True if all subtasks complete, False otherwise
    """
    completed, total = count_subtasks(case_dir)
    return total > 0 and completed == total


def get_progress_percentage(case_dir: Path) -> float:
    """
    Get the progress as a percentage.

    Args:
        case_dir: Directory containing investigation_plan.json

    Returns:
    Percentage of tasks completed (0-100)
    """
    completed, total = count_subtasks(case_dir)
    if total == 0:
        return 0.0
    return (completed / total) * 100


def print_session_header(
    session_num: int,
    is_planner: bool,
    subtask_id: str = None,
    subtask_desc: str = None,
    phase_name: str = None,
    attempt: int = 1,
) -> None:
    """Print a formatted header for the session."""
    session_type = "PLANNER AGENT" if is_planner else "CODING AGENT"
    session_icon = Icons.GEAR if is_planner else Icons.LIGHTNING

    content = [
        bold(f"{icon(session_icon)} SESSION {session_num}: {session_type}"),
    ]

    if subtask_id:
        content.append("")
        subtask_line = f"{icon(Icons.SUBTASK)} Subtask: {highlight(subtask_id)}"
        if subtask_desc:
            # Truncate long descriptions
            desc = subtask_desc[:50] + "..." if len(subtask_desc) > 50 else subtask_desc
            subtask_line += f" - {desc}"
        content.append(subtask_line)

    if phase_name:
        content.append(f"{icon(Icons.PHASE)} Phase: {phase_name}")

    if attempt > 1:
        content.append(warning(f"{icon(Icons.WARNING)} Attempt: {attempt}"))

    print()
    print(box(content, width=70, style="heavy"))
    print()


def print_progress_summary(case_dir: Path, show_next: bool = True) -> None:
    """Print a summary of current progress with enhanced formatting."""
    completed, total = count_subtasks(case_dir)

    if total > 0:
        print()
        # Progress bar
        print(f"Progress: {progress_bar(completed, total, width=40)}")

        # Status message
        if completed == total:
            print_status("BUILD COMPLETE - All tasks completed!", "success")
        else:
            remaining = total - completed
            print_status(f"{remaining} tasks remaining", "info")

        # Phase summary
        try:
            with open(case_dir / "investigation_plan.json") as f:
                plan = json.load(f)

            print("\nPhases:")
            for phase in plan.get("phases", []):
                phase_tasks = _get_phase_tasks(phase)
                phase_completed = sum(
                    1 for s in phase_tasks if s.get("status") == "completed"
                )
                phase_total = len(phase_tasks)
                phase_name = phase.get("name", phase.get("id", "Unknown"))

                if phase_completed == phase_total:
                    status = "complete"
                elif phase_completed > 0 or any(
                    s.get("status") == "in_progress" for s in phase_tasks
                ):
                    status = "in_progress"
                else:
                    # Check if blocked by dependencies
                    deps = phase.get("depends_on", [])
                    all_deps_complete = True
                    for dep_id in deps:
                        for p in plan.get("phases", []):
                            if p.get("id") == dep_id or p.get("phase") == dep_id:
                                p_tasks = _get_phase_tasks(p)
                                if not all(
                                    s.get("status") == "completed" for s in p_tasks
                                ):
                                    all_deps_complete = False
                                break
                    status = "pending" if all_deps_complete else "blocked"

                print_phase_status(phase_name, phase_completed, phase_total, status)

            # Show next subtask if requested
            if show_next and completed < total:
                next_subtask = get_next_subtask(case_dir)
                if next_subtask:
                    print()
                    next_id = next_subtask.get("id", "unknown")
                    next_desc = next_subtask.get("description", "")
                    if len(next_desc) > 60:
                        next_desc = next_desc[:57] + "..."
                    print(
                        f"  {icon(Icons.ARROW_RIGHT)} Next: {highlight(next_id)} - {next_desc}"
                    )

        except (OSError, json.JSONDecodeError):
            pass
    else:
        print()
        print_status("No investigation tasks yet - planner needs to run", "pending")


def print_build_complete_banner(case_dir: Path) -> None:
    """Print a completion banner."""
    content = [
        success(f"{icon(Icons.SUCCESS)} BUILD COMPLETE!"),
        "",
        "All tasks have been implemented successfully.",
        "",
        muted("Next steps:"),
        f"  1. Review the {highlight('auto-sleuth/*')} branch",
        "  2. Run manual tests",
        "  3. Create a PR and merge to main",
    ]

    print()
    print(box(content, width=70, style="heavy"))
    print()


def print_paused_banner(
    case_dir: Path,
    case_name: str,
    has_worktree: bool = False,
) -> None:
    """Print a paused banner with resume instructions."""
    completed, total = count_subtasks(case_dir)

    content = [
        warning(f"{icon(Icons.PAUSE)} BUILD PAUSED"),
        "",
        f"Progress saved: {completed}/{total} tasks complete",
    ]

    if has_worktree:
        content.append("")
        content.append(muted("Your build is in a separate workspace and is safe."))

    print()
    print(box(content, width=70, style="heavy"))


def get_plan_summary(case_dir: Path) -> dict:
    """
    Get a detailed summary of implementation plan status.

    Args:
        case_dir: Directory containing investigation_plan.json

    Returns:
        Dictionary with plan statistics
    """
    plan_file = case_dir / "investigation_plan.json"

    if not plan_file.exists():
        return {
            "investigation_type": None,
            "total_phases": 0,
            "total_tasks": 0,
            "completed_tasks": 0,
            "pending_tasks": 0,
            "in_progress_tasks": 0,
            "failed_tasks": 0,
            "total_subtasks": 0,
            "completed_subtasks": 0,
            "pending_subtasks": 0,
            "in_progress_subtasks": 0,
            "failed_subtasks": 0,
            "phases": [],
        }

    try:
        with open(plan_file) as f:
            plan = json.load(f)

        summary = {
            "investigation_type": plan.get("investigation_type") or plan.get("workflow_type") or "triage",
            "total_phases": len(plan.get("phases", [])),
            "total_tasks": 0,
            "completed_tasks": 0,
            "pending_tasks": 0,
            "in_progress_tasks": 0,
            "failed_tasks": 0,
            "total_subtasks": 0,
            "completed_subtasks": 0,
            "pending_subtasks": 0,
            "in_progress_subtasks": 0,
            "failed_subtasks": 0,
            "phases": [],
        }

        for phase in plan.get("phases", []):
            phase_info = {
                "id": phase.get("id"),
                "phase": phase.get("phase"),
                "name": phase.get("name"),
                "depends_on": phase.get("depends_on", []),
                "tasks": [],
                "completed": 0,
                "total": 0,
            }

            for subtask in _get_phase_tasks(phase):
                status = subtask.get("status", "pending")
                summary["total_tasks"] += 1
                summary["total_subtasks"] += 1
                phase_info["total"] += 1

                if status == "completed":
                    summary["completed_tasks"] += 1
                    summary["completed_subtasks"] += 1
                    phase_info["completed"] += 1
                elif status == "in_progress":
                    summary["in_progress_tasks"] += 1
                    summary["in_progress_subtasks"] += 1
                elif status == "failed":
                    summary["failed_tasks"] += 1
                    summary["failed_subtasks"] += 1
                else:
                    summary["pending_tasks"] += 1
                    summary["pending_subtasks"] += 1

                phase_info["tasks"].append(
                    {
                        "id": subtask.get("id"),
                        "description": subtask.get("description"),
                        "status": status,
                        "service": subtask.get("evidence_source") or subtask.get("service"),
                    }
                )

            summary["phases"].append(phase_info)

        return summary

    except (OSError, json.JSONDecodeError):
        return {
            "investigation_type": None,
            "total_phases": 0,
            "total_tasks": 0,
            "completed_tasks": 0,
            "pending_tasks": 0,
            "in_progress_tasks": 0,
            "failed_tasks": 0,
            "total_subtasks": 0,
            "completed_subtasks": 0,
            "pending_subtasks": 0,
            "in_progress_subtasks": 0,
            "failed_subtasks": 0,
            "phases": [],
        }


def get_current_phase(case_dir: Path) -> dict | None:
    """Get the current phase being worked on."""
    plan_file = case_dir / "investigation_plan.json"

    if not plan_file.exists():
        return None

    try:
        with open(plan_file) as f:
            plan = json.load(f)

        for phase in plan.get("phases", []):
            subtasks = _get_phase_tasks(phase)
            # Phase is current if it has incomplete subtasks and dependencies are met
            has_incomplete = any(s.get("status") != "completed" for s in subtasks)
            if has_incomplete:
                return {
                    "id": phase.get("id"),
                    "phase": phase.get("phase"),
                    "name": phase.get("name"),
                    "completed": sum(
                        1 for s in subtasks if s.get("status") == "completed"
                    ),
                    "total": len(subtasks),
                }

        return None

    except (OSError, json.JSONDecodeError):
        return None


def get_next_subtask(case_dir: Path) -> dict | None:
    """
    Find the next task to work on, recaseting phase dependencies.

    Args:
        case_dir: Directory containing investigation_plan.json

    Returns:
        The next subtask dict to work on, or None if all complete
    """
    plan_file = case_dir / "investigation_plan.json"

    if not plan_file.exists():
        return None

    try:
        with open(plan_file) as f:
            plan = json.load(f)

        phases = plan.get("phases", [])

        # Build a map of phase completion
        phase_complete = {}
        for phase in phases:
            phase_id = phase.get("id") or phase.get("phase")
            subtasks = _get_phase_tasks(phase)
            phase_complete[phase_id] = all(
                s.get("status") == "completed" for s in subtasks
            )

        # Find next available subtask
        for phase in phases:
            phase_id = phase.get("id") or phase.get("phase")
            depends_on = phase.get("depends_on", [])

            # Check if dependencies are satisfied
            deps_satisfied = all(phase_complete.get(dep, False) for dep in depends_on)
            if not deps_satisfied:
                continue

            # Find first pending task in this phase
            for subtask in _get_phase_tasks(phase):
                if subtask.get("status") == "pending":
                    return {
                        "phase_id": phase_id,
                        "phase_name": phase.get("name"),
                        "phase_num": phase.get("phase"),
                        **subtask,
                    }

        return None

    except (OSError, json.JSONDecodeError):
        return None


def format_duration(seconds: float) -> str:
    """Format a duration in human-readable form."""
    if seconds < 60:
        return f"{seconds:.0f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"
