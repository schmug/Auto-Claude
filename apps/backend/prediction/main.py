#!/usr/bin/env python3
"""
Predictive Bug Prevention - CLI Entry Point
============================================

Command-line interface for the bug prediction system.

Usage:
    python prediction.py <case-dir> [--demo]
    python prediction.py auto-sleuth/cases/001-feature/
"""

import json
import sys
from pathlib import Path

from prediction import generate_subtask_checklist


def main():
    """Main entry point for CLI."""
    if len(sys.argv) < 2:
        print("Usage: python prediction.py <case-dir> [--demo]")
        print("       python prediction.py auto-sleuth/cases/001-feature/")
        sys.exit(1)

    case_dir = Path(sys.argv[1])

    if "--demo" in sys.argv:
        # Demo with sample analysis task
        demo_subtask = {
            "id": "avatar-endpoint",
            "description": "POST /api/users/avatar endpoint for uploading user avatars",
            "evidence_source": "backend",
            "artifacts_to_analyze": ["app/routes/users.py"],
            "artifacts_to_produce": [],
            "reference_patterns": ["app/routes/profile.py"],
            "validation": {
                "type": "api",
                "method": "POST",
                "url": "/api/users/avatar",
                "expect_status": 200,
            },
        }

        checklist_md = generate_subtask_checklist(case_dir, demo_subtask)
        print(checklist_md)
    else:
        # Load from implementation plan
        plan_file = case_dir / "investigation_plan.json"
        if not plan_file.exists():
            print(f"Error: No investigation_plan.json found in {case_dir}")
            sys.exit(1)

        with open(plan_file) as f:
            plan = json.load(f)

        # Find first pending task
        subtask = None
        for phase in plan.get("phases", []):
            tasks = phase.get("analysis_tasks")
            if not isinstance(tasks, list):
                tasks = phase.get("subtasks", []) or []
            for c in tasks:
                if c.get("status") == "pending":
                    subtask = c
                    break
            if subtask:
                break

        if not subtask:
            print("No pending tasks found")
            sys.exit(0)

        # Generate checklist
        checklist_md = generate_subtask_checklist(case_dir, subtask)
        print(checklist_md)


if __name__ == "__main__":
    main()
