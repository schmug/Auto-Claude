"""
Plan generation logic for different investigation types.
"""

from pathlib import Path

from investigation_plan import (
    InvestigationPlan,
    InvestigationPhase,
    InvestigationPhaseType,
    InvestigationStep,
    InvestigationStepStatus,
)

from .models import PlannerContext
from .utils import (
    create_verification,
    determine_service_order,
    extract_acceptance_criteria,
    extract_case_name,
    get_patterns_for_service,
    group_files_by_service,
    infer_subtask_type,
)


class PlanGenerator:
    """Base class for plan generators."""

    def __init__(self, context: PlannerContext, case_dir: Path):
        self.context = context
        self.case_dir = case_dir

    def generate(self) -> InvestigationPlan:
        """Generate investigation plan. Override in subclasses."""
        raise NotImplementedError


class FeaturePlanGenerator(PlanGenerator):
    """Generates analysis plans for triage-style tasks."""

    def generate(self) -> InvestigationPlan:
        """Generate a plan based on file-level context."""
        case_name = extract_case_name(self.context)
        case_id = self.case_dir.name
        files_by_service = group_files_by_service(self.context)

        phases = []
        phase_num = 0

        # Determine service order (backend first, then workers, then frontend)
        service_order = determine_service_order(files_by_service)

        backend_phase = None

        for service in service_order:
            files = files_by_service[service]
            if not files:
                continue

            phase_num += 1
            patterns = get_patterns_for_service(self.context, service)

            steps = []
            for file_info in files:
                path = file_info.get("path", "")
                reason = file_info.get("reason", "")

                subtask_type = infer_subtask_type(path)
                subtask_id = Path(path).stem.replace(".", "-").lower()

                steps.append(
                    InvestigationStep(
                        id=f"{service}-{subtask_id}",
                        description=f"Modify {path}: {reason}"
                        if reason
                        else f"Update {path}",
                        evidence_source=service,
                        artifacts_to_analyze=[path] if path else [],
                        reference_patterns=patterns,
                        validation=create_verification(
                            self.context, service, subtask_type
                        ),
                    )
                )

            depends_on = []
            service_type = (
                self.context.project_index.get("services", {})
                .get(service, {})
                .get("type", "")
            )

            if service_type in ["worker", "celery", "jobs"] and backend_phase:
                depends_on = [backend_phase]
            elif service_type in ["frontend", "web", "client", "ui"] and backend_phase:
                depends_on = [backend_phase]

            phases.append(
                InvestigationPhase(
                    phase=phase_num,
                    name=f"{service.title()} Analysis",
                    phase_type=InvestigationPhaseType.ANALYSIS,
                    steps=steps,
                    depends_on=depends_on,
                    parallel_safe=len(steps) > 1,
                )
            )

            if service_type in ["backend", "api", "server"]:
                backend_phase = phase_num

        # Add integration/validation phase if multiple services
        if len(service_order) > 1:
            phase_num += 1
            integration_depends = list(range(1, phase_num))

            phases.append(
                InvestigationPhase(
                    phase=phase_num,
                    name="Cross-Service Validation",
                    phase_type=InvestigationPhaseType.VALIDATION,
                    depends_on=integration_depends,
                    steps=[
                        InvestigationStep(
                            id="integration-wiring",
                            description="Validate service boundaries and interfaces",
                            analysis_type="integration",
                            validation={
                                "type": "browser",
                                "scenario": "End-to-end flow works",
                            },
                        ),
                        InvestigationStep(
                            id="integration-testing",
                            description="Verify acceptance criteria across services",
                            analysis_type="integration",
                            validation={
                                "type": "browser",
                                "scenario": "All acceptance criteria met",
                            },
                        ),
                    ],
                )
            )

        final_acceptance = extract_acceptance_criteria(self.context)

        return InvestigationPlan(
            case_id=case_id,
            case_name=case_name,
            investigation_type=self.context.investigation_type,
            description=self.context.task_context.get("task_description", ""),
            phases=phases,
            final_acceptance=final_acceptance,
            evidence_sources=self.context.evidence_sources,
            case_file=str(self.case_dir / "case.md"),
        )


