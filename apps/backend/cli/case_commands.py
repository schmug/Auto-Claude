"""
Case Commands
=============

CLI commands for managing cases (listing, finding, etc.)
"""

import sys
from pathlib import Path

# Ensure parent directory is in path for imports (before other imports)
_PARENT_DIR = Path(__file__).parent.parent
if str(_PARENT_DIR) not in sys.path:
    sys.path.insert(0, str(_PARENT_DIR))

from progress import count_subtasks
from workspace import get_existing_build_worktree

from .utils import get_cases_dir


def list_cases(project_dir: Path) -> list[dict]:
    """
    List all cases in the project.

    Args:
        project_dir: Project root directory

    Returns:
        List of case info dicts with keys: number, name, path, status, progress
    """
    cases_dir = get_cases_dir(project_dir)
    cases = []

    if not cases_dir.exists():
        return cases

    for case_folder in sorted(cases_dir.iterdir()):
        if not case_folder.is_dir():
            continue

        # Parse folder name (e.g., "001-initial-app")
        folder_name = case_folder.name
        parts = folder_name.split("-", 1)
        if len(parts) != 2 or not parts[0].isdigit():
            continue

        number = parts[0]
        name = parts[1]

        # Check for case.md or case.md
        case_file = case_folder / "case.md"
        case_file = case_folder / "case.md"
        if not case_file.exists() and not case_file.exists():
            continue

        # Check for existing build in worktree
        has_build = get_existing_build_worktree(project_dir, folder_name) is not None

        # Check progress via investigation_plan.json
        plan_file = case_folder / "investigation_plan.json"
        if plan_file.exists():
            completed, total = count_subtasks(case_folder)
            if total > 0:
                if completed == total:
                    status = "complete"
                else:
                    status = "in_progress"
                progress = f"{completed}/{total}"
            else:
                status = "initialized"
                progress = "0/0"
        else:
            status = "pending"
            progress = "-"

        # Add build indicator
        if has_build:
            status = f"{status} (has build)"

        cases.append(
            {
                "number": number,
                "name": name,
                "folder": folder_name,
                "path": case_folder,
                "status": status,
                "progress": progress,
                "has_build": has_build,
            }
        )

    return cases


def print_cases_list(project_dir: Path, auto_create: bool = True) -> None:
    """Print a formatted list of all cases.

    Args:
        project_dir: Project root directory
        auto_create: If True and no cases exist, automatically launch case creation
    """
    import subprocess

    cases = list_cases(project_dir)

    if not cases:
        print("\nNo cases found.")

        if auto_create:
            # Get the backend directory and find case_runner.py
            backend_dir = Path(__file__).parent.parent
            case_runner = backend_dir / "runners" / "case_runner.py"

            # Find Python executable - use current interpreter
            python_path = sys.executable

            if case_runner.exists() and python_path:
                # Quick prompt for task description
                print("\n" + "=" * 60)
                print("  QUICK START")
                print("=" * 60)
                print("\nWhat do you want to build?")
                print(
                    "(Enter a brief description, or press Enter for interactive mode)\n"
                )

                try:
                    task = input("> ").strip()
                except (EOFError, KeyboardInterrupt):
                    print("\nCancelled.")
                    return

                if task:
                    # Direct mode: create case and start building
                    print(f"\nStarting build for: {task}\n")
                    subprocess.run(
                        [
                            python_path,
                            str(case_runner),
                            "--task",
                            task,
                            "--complexity",
                            "simple",
                            "--auto-approve",
                        ],
                        cwd=project_dir,
                    )
                else:
                    # Interactive mode
                    print("\nLaunching interactive mode...\n")
                    subprocess.run(
                        [python_path, str(case_runner), "--interactive"],
                        cwd=project_dir,
                    )
                return
            else:
                print("\nCreate your first case:")
                print("  python runners/case_runner.py --interactive")
        else:
            print("\nCreate your first case:")
            print("  python runners/case_runner.py --interactive")
        return

    print("\n" + "=" * 70)
    print("  AVAILABLE CASES")
    print("=" * 70)
    print()

    # Status symbols
    status_symbols = {
        "complete": "[OK]",
        "in_progress": "[..]",
        "initialized": "[--]",
        "pending": "[  ]",
    }

    for case in cases:
        # Get base status for symbol
        base_status = case["status"].split(" ")[0]
        symbol = status_symbols.get(base_status, "[??]")

        print(f"  {symbol} {case['folder']}")
        status_line = f"       Status: {case['status']} | Subtasks: {case['progress']}"
        print(status_line)
        print()

    print("-" * 70)
    print("\nTo run a case:")
    print("  python auto-sleuth/run.py --case 001")
    print("  python auto-sleuth/run.py --case 001-feature-name")
    print()
