"""
Case Writing Module
===================

Case document creation and validation.
"""

import json
from datetime import datetime
from pathlib import Path


def create_minimal_plan(case_dir: Path, task_description: str) -> Path:
    """Create a minimal investigation plan for simple tasks."""
    plan = {
        "case_name": case_dir.name,
        "case_id": case_dir.name,
        "investigation_type": "simple",
        "total_phases": 1,
        "recommended_workers": 1,
        "phases": [
            {
                "phase": 1,
                "id": "phase-1-simple",
                "name": "Implementation",
                "description": task_description or "Simple implementation",
                "depends_on": [],
                "analysis_tasks": [
                    {
                        "id": "task-1-1",
                        "description": task_description or "Implement the change",
                        "status": "pending",
                        "validation": {
                            "type": "manual",
                            "instructions": "Verify the change works as expected",
                        },
                    }
                ],
            }
        ],
        "metadata": {
            "created_at": datetime.now().isoformat(),
            "complexity": "simple",
            "estimated_sessions": 1,
        },
    }

    plan_file = case_dir / "investigation_plan.json"
    with open(plan_file, "w") as f:
        json.dump(plan, f, indent=2)

    return plan_file


def get_plan_stats(case_dir: Path) -> dict:
    """Get statistics from implementation plan if available."""
    plan_file = case_dir / "investigation_plan.json"
    if not plan_file.exists():
        return {}

    try:
        with open(plan_file) as f:
            plan_data = json.load(f)
        total_subtasks = 0
        for phase in plan_data.get("phases", []):
            tasks = phase.get("analysis_tasks")
            if isinstance(tasks, list):
                total_subtasks += len(tasks)
        return {
            "total_subtasks": total_subtasks,
            "total_phases": len(plan_data.get("phases", [])),
        }
    except Exception:
        return {}
