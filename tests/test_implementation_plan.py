#!/usr/bin/env python3
"""
Tests for Investigation Plan Management
=======================================

Covers core data structures and serialization for DFIR investigation plans.
"""

import json
from pathlib import Path

import pytest

from investigation_plan import (
    CaseType,
    InvestigationPhase,
    InvestigationPhaseType,
    InvestigationPlan,
    InvestigationPlanFactory,
    InvestigationStep,
    InvestigationStepStatus,
    Verification,
    VerificationType,
)


def make_plan(phases=None) -> InvestigationPlan:
    """Helper to create a minimal investigation plan."""
    return InvestigationPlan(
        case_id="case-001",
        case_name="Test Case",
        investigation_type="triage",
        phases=phases or [],
    )


class TestInvestigationStep:
    """Tests for InvestigationStep data structure."""

    def test_create_simple_step(self):
        step = InvestigationStep(id="step-1", description="Collect logs")

        assert step.id == "step-1"
        assert step.description == "Collect logs"
        assert step.status == InvestigationStepStatus.PENDING
        assert step.artifacts_to_analyze == []

    def test_step_to_from_dict(self):
        data = {
            "id": "step-2",
            "description": "Analyze timeline",
            "status": "completed",
            "artifacts_to_analyze": ["logs/sysmon.json"],
            "reference_patterns": ["refs/pattern.md"],
        }

        step = InvestigationStep.from_dict(data)
        assert step.status == InvestigationStepStatus.COMPLETED
        assert step.artifacts_to_analyze == ["logs/sysmon.json"]

        round_trip = step.to_dict()
        assert round_trip["id"] == "step-2"
        assert round_trip["status"] == "completed"
        assert round_trip["artifacts_to_analyze"] == ["logs/sysmon.json"]

    def test_step_status_transitions(self):
        step = InvestigationStep(id="step-3", description="Process evidence")

        step.mark_in_progress()
        assert step.status == InvestigationStepStatus.IN_PROGRESS
        assert step.started_at is not None

        step.mark_completed("Done")
        assert step.status == InvestigationStepStatus.COMPLETED
        assert step.completed_at is not None
        assert step.analyst_notes == "Done"

        step.mark_failed("Failure")
        assert step.status == InvestigationStepStatus.FAILED
        assert step.error_message == "Failure"


class TestVerification:
    """Tests for Verification data structure."""

    def test_verification_to_from_dict(self):
        verification = Verification(type=VerificationType.COMMAND, run="pytest")
        data = verification.to_dict()
        assert data == {"type": "command", "run": "pytest"}

        loaded = Verification.from_dict({"type": "browser", "scenario": "Check UI"})
        assert loaded.type == VerificationType.BROWSER
        assert loaded.scenario == "Check UI"


class TestInvestigationPhase:
    """Tests for InvestigationPhase behavior."""

    def test_phase_is_complete(self):
        steps = [
            InvestigationStep(id="s1", description="One", status=InvestigationStepStatus.COMPLETED),
            InvestigationStep(id="s2", description="Two", status=InvestigationStepStatus.COMPLETED),
        ]
        phase = InvestigationPhase(phase=1, name="Phase 1", steps=steps)

        assert phase.is_complete() is True

    def test_phase_get_pending_steps(self):
        steps = [
            InvestigationStep(id="s1", description="First", status=InvestigationStepStatus.COMPLETED),
            InvestigationStep(id="s2", description="Second"),
        ]
        phase = InvestigationPhase(phase=1, name="Phase 1", steps=steps)

        pending = phase.get_pending_steps()
        assert [s.id for s in pending] == ["s2"]

    def test_phase_get_progress(self):
        steps = [
            InvestigationStep(id="s1", description="One", status=InvestigationStepStatus.COMPLETED),
            InvestigationStep(id="s2", description="Two"),
        ]
        phase = InvestigationPhase(phase=1, name="Phase 1", steps=steps)

        progress = phase.get_progress()
        assert progress["completed"] == 1
        assert progress["total"] == 2

    def test_phase_to_from_dict(self):
        phase = InvestigationPhase(
            phase=2,
            name="Analysis",
            phase_type=InvestigationPhaseType.ANALYSIS,
            steps=[InvestigationStep(id="s1", description="Check logs")],
        )

        data = phase.to_dict()
        assert data["phase"] == 2
        assert data["type"] == "analysis"
        assert len(data["analysis_tasks"]) == 1

        loaded = InvestigationPhase.from_dict(data)
        assert loaded.phase == 2
        assert loaded.phase_type == InvestigationPhaseType.ANALYSIS
        assert len(loaded.steps) == 1


