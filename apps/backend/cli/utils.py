"""
CLI Utilities
==============

Shared utility functions for the Auto Sleuth CLI.
"""

import os
import sys
from pathlib import Path

# Ensure parent directory is in path for imports (before other imports)
_PARENT_DIR = Path(__file__).parent.parent
if str(_PARENT_DIR) not in sys.path:
    sys.path.insert(0, str(_PARENT_DIR))

from core.auth import get_auth_token, get_auth_token_source
from core.dependency_validator import validate_platform_dependencies


def import_dotenv():
    """
    Import and return load_dotenv with helpful error message if not installed.

    This centralized function ensures consistent error messaging across all
    runner scripts when python-dotenv is not available.

    Returns:
        The load_dotenv function

    Raises:
        SystemExit: If dotenv cannot be imported, with helpful installation instructions.
    """
    try:
        from dotenv import load_dotenv as _load_dotenv

        return _load_dotenv
    except ImportError:
        sys.exit(
            "Error: Required Python package 'python-dotenv' is not installed.\n"
            "\n"
            "This usually means you're not using the virtual environment.\n"
            "\n"
            "To fix this:\n"
            "1. From the 'apps/backend/' directory, activate the venv:\n"
            "   source .venv/bin/activate  # Linux/macOS\n"
            "   .venv\\Scripts\\activate   # Windows\n"
            "\n"
            "2. Or install dependencies directly:\n"
            "   pip install python-dotenv\n"
            "   pip install -r requirements.txt\n"
            "\n"
            f"Current Python: {sys.executable}\n"
        )


# Load .env with helpful error if dependencies not installed
load_dotenv = import_dotenv()
from graphiti_config import get_graphiti_status
from linear_integration import LinearManager
from linear_updater import is_linear_enabled
from case.pipeline import get_cases_dir
from ui import (
    Icons,
    bold,
    box,
    icon,
    muted,
)

# Configuration - uses shorthand that resolves via API Profile if configured
DEFAULT_MODEL = "sonnet"  # Changed from "opus" (fix #433)


def setup_environment() -> Path:
    """
    Set up the environment and return the script directory.

    Returns:
        Path to the auto-sleuth directory
    """
    # Add auto-sleuth directory to path for imports
    script_dir = Path(__file__).parent.parent.resolve()
    sys.path.insert(0, str(script_dir))

    # Load .env file - check both auto-sleuth/ and dev/auto-sleuth/ locations
    env_file = script_dir / ".env"
    dev_env_file = script_dir.parent / "dev" / "auto-sleuth" / ".env"
    if env_file.exists():
        load_dotenv(env_file)
    elif dev_env_file.exists():
        load_dotenv(dev_env_file)

    return script_dir


def find_case(project_dir: Path, case_identifier: str) -> Path | None:
    """
    Find a case by number or full name.

    Args:
        project_dir: Project root directory
        case_identifier: Either "001" or "001-feature-name"

    Returns:
        Path to case folder, or None if not found
    """
    cases_dir = get_cases_dir(project_dir)

    if cases_dir.exists():
        # Try exact match first
        exact_path = cases_dir / case_identifier
        if exact_path.exists() and ((exact_path / "case.md").exists() or (exact_path / "case.md").exists()):
            return exact_path

        # Try matching by number prefix
        for case_folder in cases_dir.iterdir():
            if case_folder.is_dir() and case_folder.name.startswith(
                case_identifier + "-"
            ):
                if (case_folder / "case.md").exists() or (case_folder / "case.md").exists():
                    return case_folder

    # Check worktree cases (for merge-preview, merge, review, discard operations)
    worktree_base = project_dir / ".auto-sleuth" / "worktrees" / "tasks"
    if worktree_base.exists():
        # Try exact match in worktree
        worktree_case = (
            worktree_base / case_identifier / ".auto-sleuth" / "cases" / case_identifier
        )
        if worktree_case.exists() and ((worktree_case / "case.md").exists() or (worktree_case / "case.md").exists()):
            return worktree_case

        # Try matching by prefix in worktrees
        for worktree_dir in worktree_base.iterdir():
            if worktree_dir.is_dir() and worktree_dir.name.startswith(
                case_identifier + "-"
            ):
                case_in_worktree = (
                    worktree_dir / ".auto-sleuth" / "cases" / worktree_dir.name
                )
                if (
                    case_in_worktree.exists()
                    and ((case_in_worktree / "case.md").exists() or (case_in_worktree / "case.md").exists())
                ):
                    return case_in_worktree

    return None


