"""
Display Formatters
==================

Provides formatted display functions for case summaries, implementation plans,
and review status information.
"""

import json
import re
from datetime import datetime
from pathlib import Path

from ui import (
    Icons,
    bold,
    box,
    highlight,
    icon,
    info,
    muted,
    print_status,
    success,
    warning,
)

from .diff_analyzer import (
    extract_checkboxes,
    extract_section,
    extract_title,
    truncate_text,
)
from .state import ReviewState, get_review_status_summary


def display_case_summary(case_dir: Path) -> None:
    """
    Display key sections of case.md for human review.

    Extracts and displays:
    - Overview
    - Investigation Type
    - Evidence Sources
    - Success Criteria

    Uses formatted boxes for readability.

    Args:
        case_dir: Path to the case directory
    """
    case_file = Path(case_dir) / "case.md"

    if not case_file.exists():
        print_status("case.md not found", "error")
        return

    try:
        content = case_file.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        print_status(f"Could not read case.md: {e}", "error")
        return

    # Extract the title from first H1
    title = extract_title(content)

    # Build summary content
    summary_lines = []

    # Title
    summary_lines.append(bold(f"{icon(Icons.DOCUMENT)} {title}"))
    summary_lines.append("")

    # Overview
    overview = extract_section(content, "## Overview")
    if overview:
        summary_lines.append(highlight("Overview:"))
        truncated = truncate_text(overview, max_lines=4, max_chars=250)
        for line in truncated.split("\n"):
            summary_lines.append(f"  {line}")
        summary_lines.append("")

    # Investigation Type (fallback to legacy Workflow Type)
    investigation_section = extract_section(content, "## Investigation Type") or extract_section(content, "## Workflow Type")
    if investigation_section:
        # Extract just the type value
        type_match = re.search(r"\*\*Type\*\*:\s*([^\n]+)", investigation_section)
        if type_match:
            summary_lines.append(f"{muted('Investigation:')} {type_match.group(1).strip()}")

    # Evidence Sources
    evidence_section = extract_section(content, "## Evidence Sources")
    if evidence_section:
        sources = []
        for line in evidence_section.splitlines():
            if line.startswith("### "):
                sources.append(line.replace("### ", "").strip())
        if sources:
            summary_lines.append("")
            summary_lines.append(highlight("Evidence Sources:"))
            for source in sources[:6]:
                summary_lines.append(f"  {icon(Icons.FILE)} {source}")
            if len(sources) > 6:
                summary_lines.append(f"  {muted(f'... and {len(sources) - 6} more')}")

    # Success Criteria
    criteria = extract_section(content, "## Success Criteria")
    if criteria:
        summary_lines.append("")
        summary_lines.append(highlight("Success Criteria:"))
        # Extract checkbox items
        checkboxes = extract_checkboxes(criteria, max_items=5)
        for item in checkboxes:
            summary_lines.append(
                f"  {icon(Icons.PENDING)} {item[:60]}{'...' if len(item) > 60 else ''}"
            )
        if len(re.findall(r"^\s*[-*]\s*\[[ x]\]\s*(.+)$", criteria, re.MULTILINE)) > 5:
            total_count = len(
                re.findall(r"^\s*[-*]\s*\[[ x]\]\s*(.+)$", criteria, re.MULTILINE)
            )
            summary_lines.append(f"  {muted(f'... and {total_count - 5} more')}")

    # Print the summary box
    print()
    print(box(summary_lines, width=80, style="heavy"))