class TestInvestigationPlan:
    """Tests for InvestigationPlan behavior."""

    def test_plan_get_available_phases(self):
        phase1 = InvestigationPhase(
            phase=1,
            name="Phase 1",
            steps=[InvestigationStep(id="s1", description="Done", status=InvestigationStepStatus.COMPLETED)],
        )
        phase2 = InvestigationPhase(
            phase=2,
            name="Phase 2",
            depends_on=[1],
            steps=[InvestigationStep(id="s2", description="Pending")],
        )
        plan = make_plan([phase1, phase2])

        available = plan.get_available_phases()
        assert [p.phase for p in available] == [2]

    def test_plan_get_next_step(self):
        phase = InvestigationPhase(
            phase=1,
            name="Phase 1",
            steps=[InvestigationStep(id="s1", description="Pending")],
        )
        plan = make_plan([phase])

        next_work = plan.get_next_step()
        assert next_work is not None
        _, step = next_work
        assert step.id == "s1"

    def test_plan_get_progress(self):
        phase = InvestigationPhase(
            phase=1,
            name="Phase 1",
            steps=[
                InvestigationStep(id="s1", description="Done", status=InvestigationStepStatus.COMPLETED),
                InvestigationStep(id="s2", description="Pending"),
            ],
        )
        plan = make_plan([phase])

        progress = plan.get_progress()
        assert progress["total_steps"] == 2
        assert progress["completed_steps"] == 1
        assert progress["percent_complete"] == 50.0
        assert progress["is_complete"] is False

    def test_plan_save_and_load(self, tmp_path: Path):
        phase = InvestigationPhase(
            phase=1,
            name="Phase 1",
            steps=[InvestigationStep(id="s1", description="Pending")],
        )
        plan = make_plan([phase])
        plan_path = tmp_path / "investigation_plan.json"

        plan.save(plan_path)
        loaded = InvestigationPlan.load(plan_path)

        assert loaded.case_name == plan.case_name
        assert len(loaded.phases) == 1
        assert loaded.updated_at is not None

    def test_plan_to_from_dict(self):
        plan = make_plan()
        data = plan.to_dict()

        assert data["case_id"] == "case-001"
        assert data["case_name"] == "Test Case"

        loaded = InvestigationPlan.from_dict(data)
        assert loaded.case_id == "case-001"
        assert loaded.case_name == "Test Case"


class TestInvestigationPlanFactory:
    """Tests for InvestigationPlanFactory helpers."""

    def test_create_from_case_requirements(self):
        plan = InvestigationPlanFactory.create_from_case_requirements(
            case_id="case-002",
            case_name="Email Investigation",
            case_type=CaseType.PHISHING,
            evidence_sources=[{"name": "mailbox"}],
            investigation_objectives=["Identify malicious sender"],
        )

        assert plan.case_id == "case-002"
        assert plan.case_name == "Email Investigation"
        assert plan.case_type == CaseType.PHISHING
        assert len(plan.phases) > 0

    def test_create_triage_plan(self):
        plan = InvestigationPlanFactory.create_triage_plan(
            case_id="case-003",
            case_name="Quick Triage",
            evidence_sources=[{"name": "endpoint"}],
        )

        assert plan.case_type == CaseType.TRIAGE
        assert len(plan.phases) == 1
        assert plan.phases[0].name == "Rapid Triage"