class InvestigationPlanGenerator(PlanGenerator):
    """Generates investigation plans for debugging."""

    def generate(self) -> InvestigationPlan:
        """Generate an investigation plan for debugging."""
        case_name = extract_case_name(self.context)
        case_id = self.case_dir.name

        phases = [
            InvestigationPhase(
                phase=1,
                name="Reproduce & Instrument",
                phase_type=InvestigationPhaseType.ANALYSIS,
                steps=[
                    InvestigationStep(
                        id="add-logging",
                        description="Add detailed logging around suspected problem areas",
                        artifacts_to_analyze=[
                            f.get("path", "")
                            for f in self.context.files_to_modify[:3]
                            if f.get("path")
                        ],
                    ),
                    InvestigationStep(
                        id="create-repro",
                        description="Create reliable reproduction steps",
                        analysis_type="investigation",
                    ),
                ],
            ),
            InvestigationPhase(
                phase=2,
                name="Investigate & Analyze",
                phase_type=InvestigationPhaseType.ANALYSIS,
                depends_on=[1],
                steps=[
                    InvestigationStep(
                        id="analyze-logs",
                        description="Analyze logs from multiple reproductions",
                        analysis_type="investigation",
                    ),
                    InvestigationStep(
                        id="form-hypothesis",
                        description="Form and test hypotheses about root cause",
                        analysis_type="investigation",
                    ),
                ],
            ),
            InvestigationPhase(
                phase=3,
                name="Implement Fix",
                phase_type=InvestigationPhaseType.REMEDIATION,
                depends_on=[2],
                steps=[
                    InvestigationStep(
                        id="implement-fix",
                        description="[TO BE DETERMINED: Fix based on investigation findings]",
                        status=InvestigationStepStatus.BLOCKED,
                    ),
                    InvestigationStep(
                        id="add-regression-test",
                        description="Add test to prevent issue from recurring",
                        status=InvestigationStepStatus.BLOCKED,
                    ),
                ],
            ),
            InvestigationPhase(
                phase=4,
                name="Verify & Harden",
                phase_type=InvestigationPhaseType.VALIDATION,
                depends_on=[3],
                steps=[
                    InvestigationStep(
                        id="verify-fix",
                        description="Verify issue no longer occurs",
                        validation={
                            "type": "manual",
                            "scenario": "Run reproduction steps - issue should not occur",
                        },
                    ),
                    InvestigationStep(
                        id="add-monitoring",
                        description="Add alerting/monitoring to catch if issue returns",
                    ),
                ],
            ),
        ]

        return InvestigationPlan(
            case_id=case_id,
            case_name=case_name,
            investigation_type=self.context.investigation_type,
            description=self.context.task_context.get("task_description", ""),
            phases=phases,
            final_acceptance=[
                "Issue no longer reproducible",
                "Root cause documented",
                "Regression test in place",
            ],
            evidence_sources=self.context.evidence_sources,
            case_file=str(self.case_dir / "case.md"),
        )


class RefactorPlanGenerator(PlanGenerator):
    """Generates refactor plans with stage-based phases."""

    def generate(self) -> InvestigationPlan:
        """Generate a refactor plan with stage-based phases."""
        case_name = extract_case_name(self.context)
        case_id = self.case_dir.name

        phases = [
            InvestigationPhase(
                phase=1,
                name="Add New System",
                phase_type=InvestigationPhaseType.ANALYSIS,
                steps=[
                    InvestigationStep(
                        id="add-new-implementation",
                        description="Implement new system alongside existing",
                        artifacts_to_analyze=[
                            f.get("path", "") for f in self.context.files_to_modify
                        ],
                        reference_patterns=[
                            f.get("path", "")
                            for f in self.context.files_to_reference[:3]
                            if f.get("path")
                        ],
                        validation={
                            "type": "command",
                            "run": "echo 'New system added - both old and new should work'",
                        },
                    ),
                ],
            ),
            InvestigationPhase(
                phase=2,
                name="Migrate Consumers",
                phase_type=InvestigationPhaseType.ANALYSIS,
                depends_on=[1],
                steps=[
                    InvestigationStep(
                        id="migrate-to-new",
                        description="Update consumers to use new system",
                        validation={
                            "type": "browser",
                            "scenario": "All functionality works with new system",
                        },
                    ),
                ],
            ),
            InvestigationPhase(
                phase=3,
                name="Remove Old System",
                phase_type=InvestigationPhaseType.REMEDIATION,
                depends_on=[2],
                steps=[
                    InvestigationStep(
                        id="remove-old",
                        description="Remove old system code",
                        validation={
                            "type": "command",
                            "run": "echo 'Old system removed - verify no references remain'",
                        },
                    ),
                ],
            ),
            InvestigationPhase(
                phase=4,
                name="Polish",
                phase_type=InvestigationPhaseType.VALIDATION,
                depends_on=[3],
                steps=[
                    InvestigationStep(
                        id="cleanup",
                        description="Final cleanup and documentation",
                    ),
                    InvestigationStep(
                        id="verify-complete",
                        description="Verify refactor is complete",
                        validation={
                            "type": "browser",
                            "scenario": "All functionality works, no regressions",
                        },
                    ),
                ],
            ),
        ]

        return InvestigationPlan(
            case_id=case_id,
            case_name=case_name,
            investigation_type=self.context.investigation_type,
            description=self.context.task_context.get("task_description", ""),
            phases=phases,
            final_acceptance=[
                "All functionality migrated to new system",
                "Old system completely removed",
                "No regressions in existing functionality",
            ],
            evidence_sources=self.context.evidence_sources,
            case_file=str(self.case_dir / "case.md"),
        )


def get_plan_generator(context: PlannerContext, case_dir: Path) -> PlanGenerator:
    """Factory function to get the appropriate plan generator."""
    investigation_type = (context.investigation_type or "").lower()
    if investigation_type in {
        "investigation",
        "intrusion",
        "malware",
        "insider_threat",
        "data_breach",
        "triage",
        "incident_response",
        "incident_analysis",
        "ransomware",
        "phishing",
        "threat_hunting",
    }:
        return InvestigationPlanGenerator(context, case_dir)
    if investigation_type == "refactor":
        return RefactorPlanGenerator(context, case_dir)
    return FeaturePlanGenerator(context, case_dir)
