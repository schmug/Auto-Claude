"""
DFIR Module
===========

Digital Forensics and Incident Response utilities for Auto-DFIR.

This module provides:
- Evidence handling and chain of custody tracking
- IOC extraction and management
- MITRE ATT&CK technique mapping
- Timeline reconstruction utilities
"""

from .evidence_handler import (
    EvidenceHandler,
    EvidenceSource,
    initialize_case_evidence,
)
from .ioc_manager import (
    IOC,
    IOCManager,
)
from .mitre_mapper import (
    MITREMapper,
    TechniqueMapping,
    MITRE_TECHNIQUES,
    TACTIC_ORDER,
)

__all__ = [
    # Evidence handling
    "EvidenceHandler",
    "EvidenceSource",
    "initialize_case_evidence",
    # IOC management
    "IOC",
    "IOCManager",
    # MITRE mapping
    "MITREMapper",
    "TechniqueMapping",
    "MITRE_TECHNIQUES",
    "TACTIC_ORDER",
]
