"""
MITRE ATT&CK Mapper Module
==========================

Maps investigation findings to MITRE ATT&CK framework techniques
and generates ATT&CK Navigator layers.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


# MITRE ATT&CK Enterprise Matrix (subset of common techniques)
MITRE_TECHNIQUES = {
    # Reconnaissance
    "T1595": {"name": "Active Scanning", "tactic": "Reconnaissance"},
    "T1592": {"name": "Gather Victim Host Information", "tactic": "Reconnaissance"},
    "T1589": {"name": "Gather Victim Identity Information", "tactic": "Reconnaissance"},
    
    # Initial Access
    "T1566": {"name": "Phishing", "tactic": "Initial Access"},
    "T1566.001": {"name": "Spearphishing Attachment", "tactic": "Initial Access"},
    "T1566.002": {"name": "Spearphishing Link", "tactic": "Initial Access"},
    "T1190": {"name": "Exploit Public-Facing Application", "tactic": "Initial Access"},
    "T1133": {"name": "External Remote Services", "tactic": "Initial Access"},
    "T1078": {"name": "Valid Accounts", "tactic": "Initial Access"},
    "T1078.001": {"name": "Default Accounts", "tactic": "Initial Access"},
    "T1078.002": {"name": "Domain Accounts", "tactic": "Initial Access"},
    "T1078.003": {"name": "Local Accounts", "tactic": "Initial Access"},
    "T1078.004": {"name": "Cloud Accounts", "tactic": "Initial Access"},
    "T1199": {"name": "Trusted Relationship", "tactic": "Initial Access"},
    
    # Execution
    "T1059": {"name": "Command and Scripting Interpreter", "tactic": "Execution"},
    "T1059.001": {"name": "PowerShell", "tactic": "Execution"},
    "T1059.003": {"name": "Windows Command Shell", "tactic": "Execution"},
    "T1059.005": {"name": "Visual Basic", "tactic": "Execution"},
    "T1059.006": {"name": "Python", "tactic": "Execution"},
    "T1059.007": {"name": "JavaScript", "tactic": "Execution"},
    "T1204": {"name": "User Execution", "tactic": "Execution"},
    "T1204.001": {"name": "Malicious Link", "tactic": "Execution"},
    "T1204.002": {"name": "Malicious File", "tactic": "Execution"},
    "T1053": {"name": "Scheduled Task/Job", "tactic": "Execution"},
    "T1053.005": {"name": "Scheduled Task", "tactic": "Execution"},
    "T1047": {"name": "Windows Management Instrumentation", "tactic": "Execution"},
    
    # Persistence
    "T1547": {"name": "Boot or Logon Autostart Execution", "tactic": "Persistence"},
    "T1547.001": {"name": "Registry Run Keys / Startup Folder", "tactic": "Persistence"},
    "T1136": {"name": "Create Account", "tactic": "Persistence"},
    "T1136.001": {"name": "Local Account", "tactic": "Persistence"},
    "T1136.002": {"name": "Domain Account", "tactic": "Persistence"},
    "T1543": {"name": "Create or Modify System Process", "tactic": "Persistence"},
    "T1543.003": {"name": "Windows Service", "tactic": "Persistence"},
    "T1505": {"name": "Server Software Component", "tactic": "Persistence"},
    "T1505.003": {"name": "Web Shell", "tactic": "Persistence"},
    
    # Privilege Escalation
    "T1548": {"name": "Abuse Elevation Control Mechanism", "tactic": "Privilege Escalation"},
    "T1548.002": {"name": "Bypass User Account Control", "tactic": "Privilege Escalation"},
    "T1134": {"name": "Access Token Manipulation", "tactic": "Privilege Escalation"},
    "T1068": {"name": "Exploitation for Privilege Escalation", "tactic": "Privilege Escalation"},
    
    # Defense Evasion
    "T1070": {"name": "Indicator Removal", "tactic": "Defense Evasion"},
    "T1070.001": {"name": "Clear Windows Event Logs", "tactic": "Defense Evasion"},
    "T1070.004": {"name": "File Deletion", "tactic": "Defense Evasion"},
    "T1562": {"name": "Impair Defenses", "tactic": "Defense Evasion"},
    "T1562.001": {"name": "Disable or Modify Tools", "tactic": "Defense Evasion"},
    "T1036": {"name": "Masquerading", "tactic": "Defense Evasion"},
    "T1036.005": {"name": "Match Legitimate Name or Location", "tactic": "Defense Evasion"},
    "T1027": {"name": "Obfuscated Files or Information", "tactic": "Defense Evasion"},
    "T1055": {"name": "Process Injection", "tactic": "Defense Evasion"},
    
    # Credential Access
    "T1003": {"name": "OS Credential Dumping", "tactic": "Credential Access"},
    "T1003.001": {"name": "LSASS Memory", "tactic": "Credential Access"},
    "T1003.002": {"name": "Security Account Manager", "tactic": "Credential Access"},
    "T1003.003": {"name": "NTDS", "tactic": "Credential Access"},
    "T1555": {"name": "Credentials from Password Stores", "tactic": "Credential Access"},
    "T1110": {"name": "Brute Force", "tactic": "Credential Access"},
    "T1558": {"name": "Steal or Forge Kerberos Tickets", "tactic": "Credential Access"},
    "T1558.003": {"name": "Kerberoasting", "tactic": "Credential Access"},
    
    # Discovery
    "T1082": {"name": "System Information Discovery", "tactic": "Discovery"},
    "T1083": {"name": "File and Directory Discovery", "tactic": "Discovery"},
    "T1057": {"name": "Process Discovery", "tactic": "Discovery"},
    "T1018": {"name": "Remote System Discovery", "tactic": "Discovery"},
    "T1087": {"name": "Account Discovery", "tactic": "Discovery"},
    "T1087.001": {"name": "Local Account", "tactic": "Discovery"},
    "T1087.002": {"name": "Domain Account", "tactic": "Discovery"},
    "T1069": {"name": "Permission Groups Discovery", "tactic": "Discovery"},
    "T1016": {"name": "System Network Configuration Discovery", "tactic": "Discovery"},
    "T1049": {"name": "System Network Connections Discovery", "tactic": "Discovery"},
    
    # Lateral Movement
    "T1021": {"name": "Remote Services", "tactic": "Lateral Movement"},
    "T1021.001": {"name": "Remote Desktop Protocol", "tactic": "Lateral Movement"},
    "T1021.002": {"name": "SMB/Windows Admin Shares", "tactic": "Lateral Movement"},
    "T1021.003": {"name": "Distributed Component Object Model", "tactic": "Lateral Movement"},
    "T1021.004": {"name": "SSH", "tactic": "Lateral Movement"},
    "T1021.006": {"name": "Windows Remote Management", "tactic": "Lateral Movement"},
    "T1570": {"name": "Lateral Tool Transfer", "tactic": "Lateral Movement"},
    "T1080": {"name": "Taint Shared Content", "tactic": "Lateral Movement"},
    
    # Collection
    "T1560": {"name": "Archive Collected Data", "tactic": "Collection"},
    "T1560.001": {"name": "Archive via Utility", "tactic": "Collection"},
    "T1005": {"name": "Data from Local System", "tactic": "Collection"},
    "T1039": {"name": "Data from Network Shared Drive", "tactic": "Collection"},
    "T1074": {"name": "Data Staged", "tactic": "Collection"},
    "T1114": {"name": "Email Collection", "tactic": "Collection"},
    
    # Command and Control
    "T1071": {"name": "Application Layer Protocol", "tactic": "Command and Control"},
    "T1071.001": {"name": "Web Protocols", "tactic": "Command and Control"},
    "T1071.004": {"name": "DNS", "tactic": "Command and Control"},
    "T1105": {"name": "Ingress Tool Transfer", "tactic": "Command and Control"},
    "T1571": {"name": "Non-Standard Port", "tactic": "Command and Control"},
    "T1572": {"name": "Protocol Tunneling", "tactic": "Command and Control"},
    "T1090": {"name": "Proxy", "tactic": "Command and Control"},
    "T1219": {"name": "Remote Access Software", "tactic": "Command and Control"},
    
    # Exfiltration
    "T1041": {"name": "Exfiltration Over C2 Channel", "tactic": "Exfiltration"},
    "T1567": {"name": "Exfiltration Over Web Service", "tactic": "Exfiltration"},
    "T1567.002": {"name": "Exfiltration to Cloud Storage", "tactic": "Exfiltration"},
    "T1048": {"name": "Exfiltration Over Alternative Protocol", "tactic": "Exfiltration"},
    "T1020": {"name": "Automated Exfiltration", "tactic": "Exfiltration"},
    
    # Impact
    "T1486": {"name": "Data Encrypted for Impact", "tactic": "Impact"},
    "T1490": {"name": "Inhibit System Recovery", "tactic": "Impact"},
    "T1489": {"name": "Service Stop", "tactic": "Impact"},
    "T1485": {"name": "Data Destruction", "tactic": "Impact"},
    "T1491": {"name": "Defacement", "tactic": "Impact"},
    "T1529": {"name": "System Shutdown/Reboot", "tactic": "Impact"},
}

# Tactic order for kill chain
TACTIC_ORDER = [
    "Reconnaissance",
    "Resource Development",
    "Initial Access",
    "Execution",
    "Persistence",
    "Privilege Escalation",
    "Defense Evasion",
    "Credential Access",
    "Discovery",
    "Lateral Movement",
    "Collection",
    "Command and Control",
    "Exfiltration",
    "Impact",
]


@dataclass
class TechniqueMapping:
    """Represents a mapping of a finding to a MITRE technique."""
    
    technique_id: str
    technique_name: str
    tactic: str
    confidence: float = 0.5
    evidence_refs: list[str] = field(default_factory=list)
    finding_refs: list[str] = field(default_factory=list)
    description: str = ""
    timestamp: str | None = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "technique_id": self.technique_id,
            "technique_name": self.technique_name,
            "tactic": self.tactic,
            "confidence": self.confidence,
            "evidence_refs": self.evidence_refs,
            "finding_refs": self.finding_refs,
            "description": self.description,
            "timestamp": self.timestamp,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "TechniqueMapping":
        """Create TechniqueMapping from dictionary."""
        return cls(
            technique_id=data.get("technique_id", ""),
            technique_name=data.get("technique_name", ""),
            tactic=data.get("tactic", ""),
            confidence=data.get("confidence", 0.5),
            evidence_refs=data.get("evidence_refs", []),
            finding_refs=data.get("finding_refs", []),
            description=data.get("description", ""),
            timestamp=data.get("timestamp"),
        )


class MITREMapper:
    """Maps investigation findings to MITRE ATT&CK framework."""
    
    def __init__(self, case_dir: Path):
        """Initialize MITRE mapper for a case."""
        self.case_dir = Path(case_dir)
        self.mapping_dir = self.case_dir / "analysis" / "mitre"
        self.mapping_file = self.mapping_dir / "technique_mappings.json"
        
        # Create directories
        self.mapping_dir.mkdir(parents=True, exist_ok=True)
        
        # Load or create mappings
        self.mappings: dict[str, TechniqueMapping] = {}
        self._load_mappings()
    
    def _load_mappings(self):
        """Load mappings from file."""
        if self.mapping_file.exists():
            with open(self.mapping_file) as f:
                data = json.load(f)
                for mapping_data in data.get("mappings", []):
                    mapping = TechniqueMapping.from_dict(mapping_data)
                    self.mappings[mapping.technique_id] = mapping
    
    def _save_mappings(self):
        """Save mappings to file."""
        data = {
            "case_dir": str(self.case_dir),
            "updated_at": datetime.now().isoformat(),
            "mapping_count": len(self.mappings),
            "mappings": [m.to_dict() for m in self.mappings.values()],
        }
        with open(self.mapping_file, "w") as f:
            json.dump(data, f, indent=2)
    
    def get_technique_info(self, technique_id: str) -> dict | None:
        """Get information about a MITRE technique."""
        return MITRE_TECHNIQUES.get(technique_id)
    
    def add_mapping(
        self,
        technique_id: str,
        confidence: float = 0.5,
        evidence_refs: list[str] | None = None,
        finding_refs: list[str] | None = None,
        description: str = "",
    ) -> TechniqueMapping | None:
        """
        Add a technique mapping.
        
        Args:
            technique_id: MITRE technique ID (e.g., T1059.001)
            confidence: Confidence level (0.0-1.0)
            evidence_refs: Evidence sources supporting this mapping
            finding_refs: Finding IDs supporting this mapping
            description: Description of how technique was observed
            
        Returns:
            TechniqueMapping if valid, None if technique not found
        """
        technique_info = self.get_technique_info(technique_id)
        if not technique_info:
            return None
        
        # Check if mapping already exists
        if technique_id in self.mappings:
            # Update existing mapping
            existing = self.mappings[technique_id]
            if evidence_refs:
                existing.evidence_refs.extend(evidence_refs)
                existing.evidence_refs = list(set(existing.evidence_refs))
            if finding_refs:
                existing.finding_refs.extend(finding_refs)
                existing.finding_refs = list(set(existing.finding_refs))
            # Update confidence (take higher)
            existing.confidence = max(existing.confidence, confidence)
            if description:
                existing.description = f"{existing.description}; {description}".strip("; ")
            self._save_mappings()
            return existing
        
        # Create new mapping
        mapping = TechniqueMapping(
            technique_id=technique_id,
            technique_name=technique_info["name"],
            tactic=technique_info["tactic"],
            confidence=confidence,
            evidence_refs=evidence_refs or [],
            finding_refs=finding_refs or [],
            description=description,
            timestamp=datetime.now().isoformat(),
        )
        
        self.mappings[technique_id] = mapping
        self._save_mappings()
        
        return mapping
    
    def get_mappings_by_tactic(self, tactic: str) -> list[TechniqueMapping]:
        """Get all mappings for a specific tactic."""
        return [m for m in self.mappings.values() if m.tactic == tactic]
    
    def get_kill_chain(self) -> dict[str, list[TechniqueMapping]]:
        """Get mappings organized by kill chain phase."""
        kill_chain = {tactic: [] for tactic in TACTIC_ORDER}
        
        for mapping in self.mappings.values():
            if mapping.tactic in kill_chain:
                kill_chain[mapping.tactic].append(mapping)
        
        return kill_chain
    
    def generate_navigator_layer(self, output_path: Path | None = None) -> dict:
        """
        Generate ATT&CK Navigator layer JSON.
        
        Args:
            output_path: Optional path to save layer
            
        Returns:
            Navigator layer dictionary
        """
        techniques = []
        
        for mapping in self.mappings.values():
            # Color based on confidence
            if mapping.confidence >= 0.8:
                color = "#ff6666"  # Red - high confidence
            elif mapping.confidence >= 0.5:
                color = "#ffcc66"  # Orange - medium confidence
            else:
                color = "#ffff66"  # Yellow - low confidence
            
            techniques.append({
                "techniqueID": mapping.technique_id,
                "color": color,
                "comment": mapping.description,
                "enabled": True,
                "metadata": [
                    {"name": "confidence", "value": str(mapping.confidence)},
                    {"name": "evidence", "value": ", ".join(mapping.evidence_refs)},
                ],
                "score": int(mapping.confidence * 100),
            })
        
        layer = {
            "name": f"Auto-DFIR - {self.case_dir.name}",
            "versions": {
                "attack": "14",
                "navigator": "4.9.1",
                "layer": "4.5",
            },
            "domain": "enterprise-attack",
            "description": f"MITRE ATT&CK mapping for case {self.case_dir.name}",
            "filters": {
                "platforms": ["Windows", "Linux", "macOS", "Azure AD", "Office 365", "SaaS"]
            },
            "sorting": 0,
            "layout": {
                "layout": "side",
                "aggregateFunction": "average",
                "showID": True,
                "showName": True,
            },
            "hideDisabled": False,
            "techniques": techniques,
            "gradient": {
                "colors": ["#ffffff", "#ff6666"],
                "minValue": 0,
                "maxValue": 100,
            },
            "legendItems": [
                {"label": "High Confidence (>80%)", "color": "#ff6666"},
                {"label": "Medium Confidence (50-80%)", "color": "#ffcc66"},
                {"label": "Low Confidence (<50%)", "color": "#ffff66"},
            ],
            "metadata": [
                {"name": "case_id", "value": self.case_dir.name},
                {"name": "generated_at", "value": datetime.now().isoformat()},
                {"name": "generator", "value": "Auto-DFIR"},
            ],
            "showTacticRowBackground": True,
            "tacticRowBackground": "#dddddd",
            "selectTechniquesAcrossTactics": True,
            "selectSubtechniquesWithParent": False,
        }
        
        if output_path:
            with open(output_path, "w") as f:
                json.dump(layer, f, indent=2)
        
        return layer
    
    def get_statistics(self) -> dict:
        """Get mapping statistics."""
        stats = {
            "total_techniques": len(self.mappings),
            "by_tactic": {},
            "average_confidence": 0,
            "high_confidence_count": 0,
            "tactics_covered": 0,
        }
        
        if not self.mappings:
            return stats
        
        total_confidence = 0
        tactics_seen = set()
        
        for mapping in self.mappings.values():
            # By tactic
            stats["by_tactic"][mapping.tactic] = stats["by_tactic"].get(mapping.tactic, 0) + 1
            tactics_seen.add(mapping.tactic)
            
            # Confidence
            total_confidence += mapping.confidence
            if mapping.confidence >= 0.8:
                stats["high_confidence_count"] += 1
        
        stats["average_confidence"] = round(total_confidence / len(self.mappings), 2)
        stats["tactics_covered"] = len(tactics_seen)
        
        return stats
    
    def suggest_techniques(self, keywords: list[str]) -> list[dict]:
        """
        Suggest MITRE techniques based on keywords.
        
        Args:
            keywords: Keywords to match against technique names
            
        Returns:
            List of matching techniques
        """
        suggestions = []
        keywords_lower = [k.lower() for k in keywords]
        
        for tech_id, tech_info in MITRE_TECHNIQUES.items():
            name_lower = tech_info["name"].lower()
            if any(kw in name_lower for kw in keywords_lower):
                suggestions.append({
                    "technique_id": tech_id,
                    "name": tech_info["name"],
                    "tactic": tech_info["tactic"],
                })
        
        return suggestions
