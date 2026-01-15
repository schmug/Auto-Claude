"""
Evidence Analyst Agent Module
=============================

Main autonomous agent loop that runs the evidence analyst agent to execute investigation steps.
"""

import asyncio
import logging
import os
from pathlib import Path

from core.client import create_client
from linear_updater import (
    LinearTaskState,
    is_linear_enabled,
    linear_build_complete,
    linear_task_started,
    linear_task_stuck,
)
from phase_config import get_phase_model, get_phase_thinking_budget
from phase_event import ExecutionPhase, emit_phase
from progress import (
    count_investigation_steps,
    count_investigation_steps_detailed,
    get_current_investigation_phase,
    get_next_investigation_step,
    is_investigation_complete,
    print_investigation_complete_banner,
    print_investigation_progress_summary,
    print_session_header,
)
from prompt_generator import (
    format_context_for_prompt,
    generate_case_planner_prompt,
    generate_investigation_step_prompt,
    load_investigation_step_context,
)
from prompts import is_first_run
from recovery import RecoveryManager
from security.constants import PROJECT_DIR_ENV_VAR
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
    print_key_value,
    print_status,
)

from .base import AUTO_CONTINUE_DELAY_SECONDS, HUMAN_INTERVENTION_FILE
from .memory_manager import debug_memory_system_status, get_graphiti_context
from .session import post_session_processing, run_agent_session
from .utils import (
    find_phase_for_step,
    get_commit_count,
    get_latest_commit,
    load_investigation_plan,
    sync_case_to_source,
)

logger = logging.getLogger(__name__)


