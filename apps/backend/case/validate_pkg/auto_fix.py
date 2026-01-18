"""
Auto-Fix Utilities
==================

Automated fixes for common implementation plan issues.
"""

import json
from pathlib import Path


def auto_fix_plan(case_dir: Path) -> bool:
    """Attempt to auto-fix common investigation_plan.json issues.

    Args:
        case_dir: Path to the case directory

    Returns:
        True if fixes were applied, False otherwise
    """
    plan_file = case_dir / "investigation_plan.json"

    if not plan_file.exists():
        return False

    try:
        with open(plan_file) as f:
            plan = json.load(f)
    except json.JSONDecodeError:
        return False

    fixed = False

    # Fix missing top-level fields
    if "case_name" not in plan:
        plan["case_name"] = case_dir.name
        fixed = True

    if "case_id" not in plan:
        plan["case_id"] = case_dir.name
        fixed = True

    if "investigation_type" not in plan:
        plan["investigation_type"] = "investigation"
        fixed = True

    if "phases" not in plan:
        plan["phases"] = []
        fixed = True

    # Fix phases
    for i, phase in enumerate(plan.get("phases", [])):
        if "phase" not in phase and "id" not in phase:
            phase["phase"] = i + 1
            fixed = True

        if "name" not in phase:
            phase["name"] = f"Phase {i + 1}"
            fixed = True

        if "analysis_tasks" not in phase:
            phase["analysis_tasks"] = []
            fixed = True

        # Fix tasks
        for j, task in enumerate(phase.get("analysis_tasks", [])):
            if "id" not in task:
                task["id"] = f"task-{i + 1}-{j + 1}"
                fixed = True

            if "description" not in task:
                task["description"] = "No description"
                fixed = True

            if "status" not in task:
                task["status"] = "pending"
                fixed = True

    if fixed:
        with open(plan_file, "w") as f:
            json.dump(plan, f, indent=2)
        print(f"Auto-fixed: {plan_file}")

    return fixed
