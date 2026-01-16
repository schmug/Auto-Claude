"""
Prompt Generator
================

Generates minimal, focused prompts for each subtask.
Instead of a 900-line mega-prompt, each subtask gets a tailored ~100-line prompt
with only the context it needs.

This approach:
- Reduces token usage by ~80%
- Keeps the agent focused on ONE task
- Moves bookkeeping to Python orchestration
"""

import json
from pathlib import Path


def get_relative_case_path(case_dir: Path, project_dir: Path) -> str:
    """
    Get the case directory path relative to the project/working directory.

    This ensures the AI gets a usable path regardless of absolute locations.

    Args:
        case_dir: Absolute path to case directory
        project_dir: Absolute path to project/working directory

    Returns:
        Relative path string (e.g., "./auto-sleuth/cases/003-new-case")
    """
    try:
        # Try to make path relative to project_dir
        relative = case_dir.relative_to(project_dir)
        return f"./{relative}"
    except ValueError:
        # If case_dir is not under project_dir, return the name only
        # This shouldn't happen if workspace.py correctly copies case files
        return f"./auto-sleuth/cases/{case_dir.name}"


def generate_environment_context(project_dir: Path, case_dir: Path) -> str:
    """
    Generate environment context header for prompts.

    This explicitly tells the AI where it is working, preventing path confusion.

    Args:
        project_dir: The working directory for the AI
        case_dir: The case directory (may be absolute or relative)

    Returns:
        Markdown string with environment context
    """
    relative_case = get_relative_case_path(case_dir, project_dir)

    case_file_name = "case.md" if (case_dir / "case.md").exists() else "case.md"

    return f"""## YOUR ENVIRONMENT

**Working Directory:** `{project_dir}`
**Case Location:** `{relative_case}/`

Your filesystem is restricted to your working directory. All file paths should be
relative to this location. Do NOT use absolute paths.

**⚠️ CRITICAL:** Before ANY git command or file operation, run `pwd` to verify your current
directory. If you've used `cd` to change directories, you MUST use paths relative to your
NEW location, not the working directory. See the PATH CONFUSION PREVENTION section in the
coder prompt for detailed examples.

**Important Files:**
- Case: `{relative_case}/{case_file_name}`
- Plan: `{relative_case}/investigation_plan.json`
- Progress: `{relative_case}/build-progress.txt`
- Context: `{relative_case}/context.json`

---

"""


def generate_subtask_prompt(
    case_dir: Path,
    project_dir: Path,
    subtask: dict,
    phase: dict,
    attempt_count: int = 0,
    recovery_hints: list[str] | None = None,
) -> str:
    """
    Generate a minimal, focused prompt for implementing a single subtask.

    Args:
        case_dir: Directory containing case files
        project_dir: Root project directory (working directory)
        subtask: The subtask to implement
        phase: The phase containing this subtask
        attempt_count: Number of previous attempts (for retry context)
        recovery_hints: Hints from previous failed attempts

    Returns:
        A focused prompt string (~100 lines instead of 900)
    """
    subtask_id = subtask.get("id", "unknown")
    description = subtask.get("description", "No description")
    service = subtask.get("service", "all")
    files_to_modify = subtask.get("files_to_modify", [])
    files_to_create = subtask.get("files_to_create", [])
    patterns_from = subtask.get("patterns_from", [])
    verification = subtask.get("verification", {})

    # Get relative case path
    relative_case = get_relative_case_path(case_dir, project_dir)

    # Build the prompt
    sections = []

    # Environment context first
    sections.append(generate_environment_context(project_dir, case_dir))

    # Header
    sections.append(f"""# Subtask Implementation Task

**Subtask ID:** `{subtask_id}`
**Phase:** {phase.get("name", phase.get("id", "Unknown"))}
**Service:** {service}

## Description

{description}
""")

    # Recovery context if this is a retry
    if attempt_count > 0:
        sections.append(f"""
## ⚠️ RETRY ATTEMPT ({attempt_count + 1})

This subtask has been attempted {attempt_count} time(s) before without success.
You MUST use a DIFFERENT approach than previous attempts.
""")
        if recovery_hints:
            sections.append("**Previous attempt insights:**")
            for hint in recovery_hints:
                sections.append(f"- {hint}")
            sections.append("")

    # Files section
    sections.append("## Files\n")

    if files_to_modify:
        sections.append("**Files to Modify:**")
        for f in files_to_modify:
            sections.append(f"- `{f}`")
        sections.append("")

    if files_to_create:
        sections.append("**Files to Create:**")
        for f in files_to_create:
            sections.append(f"- `{f}`")
        sections.append("")

    if patterns_from:
        sections.append("**Pattern Files (study these first):**")
        for f in patterns_from:
            sections.append(f"- `{f}`")
        sections.append("")

    # Verification
    sections.append("## Verification\n")
    v_type = verification.get("type", "manual")

    if v_type == "command":
        sections.append(f"""Run this command to verify:
```bash
{verification.get("command", 'echo "No command caseified"')}
```
Expected: {verification.get("expected", "Success")}
""")
    elif v_type == "api":
        method = verification.get("method", "GET")
        url = verification.get("url", "http://localhost")
        body = verification.get("body", {})
        expected_status = verification.get("expected_status", 200)
        sections.append(f"""Test the API endpoint:
```bash
curl -X {method} {url} -H "Content-Type: application/json" {f"-d '{json.dumps(body)}'" if body else ""}
```
Expected status: {expected_status}
""")
    elif v_type == "browser":
        url = verification.get("url", "http://localhost:3000")
        checks = verification.get("checks", [])
        sections.append(f"""Open in browser: {url}

Verify:""")
        for check in checks:
            sections.append(f"- [ ] {check}")
        sections.append("")
    elif v_type == "e2e":
        steps = verification.get("steps", [])
        sections.append("End-to-end verification steps:")
        for i, step in enumerate(steps, 1):
            sections.append(f"{i}. {step}")
        sections.append("")
    else:
        instructions = verification.get("instructions", "Manual verification required")
        sections.append(f"**Manual Verification:**\n{instructions}\n")

    # Instructions
    sections.append(f"""## Instructions

1. **Read the pattern files** to understand code style and conventions
2. **Read the files to modify** (if any) to understand current implementation
3. **Implement the subtask** following the patterns exactly
4. **Run verification** and fix any issues
5. **Commit your changes:**
   ```bash
   git add .
   git commit -m "auto-sleuth: {subtask_id} - {description[:50]}"
   ```
6. **Update the plan** - set this subtask's status to "completed" in investigation_plan.json

## Quality Checklist

Before marking complete, verify:
- [ ] Follows patterns from reference files
- [ ] No console.log/print debugging statements
- [ ] Error handling in place
- [ ] Verification passes
- [ ] Clean commit with descriptive message

## Important

- Focus ONLY on this subtask - don't modify unrelated code
- If verification fails, FIX IT before committing
- If you encounter a blocker, document it in build-progress.txt
""")

    # Note: Linear updates are now handled by Python orchestrator via linear_updater.py
    # Agents no longer need to call Linear MCP tools directly

    return "\n".join(sections)


