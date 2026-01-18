"""
Investigation Plan Model
========================

Defines the complete investigation plan for a DFIR case with progress
tracking, status management, and evidence handling capabilities.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from .enums import CaseType, InvestigationPhaseType, InvestigationStepStatus
from .phase import InvestigationPhase
from .step import InvestigationStep


@dataclass
class InvestigationPlan:
    """Complete investigation plan for a DFIR case."""
    
    # Case identification
    case_id: str
    case_name: str
    case_type: CaseType = CaseType.UNKNOWN
    investigation_type: str | None = None
    
    # Case details
    description: str = ""
    investigation_rationale: str = ""
    client: str = ""
    lead_analyst: str = "Auto-DFIR"
    created_by: str | None = None
    
    # Investigation structure
    phases: list[InvestigationPhase] = field(default_factory=list)
    
    # Evidence tracking
    evidence_sources: list[str] = field(default_factory=list)
    
    # Acceptance criteria
    investigation_objectives: list[str] = field(default_factory=list)
    final_deliverables: list[str] = field(default_factory=list)
    final_acceptance: list[str] = field(default_factory=list)
    
    # Metadata
    created_at: str | None = None
    updated_at: str | None = None
    case_file: str | None = None
    summary: dict | None = None
    validation_strategy: dict | None = None
    qa_signoff: dict | None = None
    qa_acceptance: list[str] | None = None
    metadata: dict | None = None
    
    # Status tracking (synced with UI)
    status: str | None = None  # intake, in_progress, validation, reporting, complete
    plan_status: str | None = None  # pending, in_progress, review, completed
    validation_status: str | None = None  # pending, passed, failed
    
    # Notes and recovery
    analyst_notes: str | None = None
    recovery_note: str | None = None

    # Preserve unknown fields for round-trip safety
    extra_fields: dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        result = dict(self.extra_fields)
        result.update(
            {
                "case_id": self.case_id,
                "case_name": self.case_name,
                "description": self.description,
                "client": self.client,
                "lead_analyst": self.lead_analyst,
                "phases": [p.to_dict() for p in self.phases],
                "evidence_sources": self.evidence_sources,
                "investigation_objectives": self.investigation_objectives,
                "final_deliverables": self.final_deliverables,
                "created_at": self.created_at,
                "updated_at": self.updated_at,
                "case_file": self.case_file,
            }
        )

        if self.case_type and self.case_type != CaseType.UNKNOWN:
            result["case_type"] = self.case_type.value
        if self.investigation_type:
            result["investigation_type"] = self.investigation_type
        if self.investigation_rationale:
            result["investigation_rationale"] = self.investigation_rationale
        if self.created_by:
            result["created_by"] = self.created_by
        if self.final_acceptance:
            result["final_acceptance"] = self.final_acceptance
        if self.summary is not None:
            result["summary"] = self.summary
        if self.validation_strategy is not None:
            result["validation_strategy"] = self.validation_strategy
        if self.qa_signoff is not None:
            result["qa_signoff"] = self.qa_signoff
        if self.qa_acceptance is not None:
            result["qa_acceptance"] = self.qa_acceptance
        if self.metadata is not None:
            result["metadata"] = self.metadata
        
        # Include status fields if set
        if self.status:
            result["status"] = self.status
        if self.plan_status:
            result["plan_status"] = self.plan_status
        if self.validation_status:
            result["validation_status"] = self.validation_status
        if self.analyst_notes:
            result["analyst_notes"] = self.analyst_notes
        if self.recovery_note:
            result["recovery_note"] = self.recovery_note
            
        return result
    
    @classmethod
    def from_dict(cls, data: dict) -> "InvestigationPlan":
        """Create InvestigationPlan from dictionary."""
        case_type_str = data.get("case_type", "unknown")
        try:
            case_type = CaseType(case_type_str)
        except ValueError:
            case_type = CaseType.UNKNOWN

        known_fields = {
            "case_id",
            "id",
            "case_name",
            "feature",
            "title",
            "case_type",
            "investigation_type",
            "workflow_type",
            "workflowType",
            "investigation_rationale",
            "description",
            "client",
            "lead_analyst",
            "created_by",
            "phases",
            "evidence_sources",
            "services_involved",
            "investigation_objectives",
            "final_deliverables",
            "final_acceptance",
            "created_at",
            "updated_at",
            "case_file",
            "summary",
            "validation_strategy",
            "qa_signoff",
            "qa_acceptance",
            "metadata",
            "status",
            "plan_status",
            "planStatus",
            "validation_status",
            "analyst_notes",
            "recovery_note",
        }
        extra_fields = {k: v for k, v in data.items() if k not in known_fields}
        case_id = (
            data.get("case_id")
            or data.get("id")
            or data.get("case_name")
            or data.get("feature")
            or ""
        )
        case_name = (
            data.get("case_name")
            or data.get("feature")
            or data.get("title")
            or case_id
            or "Unnamed Case"
        )

        return cls(
            case_id=case_id,
            case_name=case_name,
            case_type=case_type,
            investigation_type=data.get("investigation_type") or data.get("workflow_type"),
            description=data.get("description", ""),
            investigation_rationale=data.get("investigation_rationale", ""),
            client=data.get("client", ""),
            lead_analyst=data.get("lead_analyst", "Auto-DFIR"),
            created_by=data.get("created_by"),
            phases=[
                InvestigationPhase.from_dict(p, idx + 1)
                for idx, p in enumerate(data.get("phases", []))
            ],
            evidence_sources=data.get("evidence_sources", []),
            investigation_objectives=data.get("investigation_objectives", []),
            final_deliverables=data.get("final_deliverables", []),
            final_acceptance=data.get("final_acceptance", []),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            case_file=data.get("case_file"),
            summary=data.get("summary"),
            validation_strategy=data.get("validation_strategy"),
            qa_signoff=data.get("qa_signoff"),
            qa_acceptance=data.get("qa_acceptance"),
            metadata=data.get("metadata"),
            status=data.get("status"),
            plan_status=data.get("plan_status") or data.get("planStatus"),
            validation_status=data.get("validation_status"),
            analyst_notes=data.get("analyst_notes"),
            recovery_note=data.get("recovery_note"),
            extra_fields=extra_fields,
        )
    
    def save(self, path: Path):
        """Save plan to JSON file."""
        self.updated_at = datetime.now().isoformat()
        if not self.created_at:
            self.created_at = self.updated_at
            
        # Auto-update status based on step completion
        self.update_status_from_steps()
        
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load(cls, path: Path) -> "InvestigationPlan":
        """Load plan from JSON file."""
        with open(path, encoding="utf-8") as f:
            return cls.from_dict(json.load(f))
    
    def update_status_from_steps(self):
        """Update overall status based on investigation step completion."""
        all_steps = [s for p in self.phases for s in p.steps]
        
        if not all_steps:
            if not self.status:
                self.status = "intake"
            if not self.plan_status:
                self.plan_status = "pending"
            return
        
        completed_count = sum(1 for s in all_steps if s.status == InvestigationStepStatus.COMPLETED)
        failed_count = sum(1 for s in all_steps if s.status == InvestigationStepStatus.FAILED)
        in_progress_count = sum(1 for s in all_steps if s.status == InvestigationStepStatus.IN_PROGRESS)
        total_count = len(all_steps)
        
        if completed_count == total_count:
            # All steps completed
            if self.validation_status == "passed":
                self.status = "complete"
                self.plan_status = "completed"
            else:
                self.status = "validation"
                self.plan_status = "review"
        elif failed_count > 0 or in_progress_count > 0 or completed_count > 0:
            self.status = "in_progress"
            self.plan_status = "in_progress"
        else:
            self.status = "intake"
            self.plan_status = "pending"
    
    def get_available_phases(self) -> list[InvestigationPhase]:
        """Get phases whose dependencies are satisfied."""
        completed_phases = {p.phase for p in self.phases if p.is_complete()}
        available = []
        
        for phase in self.phases:
            if phase.is_complete():
                continue
            deps_met = all(d in completed_phases for d in phase.depends_on)
            if deps_met:
                available.append(phase)
        
        return available
    
    def get_next_step(self) -> tuple[InvestigationPhase, InvestigationStep] | None:
        """Get the next investigation step to work on."""
        for phase in self.get_available_phases():
            pending = phase.get_pending_steps()
            if pending:
                return phase, pending[0]
        return None
    
    def get_progress(self) -> dict:
        """Get overall investigation progress statistics."""
        total_steps = sum(len(p.steps) for p in self.phases)
        done_steps = sum(
            1 for p in self.phases for s in p.steps
            if s.status == InvestigationStepStatus.COMPLETED
        )
        failed_steps = sum(
            1 for p in self.phases for s in p.steps
            if s.status == InvestigationStepStatus.FAILED
        )
        
        completed_phases = sum(1 for p in self.phases if p.is_complete())
        
        return {
            "total_phases": len(self.phases),
            "completed_phases": completed_phases,
            "total_steps": total_steps,
            "completed_steps": done_steps,
            "failed_steps": failed_steps,
            "percent_complete": round(100 * done_steps / total_steps, 1) if total_steps > 0 else 0,
            "is_complete": done_steps == total_steps and failed_steps == 0,
        }
    
    def get_status_summary(self) -> str:
        """Get a human-readable status summary."""
        progress = self.get_progress()
        lines = [
            f"Case: {self.case_name} ({self.case_id})",
            f"Type: {self.case_type.value}",
            f"Progress: {progress['completed_steps']}/{progress['total_steps']} steps ({progress['percent_complete']}%)",
            f"Phases: {progress['completed_phases']}/{progress['total_phases']} complete",
        ]
        
        if progress["failed_steps"] > 0:
            lines.append(f"Failed: {progress['failed_steps']} steps need attention")
        
        if progress["is_complete"]:
            lines.append("Status: COMPLETE - Ready for validation and reporting")
        else:
            next_work = self.get_next_step()
            if next_work:
                phase, step = next_work
                lines.append(f"Next: Phase {phase.phase} ({phase.name}) - {step.description}")
            else:
                lines.append("Status: BLOCKED - No available steps")
        
        return "\n".join(lines)
    
    def get_all_findings(self) -> list:
        """Get all findings from all phases."""
        findings = []
        for phase in self.phases:
            findings.extend(phase.get_all_findings())
        return findings
    
    def get_all_iocs(self) -> list[str]:
        """Get all IOC IDs from all phases."""
        iocs = []
        for phase in self.phases:
            iocs.extend(phase.get_all_iocs())
        return list(set(iocs))
    
    def add_followup_phase(
        self,
        name: str,
        steps: list[InvestigationStep],
        phase_type: InvestigationPhaseType = InvestigationPhaseType.ANALYSIS,
        parallel_safe: bool = False,
    ) -> InvestigationPhase:
        """Add a new follow-up phase to an existing investigation."""
        if self.phases:
            next_phase_num = max(p.phase for p in self.phases) + 1
            depends_on = [p.phase for p in self.phases]
        else:
            next_phase_num = 1
            depends_on = []
        
        new_phase = InvestigationPhase(
            phase=next_phase_num,
            name=name,
            phase_type=phase_type,
            steps=steps,
            depends_on=depends_on,
            parallel_safe=parallel_safe,
        )
        
        self.phases.append(new_phase)
        return new_phase
    
    def reset_for_followup(self):
        """Reset plan status for follow-up work."""
        self.status = "in_progress"
        self.plan_status = "in_progress"
        self.validation_status = None
    
    def mark_step_complete(self, step_id: str, notes: str | None = None) -> bool:
        """Mark a specific step as completed."""
        for phase in self.phases:
            for step in phase.steps:
                if step.id == step_id:
                    step.mark_completed(notes)
                    return True
        return False
    
    def mark_step_failed(self, step_id: str, error: str) -> bool:
        """Mark a specific step as failed."""
        for phase in self.phases:
            for step in phase.steps:
                if step.id == step_id:
                    step.mark_failed(error)
                    return True
        return False
