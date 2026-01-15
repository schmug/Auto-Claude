"""
Investigation Phase Model
=========================

Represents a phase in the DFIR investigation plan.
"""

from dataclasses import dataclass, field

from .enums import InvestigationPhaseType, InvestigationStepStatus
from .step import InvestigationStep


@dataclass
class InvestigationPhase:
    """A phase in the investigation plan containing multiple steps."""
    
    phase: int  # Phase number (1, 2, 3, ...)
    name: str
    phase_type: InvestigationPhaseType = InvestigationPhaseType.ANALYSIS
    description: str = ""
    steps: list[InvestigationStep] = field(default_factory=list)
    depends_on: list[int] = field(default_factory=list)  # Phase numbers
    parallel_safe: bool = False  # Can steps run in parallel?
    
    # Phase-level metadata
    evidence_scope: list[str] = field(default_factory=list)  # Evidence sources for this phase
    expected_outputs: list[str] = field(default_factory=list)  # Expected deliverables
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "phase": self.phase,
            "name": self.name,
            "phase_type": self.phase_type.value,
            "description": self.description,
            "steps": [s.to_dict() for s in self.steps],
            "depends_on": self.depends_on,
            "parallel_safe": self.parallel_safe,
            "evidence_scope": self.evidence_scope,
            "expected_outputs": self.expected_outputs,
        }
    
    @classmethod
    def from_dict(cls, data: dict, phase_num: int | None = None) -> "InvestigationPhase":
        """Create InvestigationPhase from dictionary."""
        phase_type_str = data.get("phase_type", "analysis")
        try:
            phase_type = InvestigationPhaseType(phase_type_str)
        except ValueError:
            phase_type = InvestigationPhaseType.ANALYSIS
            
        return cls(
            phase=phase_num or data.get("phase", 1),
            name=data.get("name", ""),
            phase_type=phase_type,
            description=data.get("description", ""),
            steps=[InvestigationStep.from_dict(s) for s in data.get("steps", [])],
            depends_on=data.get("depends_on", []),
            parallel_safe=data.get("parallel_safe", False),
            evidence_scope=data.get("evidence_scope", []),
            expected_outputs=data.get("expected_outputs", []),
        )
    
    def is_complete(self) -> bool:
        """Check if all steps in this phase are completed."""
        if not self.steps:
            return False
        return all(s.status == InvestigationStepStatus.COMPLETED for s in self.steps)
    
    def get_pending_steps(self) -> list[InvestigationStep]:
        """Get steps that are pending and ready to execute."""
        completed_step_ids = {s.id for s in self.steps if s.status == InvestigationStepStatus.COMPLETED}
        pending = []
        
        for step in self.steps:
            if step.status == InvestigationStepStatus.PENDING:
                # Check if dependencies are satisfied
                deps_met = all(dep in completed_step_ids for dep in step.depends_on)
                if deps_met:
                    pending.append(step)
        
        return pending
    
    def get_in_progress_steps(self) -> list[InvestigationStep]:
        """Get steps currently in progress."""
        return [s for s in self.steps if s.status == InvestigationStepStatus.IN_PROGRESS]
    
    def get_failed_steps(self) -> list[InvestigationStep]:
        """Get steps that have failed."""
        return [s for s in self.steps if s.status == InvestigationStepStatus.FAILED]
    
    def get_progress(self) -> dict:
        """Get progress statistics for this phase."""
        total = len(self.steps)
        if total == 0:
            return {"total": 0, "completed": 0, "percent": 0}
            
        completed = sum(1 for s in self.steps if s.status == InvestigationStepStatus.COMPLETED)
        failed = sum(1 for s in self.steps if s.status == InvestigationStepStatus.FAILED)
        in_progress = sum(1 for s in self.steps if s.status == InvestigationStepStatus.IN_PROGRESS)
        
        return {
            "total": total,
            "completed": completed,
            "failed": failed,
            "in_progress": in_progress,
            "pending": total - completed - failed - in_progress,
            "percent": round(100 * completed / total, 1),
        }
    
    def get_all_findings(self) -> list:
        """Get all findings from all steps in this phase."""
        findings = []
        for step in self.steps:
            findings.extend(step.findings)
        return findings
    
    def get_all_iocs(self) -> list[str]:
        """Get all IOC IDs extracted in this phase."""
        iocs = []
        for step in self.steps:
            iocs.extend(step.iocs_extracted)
        return list(set(iocs))  # Deduplicate
