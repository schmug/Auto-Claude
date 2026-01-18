"""
Case Writing and Critique Phase Implementations
================================================

Phases for case document creation and quality assurance.
"""

import json
from typing import TYPE_CHECKING

from .. import validator, writer
from .models import MAX_RETRIES, PhaseResult

if TYPE_CHECKING:
    pass


class CasePhaseMixin:
    """Mixin for case writing and critique phase methods."""

    async def phase_quick_case(self) -> PhaseResult:
        """Quick case for simple tasks - combines context and case in one step."""
        case_file = self.case_dir / "case.md"
        spec_file = self.case_dir / "spec.md"  # Legacy alternative
        plan_file = self.case_dir / "investigation_plan.json"

        # Check for either case.md or spec.md (DFIR uses case.md)
        doc_file = case_file if case_file.exists() else spec_file

        if doc_file.exists() and plan_file.exists():
            self.ui.print_status("Quick investigation case already exists", "success")
            return PhaseResult(
                "quick_case", True, [str(doc_file), str(plan_file)], [], 0
            )

        errors = []
        for attempt in range(MAX_RETRIES):
            self.ui.print_status(
                f"Running quick case agent (attempt {attempt + 1})...", "progress"
            )

            context_str = f"""
**Task**: {self.task_description}
**Case Directory**: {self.case_dir}
**Complexity**: SIMPLE (1-2 files expected)

This is a SIMPLE task. Create a minimal case definition and investigation plan directly.
No research or extensive analysis needed.

Create:
1. A concise case.md (or spec.md) with just the essential sections
2. A simple investigation_plan.json with 1-2 analysis tasks
"""
            success, output = await self.run_agent_fn(
                "case_quick.md",
                additional_context=context_str,
                phase_name="quick_case",
            )

            # Check for either case.md or spec.md
            doc_file = case_file if case_file.exists() else spec_file

            if success and doc_file.exists():
                # Create minimal plan if agent didn't
                if not plan_file.exists():
                    writer.create_minimal_plan(self.case_dir, self.task_description)

                self.ui.print_status("Quick case created", "success")
                return PhaseResult(
                    "quick_case", True, [str(doc_file), str(plan_file)], [], attempt
                )

            errors.append(f"Attempt {attempt + 1}: Quick case agent failed")

        return PhaseResult("quick_case", False, [], errors, MAX_RETRIES)

    async def phase_case_writing(self) -> PhaseResult:
        """Write the case.md or spec.md document (DFIR workflows use case.md)."""
        case_file = self.case_dir / "case.md"
        spec_file = self.case_dir / "spec.md"  # Legacy alternative

        # Check for either case.md or spec.md (DFIR uses case.md)
        output_file = case_file if case_file.exists() else spec_file
        
        if output_file.exists():
            result = self.case_validator.validate_case_document()
            if result.valid:
                self.ui.print_status(f"{output_file.name} already exists and is valid", "success")
                return PhaseResult("case_writing", True, [str(output_file)], [], 0)
            self.ui.print_status(
                f"{output_file.name} exists but has issues, regenerating...", "warning"
            )

        errors = []
        for attempt in range(MAX_RETRIES):
            self.ui.print_status(
                f"Running case writer (attempt {attempt + 1})...", "progress"
            )

            success, output = await self.run_agent_fn(
                "case_writer.md",
                phase_name="case_writing",
            )

            # Check for either case.md or spec.md (DFIR workflows use case.md)
            output_file = case_file if case_file.exists() else spec_file
            
            if success and output_file.exists():
                result = self.case_validator.validate_case_document()
                if result.valid:
                    self.ui.print_status(f"Created valid {output_file.name}", "success")
                    return PhaseResult(
                        "case_writing", True, [str(output_file)], [], attempt
                    )
                else:
                    errors.append(
                        f"Attempt {attempt + 1}: Case invalid - {result.errors}"
                    )
                    self.ui.print_status(
                        f"Case created but invalid: {result.errors}", "error"
                    )
            else:
                errors.append(f"Attempt {attempt + 1}: Agent did not create case.md or spec.md")

        return PhaseResult("case_writing", False, [], errors, MAX_RETRIES)

    async def phase_self_critique(self) -> PhaseResult:
        """Self-critique the case using extended thinking."""
        case_file = self.case_dir / "case.md"
        spec_file = self.case_dir / "spec.md"  # Legacy alternative
        research_file = self.case_dir / "research.json"
        critique_file = self.case_dir / "critique_report.json"

        # Check for either case.md or spec.md (DFIR uses case.md)
        output_file = case_file if case_file.exists() else spec_file

        if not output_file.exists():
            self.ui.print_status(f"No {output_file.name} to critique", "error")
            return PhaseResult(
                "self_critique", False, [], [f"{output_file.name} does not exist"], 0
            )

        if critique_file.exists():
            with open(critique_file) as f:
                critique = json.load(f)
                if critique.get("issues_fixed", False) or critique.get(
                    "no_issues_found", False
                ):
                    self.ui.print_status("Self-critique already completed", "success")
                    return PhaseResult(
                        "self_critique", True, [str(critique_file)], [], 0
                    )

        errors = []
        for attempt in range(MAX_RETRIES):
            self.ui.print_status(
                f"Running self-critique agent (attempt {attempt + 1})...", "progress"
            )

            context_str = f"""
**Case File**: {output_file}
**Research File**: {research_file}
**Critique Output**: {critique_file}

Use EXTENDED THINKING (ultrathink) to deeply analyze the {output_file.name}:

1. **Technical Accuracy**: Do findings match the research?
2. **Completeness**: Are all investigation objectives covered?
3. **Consistency**: Do names and patterns match throughout?
4. **Feasibility**: Is the analysis approach realistic?

For each issue found:
- Fix it directly in {output_file.name}
- Document what was fixed in critique_report.json

Output critique_report.json with:
{{
  "issues_found": [...],
  "issues_fixed": true/false,
  "no_issues_found": true/false,
  "critique_summary": "..."
}}
"""
            success, output = await self.run_agent_fn(
                "case_critic.md",
                additional_context=context_str,
                phase_name="self_critique",
            )

            if success:
                if not critique_file.exists():
                    validator.create_minimal_critique(
                        self.case_dir,
                        reason="Agent completed without explicit issues",
                    )

                result = self.case_validator.validate_case_document()
                if result.valid:
                    self.ui.print_status(
                        "Self-critique completed, case is valid", "success"
                    )
                    return PhaseResult(
                        "self_critique", True, [str(critique_file)], [], attempt
                    )
                else:
                    self.ui.print_status(
                        f"Case invalid after critique: {result.errors}", "warning"
                    )
                    errors.append(
                        f"Attempt {attempt + 1}: Case still invalid after critique"
                    )
            else:
                errors.append(f"Attempt {attempt + 1}: Critique agent failed")

        validator.create_minimal_critique(
            self.case_dir,
            reason="Critique failed after retries",
        )
        return PhaseResult(
            "self_critique", True, [str(critique_file)], errors, MAX_RETRIES
        )
