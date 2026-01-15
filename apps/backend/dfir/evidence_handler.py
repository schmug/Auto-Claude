"""
Evidence Handler Module
=======================

Handles evidence integrity verification, chain of custody tracking,
and evidence metadata management for DFIR investigations.
"""

import hashlib
import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from investigation_plan.enums import ChainOfCustodyAction, EvidenceType


@dataclass
class EvidenceSource:
    """Represents a single evidence source."""
    
    name: str
    evidence_type: EvidenceType
    original_path: str
    collected_path: str | None = None
    
    # Integrity
    original_hash: str | None = None
    current_hash: str | None = None
    hash_algorithm: str = "sha256"
    integrity_verified: bool = False
    
    # Metadata
    file_size: int = 0
    collected_at: str | None = None
    collected_by: str = "Auto-DFIR"
    source_system: str | None = None
    
    # Chain of custody
    custody_entries: list[dict] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "evidence_type": self.evidence_type.value,
            "original_path": self.original_path,
            "collected_path": self.collected_path,
            "original_hash": self.original_hash,
            "current_hash": self.current_hash,
            "hash_algorithm": self.hash_algorithm,
            "integrity_verified": self.integrity_verified,
            "file_size": self.file_size,
            "collected_at": self.collected_at,
            "collected_by": self.collected_by,
            "source_system": self.source_system,
            "custody_entries": self.custody_entries,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "EvidenceSource":
        """Create EvidenceSource from dictionary."""
        evidence_type_str = data.get("evidence_type", "other")
        try:
            evidence_type = EvidenceType(evidence_type_str)
        except ValueError:
            evidence_type = EvidenceType.OTHER
            
        return cls(
            name=data.get("name", ""),
            evidence_type=evidence_type,
            original_path=data.get("original_path", ""),
            collected_path=data.get("collected_path"),
            original_hash=data.get("original_hash"),
            current_hash=data.get("current_hash"),
            hash_algorithm=data.get("hash_algorithm", "sha256"),
            integrity_verified=data.get("integrity_verified", False),
            file_size=data.get("file_size", 0),
            collected_at=data.get("collected_at"),
            collected_by=data.get("collected_by", "Auto-DFIR"),
            source_system=data.get("source_system"),
            custody_entries=data.get("custody_entries", []),
        )


