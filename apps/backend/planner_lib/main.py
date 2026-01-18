#!/usr/bin/env python3
"""
Investigation Planner
======================

Generates implementation plans from cases by analyzing the task and codebase.
This replaces the initializer's test-generation with subtask-based planning.

The planner:
1. Reads the case.md to understand what needs to be analyzed
2. Reads project_index.json to understand the codebase structure
3. Reads context.json to know which files are relevant
4. Determines the investigation type (intrusion, malware, triage, etc.)
5. Generates phases and analysis tasks with proper dependencies
6. Outputs investigation_plan.json

Usage:
    python auto-sleuth/planner.py --case-dir auto-sleuth/cases/001-feature/
"""

import json
from pathlib import Path

from investigation_plan import InvestigationPlan
from planner_lib.context import ContextLoader
from planner_lib.generators import get_plan_generator


class InvestigationPlanner:
    """Generates implementation plans from cases."""

    def __init__(self, case_dir: Path):
        self.case_dir = case_dir
        self.context_loader = ContextLoader(case_dir)
        self.context = None

    def load_context(self):
        """Load all context files from case directory."""
        self.context = self.context_loader.load_context()
        return self.context

    def generate_plan(self) -> InvestigationPlan:
        """Generate the appropriate plan based on workflow type."""
        if not self.context:
            self.load_context()

        generator = get_plan_generator(self.context, self.case_dir)
        return generator.generate()

    def save_plan(self, plan: InvestigationPlan) -> Path:
        """Save plan to case directory."""
        output_path = self.case_dir / "investigation_plan.json"
        plan.save(output_path)
        print(f"Investigation plan saved to: {output_path}")
        return output_path


def generate_investigation_plan(case_dir: Path) -> InvestigationPlan:
    """Main entry point for generating an implementation plan."""
    planner = InvestigationPlanner(case_dir)
    planner.load_context()
    plan = planner.generate_plan()
    planner.save_plan(plan)
    return plan


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate investigation plan from case"
    )
    parser.add_argument(
        "--case-dir",
        type=Path,
        required=True,
        help="Directory containing case.md, project_index.json, context.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output path for investigation_plan.json (default: case-dir/investigation_plan.json)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print plan without saving",
    )

    args = parser.parse_args()

    planner = InvestigationPlanner(args.case_dir)
    planner.load_context()
    plan = planner.generate_plan()

    if args.dry_run:
        print(json.dumps(plan.to_dict(), indent=2))
        print("\n---\n")
        print(plan.get_status_summary())
    else:
        output_path = args.output or (args.case_dir / "investigation_plan.json")
        plan.save(output_path)
        print(f"Plan saved to: {output_path}")
        print("\n" + plan.get_status_summary())


if __name__ == "__main__":
    main()
