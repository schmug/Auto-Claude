"""
Investigation Step Model
========================

Represents a single investigation step within a phase.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .enums import InvestigationStepStatus, FindingSeverity


@dataclass
class Finding:
    """A finding from an investigation step."""
    
    id: str
    title: str
    description: str
    severity: FindingSeverity = FindingSeverity.INFORMATIONAL
    evidence_refs: list[str] = field(default_factory=list)
    ioc_refs: list[str] = field(default_factory=list)
    mitre_techniques: list[str] = field(default_factory=list)
    confidence: float = 0.0  # 0.0 to 1.0
    timestamp: str | None = None
    raw_data: dict | None = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "severity": self.severity.value,
            "evidence_refs": self.evidence_refs,
            "ioc_refs": self.ioc_refs,
            "mitre_techniques": self.mitre_techniques,
            "confidence": self.confidence,
            "timestamp": self.timestamp,
            "raw_data": self.raw_data,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Finding":
        """Create Finding from dictionary."""
        severity = data.get("severity", "informational")
        try:
            severity_enum = FindingSeverity(severity)
        except ValueError:
            severity_enum = FindingSeverity.INFORMATIONAL
            
        return cls(
            id=data.get("id", ""),
            title=data.get("title", ""),
            description=data.get("description", ""),
            severity=severity_enum,
            evidence_refs=data.get("evidence_refs", []),
            ioc_refs=data.get("ioc_refs", []),
            mitre_techniques=data.get("mitre_techniques", []),
            confidence=data.get("confidence", 0.0),
            timestamp=data.get("timestamp"),
            raw_data=data.get("raw_data"),
        )


@dataclass
class InvestigationStep:
    """A single investigation step within a phase."""
    
    id: str
    description: str
    status: InvestigationStepStatus = InvestigationStepStatus.PENDING
    
    # Evidence and analysis
    evidence_sources: list[str] = field(default_factory=list)  # Evidence to analyze
    artifacts_to_examine: list[str] = field(default_factory=list)  # Specific artifacts
    analysis_tools: list[str] = field(default_factory=list)  # Tools to use
    
    # Output
    findings: list[Finding] = field(default_factory=list)
    iocs_extracted: list[str] = field(default_factory=list)  # IOC IDs
    output_files: list[str] = field(default_factory=list)  # Generated files
    
    # Metadata
    analyst_notes: str | None = None
    started_at: str | None = None
    completed_at: str | None = None
    error_message: str | None = None
    attempt_count: int = 0
    
    # Dependencies
    depends_on: list[str] = field(default_factory=list)  # Step IDs
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "description": self.description,
            "status": self.status.value,
            "evidence_sources": self.evidence_sources,
            "artifacts_to_examine": self.artifacts_to_examine,
            "analysis_tools": self.analysis_tools,
            "findings": [f.to_dict() for f in self.findings],
            "iocs_extracted": self.iocs_extracted,
            "output_files": self.output_files,
            "analyst_notes": self.analyst_notes,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "error_message": self.error_message,
            "attempt_count": self.attempt_count,
            "depends_on": self.depends_on,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "InvestigationStep":
        """Create InvestigationStep from dictionary."""
        status = data.get("status", "pending")
        try:
            status_enum = InvestigationStepStatus(status)
        except ValueError:
            status_enum = InvestigationStepStatus.PENDING
            
        return cls(
            id=data.get("id", ""),
            description=data.get("description", ""),
            status=status_enum,
            evidence_sources=data.get("evidence_sources", []),
            artifacts_to_examine=data.get("artifacts_to_examine", []),
            analysis_tools=data.get("analysis_tools", []),
            findings=[Finding.from_dict(f) for f in data.get("findings", [])],
            iocs_extracted=data.get("iocs_extracted", []),
            output_files=data.get("output_files", []),
            analyst_notes=data.get("analyst_notes"),
            started_at=data.get("started_at"),
            completed_at=data.get("completed_at"),
            error_message=data.get("error_message"),
            attempt_count=data.get("attempt_count", 0),
            depends_on=data.get("depends_on", []),
        )
    
    def mark_in_progress(self):
        """Mark step as in progress."""
        self.status = InvestigationStepStatus.IN_PROGRESS
        self.started_at = datetime.now().isoformat()
        self.attempt_count += 1
    
    def mark_completed(self, notes: str | None = None):
        """Mark step as completed."""
        self.status = InvestigationStepStatus.COMPLETED
        self.completed_at = datetime.now().isoformat()
        if notes:
            self.analyst_notes = notes
    
    def mark_failed(self, error: str):
        """Mark step as failed."""
        self.status = InvestigationStepStatus.FAILED
        self.error_message = error
        self.completed_at = datetime.now().isoformat()
    
    def add_finding(self, finding: Finding):
        """Add a finding to this step."""
        self.findings.append(finding)
    
    def add_ioc(self, ioc_id: str):
        """Add an IOC reference to this step."""
        if ioc_id not in self.iocs_extracted:
            self.iocs_extracted.append(ioc_id)
