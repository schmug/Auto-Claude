"""
Batch Task Management Commands
==============================

Commands for creating and managing multiple tasks from batch files.
"""

import json
import shutil
import subprocess
from pathlib import Path

from ui import highlight, print_status


def handle_batch_create_command(batch_file: str, project_dir: str) -> bool:
    """
    Create multiple tasks from a batch JSON file.

    Args:
        batch_file: Path to JSON file with task definitions
        project_dir: Project directory

    Returns:
        True if successful
    """
    batch_path = Path(batch_file)

    if not batch_path.exists():
        print_status(f"Batch file not found: {batch_file}", "error")
        return False

    try:
        with open(batch_path) as f:
            batch_data = json.load(f)
    except json.JSONDecodeError as e:
        print_status(f"Invalid JSON in batch file: {e}", "error")
        return False

    tasks = batch_data.get("tasks", [])
    if not tasks:
        print_status("No tasks found in batch file", "warning")
        return False

    print_status(f"Creating {len(tasks)} tasks from batch file", "info")
    print()

    cases_dir = Path(project_dir) / ".auto-sleuth" / "cases"
    cases_dir.mkdir(parents=True, exist_ok=True)

    # Find next case ID
    existing_cases = [d.name for d in cases_dir.iterdir() if d.is_dir()]
    next_id = (
        max([int(s.split("-")[0]) for s in existing_cases if s[0].isdigit()] or [0]) + 1
    )

    created_cases = []

    for idx, task in enumerate(tasks, 1):
        case_id = f"{next_id:03d}"
        task_title = task.get("title", f"Task {idx}")
        task_slug = task_title.lower().replace(" ", "-")[:50]
        case_name = f"{case_id}-{task_slug}"
        case_dir = cases_dir / case_name
        case_dir.mkdir(exist_ok=True)

        # Create requirements.json
        requirements = {
            "task_description": task.get("description", task_title),
            "description": task.get("description", task_title),
            "investigation_type": task.get("investigation_type", task.get("workflow_type", "triage")),
            "evidence_sources": task.get("evidence_sources", task.get("services", [])),
            "priority": task.get("priority", 5),
            "complexity_inferred": task.get("complexity", "standard"),
            "inferred_from": {},
            "created_at": Path(case_dir).stat().st_mtime,
            "estimate": {
                "estimated_hours": task.get("estimated_hours", 4.0),
                "estimated_days": task.get("estimated_days", 0.5),
            },
        }

        req_file = case_dir / "requirements.json"
        with open(req_file, "w") as f:
            json.dump(requirements, f, indent=2, default=str)

        created_cases.append(
            {
                "id": case_id,
                "name": case_name,
                "title": task_title,
                "status": "pending_case_creation",
            }
        )

        print_status(
            f"[{idx}/{len(tasks)}] Created {case_id} - {task_title}", "success"
        )
        next_id += 1

    print()
    print_status(f"Created {len(created_cases)} case(s) successfully", "success")
    print()

    # Show summary
    print(highlight("Next steps:"))
    print("  1. Generate cases: case_runner.py --continue <case_id>")
    print("  2. Approve cases and build them")
    print("  3. Run: python run.py --case <id> to execute")

    return True


def handle_batch_status_command(project_dir: str) -> bool:
    """
    Show status of all cases in project.

    Args:
        project_dir: Project directory

    Returns:
        True if successful
    """
    cases_dir = Path(project_dir) / ".auto-sleuth" / "cases"

    if not cases_dir.exists():
        print_status("No cases found in project", "warning")
        return True

    cases = sorted([d for d in cases_dir.iterdir() if d.is_dir()])

    if not cases:
        print_status("No cases found", "warning")
        return True

    print_status(f"Found {len(cases)} case(s)", "info")
    print()

    for case_dir in cases:
        case_name = case_dir.name
        req_file = case_dir / "requirements.json"

        status = "unknown"
        title = case_name

        if req_file.exists():
            try:
                with open(req_file) as f:
                    req = json.load(f)
                    title = req.get("task_description", title)
            except json.JSONDecodeError:
                pass

        # Determine status (check most advanced state first)
        if (case_dir / "qa_report.md").exists():
            status = "qa_approved"
        elif (case_dir / "investigation_plan.json").exists():
            status = "building"
        elif (case_dir / "case.md").exists() or (case_dir / "case.md").exists():
            status = "case_created"
        else:
            status = "pending_case"

        status_icon = {
            "pending_case": "⏳",
            "case_created": "📋",
            "building": "⚙️",
            "qa_approved": "✅",
            "unknown": "❓",
        }.get(status, "❓")

        print(f"{status_icon} {case_name:<40} {title}")

    return True


def handle_batch_cleanup_command(project_dir: str, dry_run: bool = True) -> bool:
    """
    Clean up completed cases and worktrees.

    Args:
        project_dir: Project directory
        dry_run: If True, show what would be deleted

    Returns:
        True if successful
    """
    cases_dir = Path(project_dir) / ".auto-sleuth" / "cases"
    worktrees_dir = Path(project_dir) / ".auto-sleuth" / "worktrees" / "tasks"

    if not cases_dir.exists():
        print_status("No cases directory found", "info")
        return True

    # Find completed cases
    completed = []
    for case_dir in cases_dir.iterdir():
        if case_dir.is_dir() and (case_dir / "qa_report.md").exists():
            completed.append(case_dir.name)

    if not completed:
        print_status("No completed cases to clean up", "info")
        return True

    print_status(f"Found {len(completed)} completed case(s)", "info")

    if dry_run:
        print()
        print("Would remove:")
        for case_name in completed:
            print(f"  - {case_name}")
            wt_path = worktrees_dir / case_name
            if wt_path.exists():
                print(f"    └─ .auto-sleuth/worktrees/tasks/{case_name}/")
        print()
        print("Run with --no-dry-run to actually delete")
    else:
        # Actually delete cases and worktrees
        deleted_count = 0
        for case_name in completed:
            case_path = cases_dir / case_name
            wt_path = worktrees_dir / case_name

            # Remove worktree first (if exists)
            if wt_path.exists():
                try:
                    result = subprocess.run(
                        ["git", "worktree", "remove", "--force", str(wt_path)],
                        cwd=project_dir,
                        capture_output=True,
                        text=True,
                        timeout=30,
                    )
                    if result.returncode == 0:
                        print_status(f"Removed worktree: {case_name}", "success")
                    else:
                        # Fallback: remove directory manually if git fails
                        shutil.rmtree(wt_path, ignore_errors=True)
                        print_status(
                            f"Removed worktree directory: {case_name}", "success"
                        )
                except subprocess.TimeoutExpired:
                    # Timeout: fall back to manual removal
                    shutil.rmtree(wt_path, ignore_errors=True)
                    print_status(
                        f"Worktree removal timed out, removed directory: {case_name}",
                        "warning",
                    )
                except Exception as e:
                    print_status(
                        f"Failed to remove worktree {case_name}: {e}", "warning"
                    )

            # Remove case directory
            if case_path.exists():
                try:
                    shutil.rmtree(case_path)
                    print_status(f"Removed case: {case_name}", "success")
                    deleted_count += 1
                except Exception as e:
                    print_status(f"Failed to remove case {case_name}: {e}", "error")

        print()
        print_status(f"Cleaned up {deleted_count} case(s)", "info")

    return True