async def run_autonomous_analyst(
    project_dir: Path,
    case_dir: Path,
    model: str,
    max_iterations: int | None = None,
    verbose: bool = False,
    source_case_dir: Path | None = None,
) -> None:
    """
    Run the autonomous evidence analyst loop with automatic memory management.

    The agent can use subagents (via Task tool) for parallel execution if needed.
    This is decided by the agent itself based on the investigation complexity.

    Args:
        project_dir: Root directory for the project
        case_dir: Directory containing the case (auto-dfir/cases/001-name/)
        model: Claude model to use
        max_iterations: Maximum number of iterations (None for unlimited)
        verbose: Whether to show detailed output
        source_case_dir: Original case directory in main project (for syncing from worktree)
    """
    # Set environment variable for security hooks to find the correct project directory
    os.environ[PROJECT_DIR_ENV_VAR] = str(project_dir.resolve())

    # Initialize recovery manager (handles memory persistence)
    recovery_manager = RecoveryManager(case_dir, project_dir)

    # Initialize status manager for status line
    status_manager = StatusManager(project_dir)
    status_manager.set_active(case_dir.name, BuildState.BUILDING)

    # Initialize task logger for persistent logging
    task_logger = get_task_logger(case_dir)

    # Debug: Print memory system status at startup
    debug_memory_system_status()

    # Update initial investigation step counts
    steps = count_investigation_steps_detailed(case_dir)
    status_manager.update_subtasks(
        completed=steps["completed"],
        total=steps["total"],
        in_progress=steps["in_progress"],
    )

    # Check Linear integration status
    linear_task = None
    if is_linear_enabled():
        linear_task = LinearTaskState.load(case_dir)
        if linear_task and linear_task.task_id:
            print_status("Linear integration: ENABLED", "success")
            print_key_value("Task", linear_task.task_id)
            print_key_value("Status", linear_task.status)
            print()
        else:
            print_status("Linear enabled but no task created for this case", "warning")
            print()

    # Check if this is a fresh start or continuation
    first_run = is_first_run(case_dir)

    # Track which phase we're in for logging
    current_log_phase = LogPhase.CODING  # Using CODING for analysis phase
    is_planning_phase = False

    if first_run:
        print_status(
            "Fresh start - will use Case Planner Agent to create investigation plan", "info"
        )
        content = [
            bold(f"{icon(Icons.GEAR)} CASE PLANNER SESSION"),
            "",
            f"Case: {highlight(case_dir.name)}",
            muted("The agent will analyze evidence and create an investigation plan."),
        ]
        print()
        print(box(content, width=70, style="heavy"))
        print()

        # Update status for planning phase
        status_manager.update(state=BuildState.PLANNING)
        emit_phase(ExecutionPhase.PLANNING, "Creating investigation plan")
        is_planning_phase = True
        current_log_phase = LogPhase.PLANNING

        # Start planning phase in task logger
        if task_logger:
            task_logger.start_phase(
                LogPhase.PLANNING, "Starting investigation planning..."
            )

        # Update Linear to "In Progress" when investigation starts
        if linear_task and linear_task.task_id:
            print_status("Updating Linear task to In Progress...", "progress")
            await linear_task_started(case_dir)
    else:
        print(f"Continuing investigation: {highlight(case_dir.name)}")
        print_investigation_progress_summary(case_dir)

        # Check if already complete
        if is_investigation_complete(case_dir):
            print_investigation_complete_banner(case_dir)
            status_manager.update(state=BuildState.COMPLETE)
            return

        # Start/continue analysis phase in task logger
        if task_logger:
            task_logger.start_phase(LogPhase.CODING, "Continuing evidence analysis...")

        # Emit phase event when continuing investigation
        emit_phase(ExecutionPhase.CODING, "Continuing evidence analysis")

    # Show human intervention hint
    content = [
        bold("INTERACTIVE CONTROLS"),
        "",
        f"Press {highlight('Ctrl+C')} once  {icon(Icons.ARROW_RIGHT)} Pause and optionally add instructions",
        f"Press {highlight('Ctrl+C')} twice {icon(Icons.ARROW_RIGHT)} Exit immediately",
    ]
    print(box(content, width=70, style="light"))
    print()

    # Main loop
    iteration = 0

    while True:
        iteration += 1

        # Check for human intervention (PAUSE file)
        pause_file = case_dir / HUMAN_INTERVENTION_FILE
        if pause_file.exists():
            print("\n" + "=" * 70)
            print("  PAUSED BY ANALYST")
            print("=" * 70)

            pause_content = pause_file.read_text().strip()
            if pause_content:
                print(f"\nMessage: {pause_content}")

            print("\nTo resume, delete the PAUSE file:")
            print(f"  rm {pause_file}")
            print("\nThen run again:")
            print(f"  python auto-dfir/run.py --case {case_dir.name}")
            return

        # Check max iterations
        if max_iterations and iteration > max_iterations:
            print(f"\nReached max iterations ({max_iterations})")
            print("To continue, run the script again without --max-iterations")
            break

        # Get the next investigation step to work on
        next_step = get_next_investigation_step(case_dir)
        step_id = next_step.get("id") if next_step else None
        phase_name = next_step.get("phase_name") if next_step else None

        # Update status for this session
        status_manager.update_session(iteration)
        if phase_name:
            current_phase = get_current_investigation_phase(case_dir)
            if current_phase:
                status_manager.update_phase(
                    current_phase.get("name", ""),
                    current_phase.get("phase", 0),
                    current_phase.get("total", 0),
                )
        status_manager.update_subtasks(in_progress=1)

        # Print session header
        print_session_header(
            session_num=iteration,
            is_planner=first_run,
            subtask_id=step_id,
            subtask_desc=next_step.get("description") if next_step else None,
            phase_name=phase_name,
            attempt=recovery_manager.get_attempt_count(step_id) + 1
            if step_id
            else 1,
        )

        # Capture state before session for post-processing
        commit_before = get_latest_commit(project_dir)
        commit_count_before = get_commit_count(project_dir)

        # Get the phase-specific model and thinking level
        current_phase = "planning" if first_run else "coding"
        phase_model = get_phase_model(case_dir, current_phase, model)
        phase_thinking_budget = get_phase_thinking_budget(case_dir, current_phase)

        # Create client (fresh context) with phase-specific model and thinking
        client = create_client(
            project_dir,
            case_dir,
            phase_model,
            agent_type="planner" if first_run else "analyst",
            max_thinking_tokens=phase_thinking_budget,
        )

        # Generate appropriate prompt
        if first_run:
            prompt = generate_case_planner_prompt(case_dir, project_dir)

            # Retrieve Graphiti memory context for planning phase
            planner_context = await get_graphiti_context(
                case_dir,
                project_dir,
                {
                    "description": "Planning investigation for security incident",
                    "id": "case_planner",
                },
            )
            if planner_context:
                prompt += "\n\n" + planner_context
                print_status("Graphiti memory context loaded for case planner", "success")

            first_run = False
            current_log_phase = LogPhase.PLANNING

            # Set session info in logger
            if task_logger:
                task_logger.set_session(iteration)

        else:
            # Switch to analysis phase after planning
            if is_planning_phase:
                is_planning_phase = False
                current_log_phase = LogPhase.CODING
                emit_phase(ExecutionPhase.CODING, "Starting evidence analysis")
                if task_logger:
                    task_logger.end_phase(
                        LogPhase.PLANNING,
                        success=True,
                        message="Investigation plan created",
                    )
                    task_logger.start_phase(
                        LogPhase.CODING, "Starting evidence analysis..."
                    )

            if not next_step:
                print("No pending investigation steps found - investigation may be complete!")
                break

            # Get attempt count for recovery context
            attempt_count = recovery_manager.get_attempt_count(step_id)
            recovery_hints = (
                recovery_manager.get_recovery_hints(step_id)
                if attempt_count > 0
                else None
            )

            # Find the phase for this step
            plan = load_investigation_plan(case_dir)
            phase = find_phase_for_step(plan, step_id) if plan else {}

            # Generate focused, minimal prompt for this investigation step
            prompt = generate_investigation_step_prompt(
                case_dir=case_dir,
                project_dir=project_dir,
                step=next_step,
                phase=phase or {},
                attempt_count=attempt_count,
                recovery_hints=recovery_hints,
            )

            # Load and append relevant evidence context
            context = load_investigation_step_context(case_dir, project_dir, next_step)
            if context.get("patterns") or context.get("artifacts_to_analyze"):
                prompt += "\n\n" + format_context_for_prompt(context)

            # Retrieve and append Graphiti memory context (if enabled)
            graphiti_context = await get_graphiti_context(
                case_dir, project_dir, next_step
            )
            if graphiti_context:
                prompt += "\n\n" + graphiti_context
                print_status("Graphiti memory context loaded", "success")

            # Show what we're working on
            print(f"Working on: {highlight(step_id)}")
            print(f"Description: {next_step.get('description', 'No description')}")
            if attempt_count > 0:
                print_status(f"Previous attempts: {attempt_count}", "warning")
            print()

        # Set step info in logger
        if task_logger and step_id:
            task_logger.set_subtask(step_id)
            task_logger.set_session(iteration)

        # Run session with async context manager
        async with client:
            status, response = await run_agent_session(
                client, prompt, case_dir, verbose, phase=current_log_phase
            )

        # === POST-SESSION PROCESSING ===
        if step_id and not first_run:
            linear_is_enabled = (
                linear_task is not None and linear_task.task_id is not None
            )
            success = await post_session_processing(
                spec_dir=case_dir,
                project_dir=project_dir,
                subtask_id=step_id,
                session_num=iteration,
                commit_before=commit_before,
                commit_count_before=commit_count_before,
                recovery_manager=recovery_manager,
                linear_enabled=linear_is_enabled,
                status_manager=status_manager,
                source_spec_dir=source_case_dir,
            )

            # Check for stuck investigation steps
            attempt_count = recovery_manager.get_attempt_count(step_id)
            if not success and attempt_count >= 3:
                recovery_manager.mark_subtask_stuck(
                    step_id, f"Failed after {attempt_count} attempts"
                )
                print()
                print_status(
                    f"Investigation step {step_id} marked as STUCK after {attempt_count} attempts",
                    "error",
                )
                print(muted("Consider: manual intervention or skipping this step"))

                # Record stuck step in Linear (if enabled)
                if linear_is_enabled:
                    await linear_task_stuck(
                        spec_dir=case_dir,
                        subtask_id=step_id,
                        attempt_count=attempt_count,
                    )
                    print_status("Linear notified of stuck investigation step", "info")
        elif is_planning_phase and source_case_dir:
            # After planning phase, sync the newly created investigation plan back to source
            if sync_case_to_source(case_dir, source_case_dir):
                print_status("Investigation plan synced to main project", "success")

        # Handle session status
        if status == "complete":
            print_investigation_complete_banner(case_dir)
            status_manager.update(state=BuildState.COMPLETE)

            if task_logger:
                task_logger.end_phase(
                    LogPhase.CODING,
                    success=True,
                    message="All investigation steps completed successfully",
                )

            if linear_task and linear_task.task_id:
                await linear_build_complete(case_dir)
                print_status("Linear notified: investigation complete, ready for validation", "success")

            break

        elif status == "continue":
            print(
                muted(
                    f"\nAgent will auto-continue in {AUTO_CONTINUE_DELAY_SECONDS}s..."
                )
            )
            print_investigation_progress_summary(case_dir)

            # Update state back to building
            status_manager.update(state=BuildState.BUILDING)

            # Show next investigation step info
            next_step = get_next_investigation_step(case_dir)
            if next_step:
                step_id = next_step.get("id")
                print(
                    f"\nNext: {highlight(step_id)} - {next_step.get('description')}"
                )

                attempt_count = recovery_manager.get_attempt_count(step_id)
                if attempt_count > 0:
                    print_status(
                        f"WARNING: {attempt_count} previous attempt(s)", "warning"
                    )

            await asyncio.sleep(AUTO_CONTINUE_DELAY_SECONDS)

        elif status == "error":
            emit_phase(ExecutionPhase.FAILED, "Session encountered an error")
            print_status("Session encountered an error", "error")
            print(muted("Will retry with a fresh session..."))
            status_manager.update(state=BuildState.ERROR)
            await asyncio.sleep(AUTO_CONTINUE_DELAY_SECONDS)

        # Small delay between sessions
        if max_iterations is None or iteration < max_iterations:
            print("\nPreparing next session...\n")
            await asyncio.sleep(1)

    # Final summary
    content = [
        bold(f"{icon(Icons.SESSION)} SESSION SUMMARY"),
        "",
        f"Project: {project_dir}",
        f"Case: {highlight(case_dir.name)}",
        f"Sessions completed: {iteration}",
    ]
    print()
    print(box(content, width=70, style="heavy"))
    print_investigation_progress_summary(case_dir)

    # Show stuck investigation steps if any
    stuck_steps = recovery_manager.get_stuck_subtasks()
    if stuck_steps:
        print()
        print_status("STUCK INVESTIGATION STEPS (need manual intervention):", "error")
        for stuck in stuck_steps:
            print(f"  {icon(Icons.ERROR)} {stuck['subtask_id']}: {stuck['reason']}")

    # Instructions
    completed, total = count_investigation_steps(case_dir)
    if completed < total:
        content = [
            bold(f"{icon(Icons.PLAY)} NEXT STEPS"),
            "",
            f"{total - completed} investigation steps remaining.",
            f"Run again: {highlight(f'python auto-dfir/run.py --case {case_dir.name}')}",
        ]
    else:
        content = [
            bold(f"{icon(Icons.SUCCESS)} NEXT STEPS"),
            "",
            "All investigation steps completed!",
            "  1. Review the findings in analysis/",
            "  2. Run evidence validation",
            "  3. Generate final report",
        ]

    print()
    print(box(content, width=70, style="light"))
    print()

    # Set final status
    if completed == total:
        status_manager.update(state=BuildState.COMPLETE)
    else:
        status_manager.update(state=BuildState.PAUSED)
