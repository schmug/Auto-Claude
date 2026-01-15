"""
IOC Manager Module
==================

Manages Indicators of Compromise (IOCs) extraction, storage,
deduplication, and export for DFIR investigations.
"""

import csv
import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from investigation_plan.enums import IOCType


@dataclass
class IOC:
    """Represents a single Indicator of Compromise."""
    
    id: str
    ioc_type: IOCType
    value: str
    
    # Context
    description: str = ""
    source_evidence: str | None = None
    source_step: str | None = None
    first_seen: str | None = None
    last_seen: str | None = None
    
    # Classification
    confidence: float = 0.5  # 0.0 to 1.0
    severity: str = "medium"  # critical, high, medium, low, informational
    is_malicious: bool | None = None  # True, False, or None (unknown)
    
    # Enrichment
    threat_intel: dict = field(default_factory=dict)
    mitre_techniques: list[str] = field(default_factory=list)
    related_iocs: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    
    # Metadata
    created_at: str | None = None
    updated_at: str | None = None
    analyst_notes: str | None = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "ioc_type": self.ioc_type.value,
            "value": self.value,
            "description": self.description,
            "source_evidence": self.source_evidence,
            "source_step": self.source_step,
            "first_seen": self.first_seen,
            "last_seen": self.last_seen,
            "confidence": self.confidence,
            "severity": self.severity,
            "is_malicious": self.is_malicious,
            "threat_intel": self.threat_intel,
            "mitre_techniques": self.mitre_techniques,
            "related_iocs": self.related_iocs,
            "tags": self.tags,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "analyst_notes": self.analyst_notes,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "IOC":
        """Create IOC from dictionary."""
        ioc_type_str = data.get("ioc_type", "ip_address")
        try:
            ioc_type = IOCType(ioc_type_str)
        except ValueError:
            ioc_type = IOCType.IP_ADDRESS
            
        return cls(
            id=data.get("id", ""),
            ioc_type=ioc_type,
            value=data.get("value", ""),
            description=data.get("description", ""),
            source_evidence=data.get("source_evidence"),
            source_step=data.get("source_step"),
            first_seen=data.get("first_seen"),
            last_seen=data.get("last_seen"),
            confidence=data.get("confidence", 0.5),
            severity=data.get("severity", "medium"),
            is_malicious=data.get("is_malicious"),
            threat_intel=data.get("threat_intel", {}),
            mitre_techniques=data.get("mitre_techniques", []),
            related_iocs=data.get("related_iocs", []),
            tags=data.get("tags", []),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            analyst_notes=data.get("analyst_notes"),
        )


