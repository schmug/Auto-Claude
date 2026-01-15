"""
Case Planner Agent Module
=========================

Handles follow-up case planning sessions for adding new investigation steps to completed cases.
"""

import logging
from pathlib import Path

from core.client import create_client
from phase_config import get_phase_model, get_phase_thinking_budget
from phase_event import ExecutionPhase, emit_phase
from task_logger import (
    LogPhase,
    get_task_logger,
)
from ui import (
    BuildState,
    Icons,
    StatusManager,
    bold,
    box,
    highlight,
    icon,
    muted,
    print_status,
)

from .session import run_agent_session

logger = logging.getLogger(__name__)


async def run_followup_case_planner(
    project_dir: Path,
    case_dir: Path,
    model: str,
    verbose: bool = False,
) -> bool:
    """
    Run the follow-up case planner to add new investigation steps to a completed case.

    This is a simplified version of run_autonomous_agent that:
    1. Creates a client
    2. Loads the followup case planner prompt
    3. Runs a single planning session
    4. Returns after the plan is updated (doesn't enter analysis loop)

    The case planner agent will:
    - Read FOLLOWUP_REQUEST.md for the new investigation requirements
    - Read the existing investigation_plan.json
    - Add new phase(s) with pending investigation steps
    - Update the plan status back to in_progress

    Args:
        project_dir: Root directory for the project
        case_dir: Directory containing the completed case
        model: Claude model to use
        verbose: Whether to show detailed output

    Returns:
        bool: True if planning completed successfully
    """
    from investigation_plan import InvestigationPlan
    from prompts import get_followup_case_planner_prompt

    # Initialize status manager for status line
    status_manager = StatusManager(project_dir)
    status_manager.set_active(case_dir.name, BuildState.PLANNING)
    emit_phase(ExecutionPhase.PLANNING, "Follow-up case planning")

    # Initialize task logger for persistent logging
    task_logger = get_task_logger(case_dir)

    # Show header
    content = [
        bold(f"{icon(Icons.GEAR)} FOLLOW-UP CASE PLANNER SESSION"),
        "",
        f"Case: {highlight(case_dir.name)}",
        muted("Adding follow-up investigation work to completed case."),
        "",
        muted("The agent will read your FOLLOWUP_REQUEST.md and add new investigation steps."),
    ]
    print()
    print(box(content, width=70, style="heavy"))
    print()

    # Start planning phase in task logger
    if task_logger:
        task_logger.start_phase(LogPhase.PLANNING, "Starting follow-up case planning...")
        task_logger.set_session(1)

    # Create client with phase-specific model and thinking budget
    # Respects case_metadata.json configuration when no CLI override
    planning_model = get_phase_model(case_dir, "planning", model)
    planning_thinking_budget = get_phase_thinking_budget(case_dir, "planning")
    client = create_client(
        project_dir,
        case_dir,
        planning_model,
        max_thinking_tokens=planning_thinking_budget,
    )

    # Generate follow-up case planner prompt
    prompt = get_followup_case_planner_prompt(case_dir)

    print_status("Running follow-up case planner...", "progress")
    print()

    try:
        # Run single planning session
        async with client:
            status, response = await run_agent_session(
                client, prompt, case_dir, verbose, phase=LogPhase.PLANNING
            )

        # End planning phase in task logger
        if task_logger:
            task_logger.end_phase(
                LogPhase.PLANNING,
                success=(status != "error"),
                message="Follow-up case planning session completed",
            )

        if status == "error":
            print()
            print_status("Follow-up case planning failed", "error")
            status_manager.update(state=BuildState.ERROR)
            return False

        # Verify the plan was updated (should have pending steps now)
        plan_file = case_dir / "investigation_plan.json"
        if plan_file.exists():
            plan = InvestigationPlan.load(plan_file)

            # Check if there are any pending investigation steps
            all_steps = [s for p in plan.phases for s in p.steps]
            pending_steps = [s for s in all_steps if s.status.value == "pending"]

            if pending_steps:
                # Reset the plan status to in_progress (in case planner didn't)
                plan.reset_for_followup()
                plan.save(plan_file)

                print()
                content = [
                    bold(f"{icon(Icons.SUCCESS)} FOLLOW-UP CASE PLANNING COMPLETE"),
                    "",
                    f"New pending investigation steps: {highlight(str(len(pending_steps)))}",
                    f"Total investigation steps: {len(all_steps)}",
                    "",
                    muted("Next steps:"),
                    f"  Run: {highlight(f'python auto-dfir/run.py --case {case_dir.name}')}",
                ]
                print(box(content, width=70, style="heavy"))
                print()
                status_manager.update(state=BuildState.PAUSED)
                return True
            else:
                print()
                print_status(
                    "Warning: No pending investigation steps found after planning", "warning"
                )
                print(muted("The case planner may not have added new investigation steps."))
                print(muted("Check investigation_plan.json manually."))
                status_manager.update(state=BuildState.PAUSED)
                return False
        else:
            print()
            print_status(
                "Error: investigation_plan.json not found after planning", "error"
            )
            status_manager.update(state=BuildState.ERROR)
            return False

    except Exception as e:
        print()
        print_status(f"Follow-up case planning error: {e}", "error")
        if task_logger:
            task_logger.log_error(f"Follow-up case planning error: {e}", LogPhase.PLANNING)
        status_manager.update(state=BuildState.ERROR)
        return False