def validate_environment(case_dir: Path) -> bool:
    """
    Validate that the environment is set up correctly.

    Returns:
        True if valid, False otherwise (with error messages printed)
    """
    # Validate platform-caseific dependencies first (exits if missing)
    validate_platform_dependencies()

    valid = True

    # Check for OAuth token (API keys are not supported)
    if not get_auth_token():
        print("Error: No OAuth token found")
        print("\nAuto Sleuth requires Claude Code OAuth authentication.")
        print("Direct API keys (ANTHROPIC_API_KEY) are not supported.")
        print("\nTo authenticate, run:")
        print("  claude setup-token")
        valid = False
    else:
        # Show which auth source is being used
        source = get_auth_token_source()
        if source:
            print(f"Auth: {source}")

        # Show custom base URL if set
        base_url = os.environ.get("ANTHROPIC_BASE_URL")
        if base_url:
            print(f"API Endpoint: {base_url}")

    # Check for case.md or case.md in case directory
    case_file = case_dir / "case.md"
    case_file = case_dir / "case.md"
    if not case_file.exists() and not case_file.exists():
        print(f"\nError: case.md (or case.md) not found in {case_dir}")
        valid = False

    # Check Linear integration (optional but show status)
    if is_linear_enabled():
        print("Linear integration: ENABLED")
        # Show Linear project status if initialized
        project_dir = (
            case_dir.parent.parent
        )  # .auto-sleuth/cases/001-name -> project root
        linear_manager = LinearManager(case_dir, project_dir)
        if linear_manager.is_initialized:
            summary = linear_manager.get_progress_summary()
            print(f"  Project: {summary.get('project_name', 'Unknown')}")
            print(
                f"  Issues: {summary.get('mapped_subtasks', 0)}/{summary.get('total_subtasks', 0)} mapped"
            )
        else:
            print("  Status: Will be initialized during planner session")
    else:
        print("Linear integration: DISABLED (set LINEAR_API_KEY to enable)")

    # Check Graphiti integration (optional but show status)
    graphiti_status = get_graphiti_status()
    if graphiti_status["available"]:
        print("Graphiti memory: ENABLED")
        print(f"  Database: {graphiti_status['database']}")
        if graphiti_status.get("db_path"):
            print(f"  Path: {graphiti_status['db_path']}")
    elif graphiti_status["enabled"]:
        print(
            f"Graphiti memory: CONFIGURED but unavailable ({graphiti_status['reason']})"
        )
    else:
        print("Graphiti memory: DISABLED (set GRAPHITI_ENABLED=true to enable)")

    print()
    return valid


def print_banner() -> None:
    """Print the Auto-Sleuth banner."""
    content = [
        bold(f"{icon(Icons.LIGHTNING)} AUTO-SLEUTH DFIR FRAMEWORK"),
        "",
        "Autonomous Multi-Session DFIR Agent",
        muted("Subtask-Based Investigation with Phase Dependencies"),
    ]
    print()
    print(box(content, width=70, style="heavy"))


def get_project_dir(provided_dir: Path | None) -> Path:
    """
    Determine the project directory.

    Args:
        provided_dir: User-provided project directory (or None)

    Returns:
        Resolved project directory path
    """
    if provided_dir:
        return provided_dir.resolve()

    project_dir = Path.cwd()

    # Auto-detect if running from within apps/backend directory (the source code)
    if project_dir.name == "backend" and (project_dir / "run.py").exists():
        # Running from within apps/backend/ source directory, go up 2 levels
        project_dir = project_dir.parent.parent

    return project_dir