def generate_planner_prompt(case_dir: Path, project_dir: Path | None = None) -> str:
    """
    Generate the planner prompt (used only once at start).
    This is a simplified version that focuses on plan creation.

    Args:
        case_dir: Directory containing case.md
        project_dir: Working directory (for relative paths)

    Returns:
        Planner prompt string
    """
    # Load the full planner prompt from file
    prompts_dir = Path(__file__).parent / "prompts"
    planner_file = prompts_dir / "planner.md"

    case_file_name = "case.md" if (case_dir / "case.md").exists() else "case.md"
    
    if planner_file.exists():
        prompt = planner_file.read_text()
    else:
        prompt = (
            f"Read {case_file_name} and create investigation_plan.json with phases and subtasks."
        )

    # Use project_dir for relative paths, or infer from case_dir
    if project_dir is None:
        # Infer: case_dir is typically project/auto-sleuth/cases/XXX
        project_dir = case_dir.parent.parent.parent

    # Get relative path for case directory
    relative_case = get_relative_case_path(case_dir, project_dir)

    # Build header with environment context
    header = generate_environment_context(project_dir, case_dir)

    # Add case-caseific instructions
    header += f"""## SPEC LOCATION

Your case file is located at: `{relative_case}/{case_file_name}`

Store all build artifacts in this case directory:
- `{relative_case}/investigation_plan.json` - Subtask-based implementation plan
- `{relative_case}/build-progress.txt` - Progress notes
- `{relative_case}/init.sh` - Environment setup script

The project root is your current working directory. Implement code in the project root,
not in the case directory.

---

"""
    # Note: Linear task creation and updates are now handled by Python orchestrator
    # via linear_updater.py - agents no longer need Linear instructions in prompts

    return header + prompt


def load_subtask_context(
    case_dir: Path,
    project_dir: Path,
    subtask: dict,
    max_file_lines: int = 200,
) -> dict:
    """
    Load minimal context needed for a subtask.

    Args:
        case_dir: Case directory
        project_dir: Project root
        subtask: The subtask being implemented
        max_file_lines: Maximum lines to include per file

    Returns:
        Dict with file contents and relevant context
    """
    context = {
        "patterns": {},
        "files_to_modify": {},
        "case_excerpt": None,
    }

    # Load pattern files (truncated)
    for pattern_path in subtask.get("patterns_from", []):
        full_path = project_dir / pattern_path
        if full_path.exists():
            try:
                lines = full_path.read_text().split("\n")
                if len(lines) > max_file_lines:
                    content = "\n".join(lines[:max_file_lines])
                    content += (
                        f"\n\n... (truncated, {len(lines) - max_file_lines} more lines)"
                    )
                else:
                    content = "\n".join(lines)
                context["patterns"][pattern_path] = content
            except Exception:
                context["patterns"][pattern_path] = "(Could not read file)"

    # Load files to modify (truncated)
    for file_path in subtask.get("files_to_modify", []):
        full_path = project_dir / file_path
        if full_path.exists():
            try:
                lines = full_path.read_text().split("\n")
                if len(lines) > max_file_lines:
                    content = "\n".join(lines[:max_file_lines])
                    content += (
                        f"\n\n... (truncated, {len(lines) - max_file_lines} more lines)"
                    )
                else:
                    content = "\n".join(lines)
                context["files_to_modify"][file_path] = content
            except Exception:
                context["files_to_modify"][file_path] = "(Could not read file)"

    return context


def format_context_for_prompt(context: dict) -> str:
    """
    Format loaded context into a prompt section.

    Args:
        context: Dict from load_subtask_context

    Returns:
        Formatted string to append to prompt
    """
    sections = []

    if context.get("patterns"):
        sections.append("## Reference Files (Patterns to Follow)\n")
        for path, content in context["patterns"].items():
            sections.append(f"### `{path}`\n```\n{content}\n```\n")

    if context.get("files_to_modify"):
        sections.append("## Current File Contents (To Modify)\n")
        for path, content in context["files_to_modify"].items():
            sections.append(f"### `{path}`\n```\n{content}\n```\n")

    return "\n".join(sections)
