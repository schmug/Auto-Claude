"""
Planning and Validation Phase Implementations
==============================================

Phases for implementation planning and final validation.
"""

from typing import TYPE_CHECKING

from task_logger import LogEntryType, LogPhase

from .. import writer
from .models import MAX_RETRIES, PhaseResult

if TYPE_CHECKING:
    pass


class PlanningPhaseMixin:
    """Mixin for planning and validation phase methods."""

    async def phase_evidence_preprocessing(self) -> PhaseResult:
        """Preprocess evidence files before investigation planning (DFIR workflow).
        
        This phase runs the Evidence Preprocessor Agent to:
        - Detect evidence file formats (EVTX, PCAP, JSON, Zeek, etc.)
        - Calculate SHA256 hashes for chain of custody
        - Extract metadata (time ranges, record counts)
        - Create evidence_index.json for the Investigation Planner
        """
        evidence_index_file = self.case_dir / "evidence_index.json"
        evidence_dir = self.case_dir / "evidence"
        
        # Skip if no evidence directory
        if not evidence_dir.exists():
            self.ui.print_status(
                "No evidence directory found, skipping preprocessing", "info"
            )
            return PhaseResult("evidence_preprocessing", True, [], [], 0)
        
        # Skip if evidence_index already exists and is valid
        if evidence_index_file.exists():
            self.ui.print_status(
                "evidence_index.json already exists", "success"
            )
            return PhaseResult(
                "evidence_preprocessing", True, [str(evidence_index_file)], [], 0
            )
        
        errors = []
        
        self.ui.print_status("Running Evidence Preprocessor agent...", "progress")
        self.task_logger.log(
            "Preprocessing evidence files for investigation...",
            LogEntryType.INFO,
            LogPhase.PLANNING,
        )
        
        for attempt in range(MAX_RETRIES):
            self.ui.print_status(
                f"Evidence preprocessing (attempt {attempt + 1})...", "progress"
            )
            
            # Provide context about evidence directory
            evidence_files = list(evidence_dir.rglob("*"))
            file_list = "\n".join(f"- {f.relative_to(self.case_dir)}" for f in evidence_files if f.is_file())
            
            context = f"""
## Evidence Directory
Path: {evidence_dir}

## Files Found
{file_list}

## Task
1. Analyze each evidence file format
2. Calculate SHA256 hashes
3. Extract time ranges and record counts where possible
4. Create evidence_index.json with full catalog
5. Generate preprocessing_report.txt
"""
            
            success, output = await self.run_agent_fn(
                "evidence_preprocessor.md",
                additional_context=context,
                phase_name="evidence_preprocessing",
            )
            
            if success and evidence_index_file.exists():
                self.ui.print_status(
                    "Created evidence_index.json", "success"
                )
                self.task_logger.log(
                    f"Evidence preprocessing complete - index created",
                    LogEntryType.SUCCESS,
                    LogPhase.PLANNING,
                )
                return PhaseResult(
                    "evidence_preprocessing", True, [str(evidence_index_file)], [], attempt
                )
            else:
                errors.append(f"Attempt {attempt + 1}: Did not create evidence_index.json")
                self.ui.print_status(
                    f"Evidence preprocessing attempt {attempt + 1} failed", "warning"
                )
        
        # Allow pipeline to continue even if preprocessing fails
        self.ui.print_status(
            "Evidence preprocessing incomplete, continuing with planning...", "warning"
        )
        return PhaseResult("evidence_preprocessing", True, [], errors, MAX_RETRIES)

    async def phase_planning(self) -> PhaseResult:
        """Create the implementation plan."""
        from ..validate_pkg.auto_fix import auto_fix_plan

        plan_file = self.case_dir / "investigation_plan.json"

        if plan_file.exists():
            result = self.case_validator.validate_investigation_plan()
            if result.valid:
                self.ui.print_status(
                    "investigation_plan.json already exists and is valid", "success"
                )
                return PhaseResult("planning", True, [str(plan_file)], [], 0)
            self.ui.print_status("Plan exists but invalid, regenerating...", "warning")

        errors = []

        # Try Python script first (deterministic)
        self.ui.print_status("Trying planner.py (deterministic)...", "progress")
        success, output = self._run_script(
            "planner.py", ["--case-dir", str(self.case_dir)]
        )

        if success and plan_file.exists():
            result = self.case_validator.validate_investigation_plan()
            if result.valid:
                self.ui.print_status(
                    "Created valid investigation_plan.json via script", "success"
                )
                stats = writer.get_plan_stats(self.case_dir)
                if stats:
                    self.task_logger.log(
                        f"Investigation plan created with {stats.get('total_subtasks', 0)} tasks",
                        LogEntryType.SUCCESS,
                        LogPhase.PLANNING,
                    )
                return PhaseResult("planning", True, [str(plan_file)], [], 0)
            else:
                if auto_fix_plan(self.case_dir):
                    result = self.case_validator.validate_investigation_plan()
                    if result.valid:
                        self.ui.print_status(
                            "Auto-fixed investigation_plan.json", "success"
                        )
                        return PhaseResult("planning", True, [str(plan_file)], [], 0)
                errors.append(f"Script output invalid: {result.errors}")

        # Fall back to agent
        self.ui.print_status("Falling back to planner agent...", "progress")
        for attempt in range(MAX_RETRIES):
            self.ui.print_status(
                f"Running planner agent (attempt {attempt + 1})...", "progress"
            )

            success, output = await self.run_agent_fn(
                "planner.md",
                phase_name="planning",
            )

            if success and plan_file.exists():
                result = self.case_validator.validate_investigation_plan()
                if result.valid:
                    self.ui.print_status(
                        "Created valid investigation_plan.json via agent", "success"
                    )
                    return PhaseResult("planning", True, [str(plan_file)], [], attempt)
                else:
                    if auto_fix_plan(self.case_dir):
                        result = self.case_validator.validate_investigation_plan()
                        if result.valid:
                            self.ui.print_status(
                                "Auto-fixed investigation_plan.json", "success"
                            )
                            return PhaseResult(
                                "planning", True, [str(plan_file)], [], attempt
                            )
                    errors.append(f"Agent attempt {attempt + 1}: {result.errors}")
                    self.ui.print_status("Plan created but invalid", "error")
            else:
                errors.append(f"Agent attempt {attempt + 1}: Did not create plan file")

        return PhaseResult("planning", False, [], errors, MAX_RETRIES)

    async def phase_validation(self) -> PhaseResult:
        """Final validation of all case files with auto-fix retry."""
        for attempt in range(MAX_RETRIES):
            results = self.case_validator.validate_all()
            all_valid = all(r.valid for r in results)

            for result in results:
                if result.valid:
                    self.ui.print_status(f"{result.checkpoint}: PASS", "success")
                else:
                    self.ui.print_status(f"{result.checkpoint}: FAIL", "error")
                for err in result.errors:
                    print(f"    {self.ui.muted('Error:')} {err}")

            if all_valid:
                print()
                self.ui.print_status("All validation checks passed", "success")
                return PhaseResult("validation", True, [], [], attempt)

            # If not valid, try to auto-fix with AI agent
            if attempt < MAX_RETRIES - 1:
                print()
                self.ui.print_status(
                    f"Attempting auto-fix (attempt {attempt + 1}/{MAX_RETRIES - 1})...",
                    "progress",
                )

                # Collect all errors for the fixer agent
                error_details = []
                for result in results:
                    if not result.valid:
                        error_details.append(
                            f"**{result.checkpoint}** validation failed:"
                        )
                        for err in result.errors:
                            error_details.append(f"  - {err}")
                        if result.fixes:
                            error_details.append("  Suggested fixes:")
                            for fix in result.fixes:
                                error_details.append(f"    - {fix}")

                context_str = f"""
**Case Directory**: {self.case_dir}

## Validation Errors to Fix

{chr(10).join(error_details)}

## Files in Case Directory

The following files exist in the case directory:
- context.json
- requirements.json
- case.md
- investigation_plan.json
- project_index.json (if exists)

Read the failed files, understand the errors, and fix them.
"""
                success, output = await self.run_agent_fn(
                    "validation_fixer.md",
                    additional_context=context_str,
                    phase_name="validation",
                )

                if not success:
                    self.ui.print_status("Auto-fix agent failed", "warning")

        # All retries exhausted
        errors = [f"{r.checkpoint}: {err}" for r in results for err in r.errors]
        return PhaseResult("validation", False, [], errors, MAX_RETRIES)