class IOCManager:
    """Manages IOCs for a DFIR investigation."""
    
    # Regex patterns for IOC extraction
    PATTERNS = {
        IOCType.IP_ADDRESS: r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b',
        IOCType.DOMAIN: r'\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b',
        IOCType.URL: r'https?://[^\s<>"{}|\\^`\[\]]+',
        IOCType.EMAIL_ADDRESS: r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        IOCType.FILE_HASH_MD5: r'\b[a-fA-F0-9]{32}\b',
        IOCType.FILE_HASH_SHA1: r'\b[a-fA-F0-9]{40}\b',
        IOCType.FILE_HASH_SHA256: r'\b[a-fA-F0-9]{64}\b',
        IOCType.CVE: r'CVE-\d{4}-\d{4,}',
    }
    
    # Common false positives to filter
    FALSE_POSITIVES = {
        IOCType.IP_ADDRESS: {'0.0.0.0', '127.0.0.1', '255.255.255.255', '192.168.0.1'},
        IOCType.DOMAIN: {'localhost', 'example.com', 'test.com', 'microsoft.com', 'google.com'},
    }
    
    def __init__(self, case_dir: Path):
        """Initialize IOC manager for a case."""
        self.case_dir = Path(case_dir)
        self.ioc_dir = self.case_dir / "analysis" / "iocs"
        self.ioc_file = self.ioc_dir / "extracted_iocs.json"
        
        # Create directories
        self.ioc_dir.mkdir(parents=True, exist_ok=True)
        
        # Load or create IOC database
        self.iocs: dict[str, IOC] = {}
        self._load_iocs()
        
        # Counter for generating IDs
        self._id_counter = len(self.iocs)
    
    def _load_iocs(self):
        """Load IOCs from file."""
        if self.ioc_file.exists():
            with open(self.ioc_file) as f:
                data = json.load(f)
                for ioc_data in data.get("iocs", []):
                    ioc = IOC.from_dict(ioc_data)
                    self.iocs[ioc.id] = ioc
    
    def _save_iocs(self):
        """Save IOCs to file."""
        data = {
            "case_dir": str(self.case_dir),
            "ioc_count": len(self.iocs),
            "updated_at": datetime.now().isoformat(),
            "iocs": [ioc.to_dict() for ioc in self.iocs.values()],
        }
        with open(self.ioc_file, "w") as f:
            json.dump(data, f, indent=2)
    
    def _generate_id(self, ioc_type: IOCType) -> str:
        """Generate a unique IOC ID."""
        self._id_counter += 1
        type_prefix = ioc_type.value.split("_")[0][:4]
        return f"{type_prefix}-{self._id_counter:04d}"
    
    def _is_false_positive(self, ioc_type: IOCType, value: str) -> bool:
        """Check if value is a known false positive."""
        fp_set = self.FALSE_POSITIVES.get(ioc_type, set())
        return value.lower() in {fp.lower() for fp in fp_set}
    
    def add_ioc(
        self,
        ioc_type: IOCType,
        value: str,
        description: str = "",
        source_evidence: str | None = None,
        source_step: str | None = None,
        confidence: float = 0.5,
        severity: str = "medium",
        tags: list[str] | None = None,
    ) -> IOC | None:
        """
        Add a new IOC to the database.
        
        Args:
            ioc_type: Type of IOC
            value: IOC value
            description: Description of the IOC
            source_evidence: Evidence source where IOC was found
            source_step: Investigation step that found the IOC
            confidence: Confidence level (0.0-1.0)
            severity: Severity level
            tags: Optional tags
            
        Returns:
            IOC object if added, None if duplicate or false positive
        """
        # Check for false positive
        if self._is_false_positive(ioc_type, value):
            return None
        
        # Check for duplicate
        for existing in self.iocs.values():
            if existing.ioc_type == ioc_type and existing.value.lower() == value.lower():
                # Update existing IOC with new source
                if source_evidence and source_evidence not in (existing.source_evidence or ""):
                    existing.source_evidence = f"{existing.source_evidence or ''}, {source_evidence}".strip(", ")
                existing.updated_at = datetime.now().isoformat()
                self._save_iocs()
                return existing
        
        # Create new IOC
        ioc = IOC(
            id=self._generate_id(ioc_type),
            ioc_type=ioc_type,
            value=value,
            description=description,
            source_evidence=source_evidence,
            source_step=source_step,
            confidence=confidence,
            severity=severity,
            tags=tags or [],
            created_at=datetime.now().isoformat(),
        )
        
        self.iocs[ioc.id] = ioc
        self._save_iocs()
        
        return ioc
    
    def extract_iocs_from_text(
        self,
        text: str,
        source_evidence: str | None = None,
        source_step: str | None = None,
    ) -> list[IOC]:
        """
        Extract IOCs from text using regex patterns.
        
        Args:
            text: Text to extract IOCs from
            source_evidence: Evidence source
            source_step: Investigation step
            
        Returns:
            List of extracted IOCs
        """
        extracted = []
        
        for ioc_type, pattern in self.PATTERNS.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in set(matches):  # Deduplicate within text
                ioc = self.add_ioc(
                    ioc_type=ioc_type,
                    value=match,
                    source_evidence=source_evidence,
                    source_step=source_step,
                )
                if ioc:
                    extracted.append(ioc)
        
        return extracted
    
    def get_ioc(self, ioc_id: str) -> IOC | None:
        """Get IOC by ID."""
        return self.iocs.get(ioc_id)
    
    def get_iocs_by_type(self, ioc_type: IOCType) -> list[IOC]:
        """Get all IOCs of a specific type."""
        return [ioc for ioc in self.iocs.values() if ioc.ioc_type == ioc_type]
    
    def get_malicious_iocs(self) -> list[IOC]:
        """Get all IOCs marked as malicious."""
        return [ioc for ioc in self.iocs.values() if ioc.is_malicious is True]
    
    def get_high_confidence_iocs(self, threshold: float = 0.8) -> list[IOC]:
        """Get IOCs with confidence above threshold."""
        return [ioc for ioc in self.iocs.values() if ioc.confidence >= threshold]
    
    def update_ioc(self, ioc_id: str, **kwargs) -> IOC | None:
        """Update IOC fields."""
        ioc = self.iocs.get(ioc_id)
        if not ioc:
            return None
        
        for key, value in kwargs.items():
            if hasattr(ioc, key):
                setattr(ioc, key, value)
        
        ioc.updated_at = datetime.now().isoformat()
        self._save_iocs()
        
        return ioc
    
    def enrich_ioc(self, ioc_id: str, threat_intel: dict) -> IOC | None:
        """Add threat intelligence enrichment to an IOC."""
        ioc = self.iocs.get(ioc_id)
        if not ioc:
            return None
        
        ioc.threat_intel.update(threat_intel)
        
        # Update malicious status based on threat intel
        if threat_intel.get("is_malicious") is not None:
            ioc.is_malicious = threat_intel["is_malicious"]
        
        # Update confidence based on threat intel
        if threat_intel.get("confidence"):
            # Average with existing confidence
            ioc.confidence = (ioc.confidence + threat_intel["confidence"]) / 2
        
        ioc.updated_at = datetime.now().isoformat()
        self._save_iocs()
        
        return ioc
    
    def export_to_json(self, output_path: Path | None = None) -> dict:
        """Export IOCs to JSON format."""
        data = {
            "export_metadata": {
                "case_dir": str(self.case_dir),
                "exported_at": datetime.now().isoformat(),
                "ioc_count": len(self.iocs),
                "generator": "Auto-DFIR",
            },
            "iocs": [ioc.to_dict() for ioc in self.iocs.values()],
            "summary": {
                "by_type": {},
                "by_severity": {},
                "malicious_count": len(self.get_malicious_iocs()),
            },
        }
        
        # Calculate summary
        for ioc in self.iocs.values():
            type_key = ioc.ioc_type.value
            data["summary"]["by_type"][type_key] = data["summary"]["by_type"].get(type_key, 0) + 1
            data["summary"]["by_severity"][ioc.severity] = data["summary"]["by_severity"].get(ioc.severity, 0) + 1
        
        if output_path:
            with open(output_path, "w") as f:
                json.dump(data, f, indent=2)
        
        return data
    
    def export_to_csv(self, output_path: Path) -> None:
        """Export IOCs to CSV format."""
        with open(output_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "ID", "Type", "Value", "Confidence", "Severity",
                "Is Malicious", "Description", "Source", "Tags"
            ])
            
            for ioc in self.iocs.values():
                writer.writerow([
                    ioc.id,
                    ioc.ioc_type.value,
                    ioc.value,
                    ioc.confidence,
                    ioc.severity,
                    ioc.is_malicious,
                    ioc.description,
                    ioc.source_evidence,
                    "|".join(ioc.tags),
                ])
    
    def export_to_stix(self, output_path: Path) -> dict:
        """Export IOCs to STIX 2.1 format."""
        stix_bundle = {
            "type": "bundle",
            "id": f"bundle--{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "objects": [],
        }
        
        for ioc in self.iocs.values():
            stix_object = self._ioc_to_stix(ioc)
            if stix_object:
                stix_bundle["objects"].append(stix_object)
        
        with open(output_path, "w") as f:
            json.dump(stix_bundle, f, indent=2)
        
        return stix_bundle
    
    def _ioc_to_stix(self, ioc: IOC) -> dict | None:
        """Convert IOC to STIX 2.1 indicator."""
        pattern = None
        
        if ioc.ioc_type == IOCType.IP_ADDRESS:
            pattern = f"[ipv4-addr:value = '{ioc.value}']"
        elif ioc.ioc_type == IOCType.DOMAIN:
            pattern = f"[domain-name:value = '{ioc.value}']"
        elif ioc.ioc_type == IOCType.URL:
            pattern = f"[url:value = '{ioc.value}']"
        elif ioc.ioc_type == IOCType.FILE_HASH_SHA256:
            pattern = f"[file:hashes.'SHA-256' = '{ioc.value}']"
        elif ioc.ioc_type == IOCType.FILE_HASH_MD5:
            pattern = f"[file:hashes.MD5 = '{ioc.value}']"
        elif ioc.ioc_type == IOCType.EMAIL_ADDRESS:
            pattern = f"[email-addr:value = '{ioc.value}']"
        
        if not pattern:
            return None
        
        return {
            "type": "indicator",
            "id": f"indicator--{ioc.id}",
            "created": ioc.created_at or datetime.now().isoformat(),
            "modified": ioc.updated_at or datetime.now().isoformat(),
            "name": f"{ioc.ioc_type.value}: {ioc.value}",
            "description": ioc.description,
            "pattern": pattern,
            "pattern_type": "stix",
            "valid_from": ioc.first_seen or ioc.created_at,
            "confidence": int(ioc.confidence * 100),
            "labels": ioc.tags,
        }
    
    def get_statistics(self) -> dict:
        """Get IOC statistics."""
        stats = {
            "total": len(self.iocs),
            "by_type": {},
            "by_severity": {},
            "by_malicious_status": {
                "malicious": 0,
                "benign": 0,
                "unknown": 0,
            },
            "average_confidence": 0,
        }
        
        if not self.iocs:
            return stats
        
        total_confidence = 0
        
        for ioc in self.iocs.values():
            # By type
            type_key = ioc.ioc_type.value
            stats["by_type"][type_key] = stats["by_type"].get(type_key, 0) + 1
            
            # By severity
            stats["by_severity"][ioc.severity] = stats["by_severity"].get(ioc.severity, 0) + 1
            
            # By malicious status
            if ioc.is_malicious is True:
                stats["by_malicious_status"]["malicious"] += 1
            elif ioc.is_malicious is False:
                stats["by_malicious_status"]["benign"] += 1
            else:
                stats["by_malicious_status"]["unknown"] += 1
            
            total_confidence += ioc.confidence
        
        stats["average_confidence"] = round(total_confidence / len(self.iocs), 2)
        
        return stats