async def run_initial_case_planning(
    project_dir: Path,
    case_dir: Path,
    model: str,
    verbose: bool = False,
) -> bool:
    """
    Run initial case planning to create the investigation plan from case requirements.

    The case planner agent will:
    - Read case_requirements.json for investigation requirements
    - Read evidence_inventory.json for available evidence
    - Create investigation_plan.json with phases and steps
    - Set up the case structure

    Args:
        project_dir: Root directory for the project
        case_dir: Directory containing the case
        model: Claude model to use
        verbose: Whether to show detailed output

    Returns:
        bool: True if planning completed successfully
    """
    from prompts import get_case_planner_prompt

    # Initialize status manager
    status_manager = StatusManager(project_dir)
    status_manager.set_active(case_dir.name, BuildState.PLANNING)
    emit_phase(ExecutionPhase.PLANNING, "Initial case planning")

    # Initialize task logger
    task_logger = get_task_logger(case_dir)

    # Show header
    content = [
        bold(f"{icon(Icons.GEAR)} CASE PLANNING SESSION"),
        "",
        f"Case: {highlight(case_dir.name)}",
        muted("Creating investigation plan from case requirements."),
        "",
        muted("The agent will analyze evidence and create the investigation plan."),
    ]
    print()
    print(box(content, width=70, style="heavy"))
    print()

    # Start planning phase
    if task_logger:
        task_logger.start_phase(LogPhase.PLANNING, "Starting initial case planning...")
        task_logger.set_session(1)

    # Create client
    planning_model = get_phase_model(case_dir, "planning", model)
    planning_thinking_budget = get_phase_thinking_budget(case_dir, "planning")
    client = create_client(
        project_dir,
        case_dir,
        planning_model,
        max_thinking_tokens=planning_thinking_budget,
    )

    # Generate case planner prompt
    prompt = get_case_planner_prompt(case_dir)

    print_status("Running case planner...", "progress")
    print()

    try:
        async with client:
            status, response = await run_agent_session(
                client, prompt, case_dir, verbose, phase=LogPhase.PLANNING
            )

        if task_logger:
            task_logger.end_phase(
                LogPhase.PLANNING,
                success=(status != "error"),
                message="Initial case planning completed",
            )

        if status == "error":
            print()
            print_status("Case planning failed", "error")
            status_manager.update(state=BuildState.ERROR)
            return False

        # Verify investigation plan was created
        plan_file = case_dir / "investigation_plan.json"
        if plan_file.exists():
            print()
            content = [
                bold(f"{icon(Icons.SUCCESS)} CASE PLANNING COMPLETE"),
                "",
                f"Investigation plan created: {highlight('investigation_plan.json')}",
                "",
                muted("Next steps:"),
                f"  Run: {highlight(f'python auto-dfir/run.py --case {case_dir.name}')}",
            ]
            print(box(content, width=70, style="heavy"))
            print()
            status_manager.update(state=BuildState.PAUSED)
            return True
        else:
            print()
            print_status("Error: investigation_plan.json not created", "error")
            status_manager.update(state=BuildState.ERROR)
            return False

    except Exception as e:
        print()
        print_status(f"Case planning error: {e}", "error")
        if task_logger:
            task_logger.log_error(f"Case planning error: {e}", LogPhase.PLANNING)
        status_manager.update(state=BuildState.ERROR)
        return False