def display_plan_summary(case_dir: Path) -> None:
    """
    Display summary of investigation_plan.json for human review.

    Shows:
    - Phase count and names
    - Subtask count per phase
    - Total work estimate
    - Services involved

    Args:
        case_dir: Path to the case directory
    """
    plan_file = Path(case_dir) / "investigation_plan.json"

    if not plan_file.exists():
        print_status("investigation_plan.json not found", "error")
        return

    try:
        with open(plan_file) as f:
            plan = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print_status(f"Could not read investigation_plan.json: {e}", "error")
        return

    # Build summary content
    summary_lines = []

    case_title = plan.get("case_name") or plan.get("case_id") or "Investigation Plan"
    summary_lines.append(bold(f"{icon(Icons.GEAR)} {case_title}"))
    summary_lines.append("")

    # Overall stats
    phases = plan.get("phases", [])
    def _phase_tasks(phase: dict) -> list[dict]:
        tasks = phase.get("analysis_tasks")
        if isinstance(tasks, list):
            return tasks
        return phase.get("subtasks", []) or []

    total_subtasks = sum(len(_phase_tasks(p)) for p in phases)
    completed_subtasks = sum(
        1 for p in phases for c in _phase_tasks(p) if c.get("status") == "completed"
    )
    services = plan.get("evidence_sources", [])

    summary_lines.append(f"{muted('Phases:')} {len(phases)}")
    summary_lines.append(
        f"{muted('Tasks:')} {completed_subtasks}/{total_subtasks} completed"
    )
    if services:
        summary_lines.append(f"{muted('Evidence Sources:')} {', '.join(services)}")

    # Phases breakdown
    if phases:
        summary_lines.append("")
        summary_lines.append(highlight("Investigation Phases:"))

        for phase in phases:
            phase_num = phase.get("phase", "?")
            phase_name = phase.get("name", "Unknown")
            subtasks = _phase_tasks(phase)
            subtask_count = len(subtasks)
            completed = sum(1 for c in subtasks if c.get("status") == "completed")

            # Determine phase status icon
            if completed == subtask_count and subtask_count > 0:
                status_icon = icon(Icons.SUCCESS)
                phase_display = success(f"Phase {phase_num}: {phase_name}")
            elif completed > 0:
                status_icon = icon(Icons.IN_PROGRESS)
                phase_display = info(f"Phase {phase_num}: {phase_name}")
            else:
                status_icon = icon(Icons.PENDING)
                phase_display = f"Phase {phase_num}: {phase_name}"

            summary_lines.append(
                f"  {status_icon} {phase_display} ({completed}/{subtask_count} tasks)"
            )

            # Show subtask details for non-completed phases
            if completed < subtask_count:
                for subtask in subtasks[:3]:  # Show max 3 subtasks
                    subtask_id = subtask.get("id", "")
                    subtask_desc = subtask.get("description", "")
                    subtask_status = subtask.get("status", "pending")

                    if subtask_status == "completed":
                        status_str = success(icon(Icons.SUCCESS))
                    elif subtask_status == "in_progress":
                        status_str = info(icon(Icons.IN_PROGRESS))
                    else:
                        status_str = muted(icon(Icons.PENDING))

                    # Truncate description
                    desc_short = (
                        subtask_desc[:50] + "..."
                        if len(subtask_desc) > 50
                        else subtask_desc
                    )
                    summary_lines.append(
                        f"      {status_str} {muted(subtask_id)}: {desc_short}"
                    )

                if len(subtasks) > 3:
                    remaining = len(subtasks) - 3
                    summary_lines.append(
                        f"      {muted(f'... {remaining} more tasks')}"
                    )

    # Parallelism info
    summary_section = plan.get("summary", {})
    parallelism = summary_section.get("parallelism", {})
    if parallelism:
        recommended_workers = parallelism.get("recommended_workers", 1)
        if recommended_workers > 1:
            summary_lines.append("")
            summary_lines.append(
                f"{icon(Icons.LIGHTNING)} {highlight('Parallel execution supported:')} "
                f"{recommended_workers} workers recommended"
            )

    # Print the summary box
    print()
    print(box(summary_lines, width=80, style="light"))


def display_review_status(case_dir: Path) -> None:
    """
    Display the current review/approval status.

    Shows whether case is approved, by whom, and if changes have been detected.

    Args:
        case_dir: Path to the case directory
    """
    status = get_review_status_summary(case_dir)
    state = ReviewState.load(case_dir)

    content = []

    if status["approved"]:
        if status["valid"]:
            content.append(success(f"{icon(Icons.SUCCESS)} APPROVED"))
            content.append("")
            content.append(f"{muted('Approved by:')} {status['approved_by']}")
            if status["approved_at"]:
                # Format the timestamp nicely
                try:
                    dt = datetime.fromisoformat(status["approved_at"])
                    formatted = dt.strftime("%Y-%m-%d %H:%M")
                    content.append(f"{muted('Approved at:')} {formatted}")
                except ValueError:
                    content.append(f"{muted('Approved at:')} {status['approved_at']}")
        else:
            content.append(warning(f"{icon(Icons.WARNING)} APPROVAL STALE"))
            content.append("")
            content.append("The case has been modified since approval.")
            content.append("Re-approval is required before building.")
    else:
        content.append(info(f"{icon(Icons.INFO)} NOT YET APPROVED"))
        content.append("")
        content.append("This case requires human review before building.")

    # Show review history
    if status["review_count"] > 0:
        content.append("")
        content.append(f"{muted('Review sessions:')} {status['review_count']}")

    # Show feedback if any
    if state.feedback:
        content.append("")
        content.append(highlight("Recent Feedback:"))
        for fb in state.feedback[-3:]:  # Show last 3 feedback items
            content.append(f"  {muted('•')} {fb[:60]}{'...' if len(fb) > 60 else ''}")

    print()
    print(box(content, width=60, style="light"))