class EvidenceHandler:
    """Handles evidence collection, verification, and chain of custody."""
    
    def __init__(self, case_dir: Path):
        """Initialize evidence handler for a case."""
        self.case_dir = Path(case_dir)
        self.evidence_dir = self.case_dir / "evidence"
        self.inventory_file = self.case_dir / "evidence_inventory.json"
        self.custody_log = self.case_dir / "chain_of_custody.log"
        
        # Create directories
        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        
        # Load or create inventory
        self.inventory: dict[str, EvidenceSource] = {}
        self._load_inventory()
    
    def _load_inventory(self):
        """Load evidence inventory from file."""
        if self.inventory_file.exists():
            with open(self.inventory_file) as f:
                data = json.load(f)
                for name, source_data in data.get("evidence_sources", {}).items():
                    self.inventory[name] = EvidenceSource.from_dict(source_data)
    
    def _save_inventory(self):
        """Save evidence inventory to file."""
        data = {
            "case_dir": str(self.case_dir),
            "evidence_sources": {
                name: source.to_dict()
                for name, source in self.inventory.items()
            },
            "updated_at": datetime.now().isoformat(),
        }
        with open(self.inventory_file, "w") as f:
            json.dump(data, f, indent=2)
    
    def _log_custody(
        self,
        action: ChainOfCustodyAction,
        evidence_name: str,
        details: str,
        analyst: str = "Auto-DFIR",
    ):
        """Log a chain of custody entry."""
        timestamp = datetime.now().isoformat()
        entry = f"[{timestamp}] [{action.value.upper()}] {evidence_name}: {details} (by {analyst})\n"
        
        with open(self.custody_log, "a") as f:
            f.write(entry)
        
        # Also add to evidence source
        if evidence_name in self.inventory:
            self.inventory[evidence_name].custody_entries.append({
                "timestamp": timestamp,
                "action": action.value,
                "details": details,
                "analyst": analyst,
            })
    
    def calculate_hash(self, file_path: Path, algorithm: str = "sha256") -> str:
        """Calculate hash of a file."""
        hasher = hashlib.new(algorithm)
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    
    def register_evidence(
        self,
        name: str,
        evidence_type: EvidenceType,
        original_path: str,
        source_system: str | None = None,
        analyst: str = "Auto-DFIR",
    ) -> EvidenceSource:
        """
        Register a new evidence source.
        
        Args:
            name: Unique name for this evidence
            evidence_type: Type of evidence
            original_path: Original path where evidence was found
            source_system: System where evidence originated
            analyst: Name of analyst registering evidence
            
        Returns:
            EvidenceSource object
        """
        source = EvidenceSource(
            name=name,
            evidence_type=evidence_type,
            original_path=original_path,
            source_system=source_system,
            collected_at=datetime.now().isoformat(),
            collected_by=analyst,
        )
        
        self.inventory[name] = source
        self._save_inventory()
        
        self._log_custody(
            ChainOfCustodyAction.COLLECTED,
            name,
            f"Evidence registered from {original_path}",
            analyst,
        )
        
        return source
    
    def collect_evidence(
        self,
        name: str,
        source_path: Path,
        evidence_type: EvidenceType,
        source_system: str | None = None,
        analyst: str = "Auto-DFIR",
    ) -> EvidenceSource:
        """
        Collect evidence by copying to evidence directory and hashing.
        
        Args:
            name: Unique name for this evidence
            source_path: Path to source file
            evidence_type: Type of evidence
            source_system: System where evidence originated
            analyst: Name of analyst collecting evidence
            
        Returns:
            EvidenceSource object with hash information
        """
        source_path = Path(source_path)
        
        if not source_path.exists():
            raise FileNotFoundError(f"Evidence source not found: {source_path}")
        
        # Calculate original hash
        original_hash = self.calculate_hash(source_path)
        
        # Copy to evidence directory
        dest_path = self.evidence_dir / source_path.name
        if dest_path.exists():
            # Add timestamp to avoid collision
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dest_path = self.evidence_dir / f"{source_path.stem}_{timestamp}{source_path.suffix}"
        
        # Copy file
        import shutil
        shutil.copy2(source_path, dest_path)
        
        # Verify copy
        copied_hash = self.calculate_hash(dest_path)
        if copied_hash != original_hash:
            dest_path.unlink()  # Remove corrupted copy
            raise ValueError(f"Hash mismatch after copy: {original_hash} != {copied_hash}")
        
        # Create evidence source
        source = EvidenceSource(
            name=name,
            evidence_type=evidence_type,
            original_path=str(source_path),
            collected_path=str(dest_path),
            original_hash=original_hash,
            current_hash=copied_hash,
            integrity_verified=True,
            file_size=dest_path.stat().st_size,
            collected_at=datetime.now().isoformat(),
            collected_by=analyst,
            source_system=source_system,
        )
        
        self.inventory[name] = source
        self._save_inventory()
        
        self._log_custody(
            ChainOfCustodyAction.COLLECTED,
            name,
            f"Collected from {source_path}, hash: {original_hash[:16]}...",
            analyst,
        )
        
        return source
    
    def verify_integrity(self, name: str) -> tuple[bool, str]:
        """
        Verify integrity of collected evidence.
        
        Args:
            name: Evidence name to verify
            
        Returns:
            Tuple of (is_valid, message)
        """
        if name not in self.inventory:
            return False, f"Evidence '{name}' not found in inventory"
        
        source = self.inventory[name]
        
        if not source.collected_path:
            return False, "Evidence has not been collected yet"
        
        collected_path = Path(source.collected_path)
        if not collected_path.exists():
            return False, f"Evidence file not found: {collected_path}"
        
        # Calculate current hash
        current_hash = self.calculate_hash(collected_path, source.hash_algorithm)
        source.current_hash = current_hash
        
        if current_hash == source.original_hash:
            source.integrity_verified = True
            self._save_inventory()
            
            self._log_custody(
                ChainOfCustodyAction.ANALYZED,
                name,
                f"Integrity verified, hash matches: {current_hash[:16]}...",
            )
            
            return True, f"Integrity verified: {current_hash}"
        else:
            source.integrity_verified = False
            self._save_inventory()
            
            self._log_custody(
                ChainOfCustodyAction.ANALYZED,
                name,
                f"INTEGRITY FAILURE: expected {source.original_hash[:16]}..., got {current_hash[:16]}...",
            )
            
            return False, f"Hash mismatch: expected {source.original_hash}, got {current_hash}"
    
    def verify_all_integrity(self) -> dict:
        """
        Verify integrity of all collected evidence.
        
        Returns:
            Dictionary with verification results
        """
        results = {
            "verified": [],
            "failed": [],
            "not_collected": [],
        }
        
        for name, source in self.inventory.items():
            if not source.collected_path:
                results["not_collected"].append(name)
                continue
            
            is_valid, message = self.verify_integrity(name)
            if is_valid:
                results["verified"].append({"name": name, "hash": source.current_hash})
            else:
                results["failed"].append({"name": name, "error": message})
        
        return results
    
    def get_evidence(self, name: str) -> EvidenceSource | None:
        """Get evidence source by name."""
        return self.inventory.get(name)
    
    def get_evidence_path(self, name: str) -> Path | None:
        """Get path to collected evidence file."""
        source = self.inventory.get(name)
        if source and source.collected_path:
            return Path(source.collected_path)
        return None
    
    def list_evidence(self) -> list[dict]:
        """List all evidence sources."""
        return [source.to_dict() for source in self.inventory.values()]
    
    def export_inventory(self, output_path: Path | None = None) -> dict:
        """
        Export evidence inventory.
        
        Args:
            output_path: Optional path to save export
            
        Returns:
            Inventory data dictionary
        """
        data = {
            "case_dir": str(self.case_dir),
            "exported_at": datetime.now().isoformat(),
            "evidence_count": len(self.inventory),
            "evidence_sources": {
                name: source.to_dict()
                for name, source in self.inventory.items()
            },
            "integrity_summary": self.verify_all_integrity(),
        }
        
        if output_path:
            with open(output_path, "w") as f:
                json.dump(data, f, indent=2)
        
        return data
    
    def get_chain_of_custody(self) -> list[str]:
        """Get all chain of custody entries."""
        if not self.custody_log.exists():
            return []
        
        with open(self.custody_log) as f:
            return f.readlines()


def initialize_case_evidence(case_dir: Path) -> EvidenceHandler:
    """
    Initialize evidence handling for a new case.
    
    Args:
        case_dir: Case directory path
        
    Returns:
        Configured EvidenceHandler
    """
    handler = EvidenceHandler(case_dir)
    
    # Log case initialization
    handler._log_custody(
        ChainOfCustodyAction.COLLECTED,
        "CASE_INIT",
        f"Investigation started for case at {case_dir}",
    )
    
    return handler
