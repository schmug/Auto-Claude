"""
Evidence Validator Agent Module
===============================

Handles validation of DFIR investigation findings, evidence integrity, and chain of custody.
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


async def run_evidence_validator(
    project_dir: Path,
    case_dir: Path,
    model: str,
    verbose: bool = False,
) -> bool:
    """
    Run the evidence validator to verify investigation findings.

    The validator agent will:
    - Verify evidence integrity (hash verification)
    - Validate chain of custody documentation
    - Check IOC extraction completeness and accuracy
    - Validate timeline consistency
    - Verify MITRE ATT&CK mappings
    - Check threat intelligence enrichment
    - Cross-reference findings across evidence sources
    - Generate validation report

    Args:
        project_dir: Root directory for the project
        case_dir: Directory containing the case
        model: Claude model to use
        verbose: Whether to show detailed output

    Returns:
        bool: True if validation passed (approved), False if rejected
    """
    from prompts import get_evidence_validator_prompt

    # Initialize status manager
    status_manager = StatusManager(project_dir)
    status_manager.set_active(case_dir.name, BuildState.VALIDATING)
    emit_phase(ExecutionPhase.VALIDATION, "Validating investigation findings")

    # Initialize task logger
    task_logger = get_task_logger(case_dir)

    # Show header
    content = [
        bold(f"{icon(Icons.GEAR)} EVIDENCE VALIDATION SESSION"),
        "",
        f"Case: {highlight(case_dir.name)}",
        muted("Validating investigation findings and evidence integrity."),
        "",
        muted("The validator will check:"),
        muted("  • Evidence integrity (hash verification)"),
        muted("  • Chain of custody documentation"),
        muted("  • IOC extraction and validation"),
        muted("  • Timeline consistency"),
        muted("  • MITRE ATT&CK mappings"),
        muted("  • Cross-reference findings"),
    ]
    print()
    print(box(content, width=70, style="heavy"))
    print()

    # Start validation phase in task logger
    if task_logger:
        task_logger.start_phase(LogPhase.VALIDATION, "Starting evidence validation...")
        task_logger.set_session(1)

    # Create client with phase-specific model and thinking budget
    validation_model = get_phase_model(case_dir, "validation", model)
    validation_thinking_budget = get_phase_thinking_budget(case_dir, "validation")
    client = create_client(
        project_dir,
        case_dir,
        validation_model,
        agent_type="validator",
        max_thinking_tokens=validation_thinking_budget,
    )

    # Generate evidence validator prompt
    prompt = get_evidence_validator_prompt(case_dir)

    print_status("Running evidence validator...", "progress")
    print()

    try:
        # Run validation session
        async with client:
            status, response = await run_agent_session(
                client, prompt, case_dir, verbose, phase=LogPhase.VALIDATION
            )

        # End validation phase in task logger
        if task_logger:
            task_logger.end_phase(
                LogPhase.VALIDATION,
                success=(status != "error"),
                message="Evidence validation session completed",
            )

        if status == "error":
            print()
            print_status("Evidence validation failed", "error")
            status_manager.update(state=BuildState.ERROR)
            return False

        # Check validation result
        validation_report = case_dir / "validation_report.md"
        investigation_plan = case_dir / "investigation_plan.json"

        if validation_report.exists():
            # Read validation report to determine result
            report_content = validation_report.read_text()

            if "SIGN-OFF: APPROVED" in report_content or "Status: APPROVED" in report_content:
                print()
                content = [
                    bold(f"{icon(Icons.SUCCESS)} EVIDENCE VALIDATION PASSED"),
                    "",
                    "All validation criteria verified:",
                    "  ✓ Evidence integrity verified",
                    "  ✓ Chain of custody complete",
                    "  ✓ IOCs validated",
                    "  ✓ Timeline consistent",
                    "  ✓ MITRE mappings accurate",
                    "",
                    muted("Investigation is ready for report generation."),
                ]
                print(box(content, width=70, style="heavy"))
                print()
                status_manager.update(state=BuildState.COMPLETE)
                emit_phase(ExecutionPhase.COMPLETE, "Investigation validated")
                return True

            elif "SIGN-OFF: REJECTED" in report_content or "Status: REJECTED" in report_content:
                print()
                content = [
                    bold(f"{icon(Icons.ERROR)} EVIDENCE VALIDATION FAILED"),
                    "",
                    "Issues found that require attention.",
                    "See: validation_report.md for details",
                    "",
                    muted("Fix the issues and re-run validation."),
                ]
                print(box(content, width=70, style="heavy"))
                print()
                status_manager.update(state=BuildState.PAUSED)
                return False

            else:
                print()
                print_status("Validation result unclear - check validation_report.md", "warning")
                status_manager.update(state=BuildState.PAUSED)
                return False

        else:
            print()
            print_status("Error: validation_report.md not created", "error")
            status_manager.update(state=BuildState.ERROR)
            return False

    except Exception as e:
        print()
        print_status(f"Evidence validation error: {e}", "error")
        if task_logger:
            task_logger.log_error(f"Evidence validation error: {e}", LogPhase.VALIDATION)
        status_manager.update(state=BuildState.ERROR)
        return False


async def run_validation_loop(
    project_dir: Path,
    case_dir: Path,
    model: str,
    max_iterations: int = 5,
    verbose: bool = False,
) -> bool:
    """
    Run the validation loop until findings are approved or max iterations reached.

    The loop:
    1. Runs evidence validator
    2. If rejected, runs evidence analyst to fix issues
    3. Repeats until approved or max iterations

    Args:
        project_dir: Root directory for the project
        case_dir: Directory containing the case
        model: Claude model to use
        max_iterations: Maximum validation attempts
        verbose: Whether to show detailed output

    Returns:
        bool: True if validation eventually passed
    """
    from .evidence_analyst import run_autonomous_analyst

    for iteration in range(1, max_iterations + 1):
        print()
        print(f"{'=' * 70}")
        print(f"  VALIDATION ITERATION {iteration}/{max_iterations}")
        print(f"{'=' * 70}")
        print()

        # Run validation
        approved = await run_evidence_validator(
            project_dir=project_dir,
            case_dir=case_dir,
            model=model,
            verbose=verbose,
        )

        if approved:
            print()
            print_status(f"Investigation validated after {iteration} iteration(s)", "success")
            return True

        if iteration < max_iterations:
            # Check if there's a fix request
            fix_request = case_dir / "VALIDATION_FIX_REQUEST.md"
            if fix_request.exists():
                print()
                print_status("Fix request found - running evidence analyst to address issues", "info")

                # Run analyst to fix issues
                await run_autonomous_analyst(
                    project_dir=project_dir,
                    case_dir=case_dir,
                    model=model,
                    max_iterations=1,  # Single iteration to fix issues
                    verbose=verbose,
                )

                # Remove fix request after processing
                fix_request.unlink()
            else:
                print()
                print_status("No fix request found - cannot auto-fix", "warning")
                break

    print()
    print_status(f"Validation failed after {max_iterations} iterations", "error")
    print(muted("Manual intervention required."))
    return False


async def verify_evidence_integrity(case_dir: Path) -> dict:
    """
    Verify integrity of all evidence files by checking hashes.

    Args:
        case_dir: Directory containing the case

    Returns:
        dict: Verification results with status for each evidence file
    """
    import hashlib
    import json

    results = {
        "verified": [],
        "failed": [],
        "missing": [],
    }

    # Load evidence inventory
    inventory_file = case_dir / "evidence_inventory.json"
    if not inventory_file.exists():
        return {"error": "evidence_inventory.json not found"}

    with open(inventory_file) as f:
        inventory = json.load(f)

    evidence_dir = case_dir / "evidence"

    for source_name, source_info in inventory.get("evidence_sources", {}).items():
        original_hash = source_info.get("original_hash")
        hash_algorithm = source_info.get("hash_algorithm", "sha256")

        # Find the evidence file
        evidence_file = evidence_dir / source_name
        if not evidence_file.exists():
            # Try with common extensions
            for ext in ["", ".evtx", ".log", ".pcap", ".dmp", ".json"]:
                test_file = evidence_dir / f"{source_name}{ext}"
                if test_file.exists():
                    evidence_file = test_file
                    break

        if not evidence_file.exists():
            results["missing"].append({
                "source": source_name,
                "expected_hash": original_hash,
            })
            continue

        # Calculate current hash
        hasher = hashlib.new(hash_algorithm)
        with open(evidence_file, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        current_hash = hasher.hexdigest()

        if current_hash == original_hash:
            results["verified"].append({
                "source": source_name,
                "hash": current_hash,
                "algorithm": hash_algorithm,
            })
        else:
            results["failed"].append({
                "source": source_name,
                "expected_hash": original_hash,
                "current_hash": current_hash,
                "algorithm": hash_algorithm,
            })

    return results


async def verify_chain_of_custody(case_dir: Path) -> dict:
    """
    Verify chain of custody documentation is complete.

    Args:
        case_dir: Directory containing the case

    Returns:
        dict: Verification results
    """
    results = {
        "complete": True,
        "issues": [],
        "entries": 0,
    }

    coc_file = case_dir / "chain_of_custody.log"
    if not coc_file.exists():
        results["complete"] = False
        results["issues"].append("chain_of_custody.log not found")
        return results

    with open(coc_file) as f:
        entries = f.readlines()

    results["entries"] = len(entries)

    # Check for required entries
    required_events = [
        "Investigation started",
        "Evidence collected",
    ]

    content = coc_file.read_text()
    for event in required_events:
        if event.lower() not in content.lower():
            results["issues"].append(f"Missing required event: {event}")
            results["complete"] = False

    # Check timestamp format
    import re
    timestamp_pattern = r'\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}'
    for i, entry in enumerate(entries, 1):
        if not re.match(timestamp_pattern, entry.strip()):
            results["issues"].append(f"Line {i}: Invalid timestamp format")
            results["complete"] = False

    return results
