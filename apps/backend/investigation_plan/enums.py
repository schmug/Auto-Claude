"""
Investigation Plan Enums
========================

Enumerations for DFIR investigation plan types and statuses.
"""

from enum import Enum


class CaseType(str, Enum):
    """Type of DFIR case/investigation."""
    
    # Incident types
    MALWARE = "malware"
    RANSOMWARE = "ransomware"
    PHISHING = "phishing"
    DATA_BREACH = "data_breach"
    INSIDER_THREAT = "insider_threat"
    APT = "apt"
    BUSINESS_EMAIL_COMPROMISE = "bec"
    DENIAL_OF_SERVICE = "dos"
    WEB_COMPROMISE = "web_compromise"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    
    # Investigation types
    TRIAGE = "triage"
    FULL_INVESTIGATION = "full_investigation"
    THREAT_HUNT = "threat_hunt"
    COMPLIANCE_AUDIT = "compliance_audit"
    VULNERABILITY_ASSESSMENT = "vulnerability_assessment"
    
    # Other
    UNKNOWN = "unknown"


class EvidenceType(str, Enum):
    """Type of digital evidence."""
    
    # Disk/File evidence
    DISK_IMAGE = "disk_image"
    MEMORY_DUMP = "memory_dump"
    FILE_SYSTEM = "file_system"
    REGISTRY = "registry"
    
    # Log evidence
    WINDOWS_EVENT_LOG = "windows_event_log"
    SYSLOG = "syslog"
    APPLICATION_LOG = "application_log"
    SECURITY_LOG = "security_log"
    WEB_SERVER_LOG = "web_server_log"
    DATABASE_LOG = "database_log"
    
    # Network evidence
    PCAP = "pcap"
    NETFLOW = "netflow"
    FIREWALL_LOG = "firewall_log"
    PROXY_LOG = "proxy_log"
    DNS_LOG = "dns_log"
    
    # Endpoint evidence
    EDR_TELEMETRY = "edr_telemetry"
    PROCESS_LIST = "process_list"
    NETWORK_CONNECTIONS = "network_connections"
    SCHEDULED_TASKS = "scheduled_tasks"
    SERVICES = "services"
    AUTORUNS = "autoruns"
    
    # Cloud evidence
    CLOUD_TRAIL = "cloud_trail"
    AZURE_AD_LOG = "azure_ad_log"
    O365_AUDIT = "o365_audit"
    
    # Email evidence
    EMAIL_HEADERS = "email_headers"
    EMAIL_BODY = "email_body"
    EMAIL_ATTACHMENT = "email_attachment"
    
    # Other
    MALWARE_SAMPLE = "malware_sample"
    SCREENSHOT = "screenshot"
    OTHER = "other"


class InvestigationPhaseType(str, Enum):
    """Type of investigation phase."""
    
    # Standard DFIR phases
    INTAKE = "intake"
    EVIDENCE_COLLECTION = "evidence_collection"
    EVIDENCE_PRESERVATION = "evidence_preservation"
    ANALYSIS = "analysis"
    IOC_EXTRACTION = "ioc_extraction"
    TIMELINE_RECONSTRUCTION = "timeline_reconstruction"
    THREAT_INTEL_ENRICHMENT = "threat_intel_enrichment"
    MITRE_MAPPING = "mitre_mapping"
    VALIDATION = "validation"
    REPORTING = "reporting"
    REMEDIATION = "remediation"
    
    # Specialized phases
    MEMORY_ANALYSIS = "memory_analysis"
    NETWORK_ANALYSIS = "network_analysis"
    MALWARE_ANALYSIS = "malware_analysis"
    LOG_ANALYSIS = "log_analysis"
    REGISTRY_ANALYSIS = "registry_analysis"
    
    # Meta phases
    PLANNING = "planning"
    REVIEW = "review"


class InvestigationStepStatus(str, Enum):
    """Status of an investigation step."""
    
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    SKIPPED = "skipped"
    NEEDS_REVIEW = "needs_review"


class FindingSeverity(str, Enum):
    """Severity level for investigation findings."""
    
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"


class IOCType(str, Enum):
    """Type of Indicator of Compromise."""
    
    # Network IOCs
    IP_ADDRESS = "ip_address"
    DOMAIN = "domain"
    URL = "url"
    EMAIL_ADDRESS = "email_address"
    
    # File IOCs
    FILE_HASH_MD5 = "file_hash_md5"
    FILE_HASH_SHA1 = "file_hash_sha1"
    FILE_HASH_SHA256 = "file_hash_sha256"
    FILE_NAME = "file_name"
    FILE_PATH = "file_path"
    
    # Host IOCs
    REGISTRY_KEY = "registry_key"
    REGISTRY_VALUE = "registry_value"
    PROCESS_NAME = "process_name"
    SERVICE_NAME = "service_name"
    SCHEDULED_TASK = "scheduled_task"
    MUTEX = "mutex"
    
    # Behavioral IOCs
    COMMAND_LINE = "command_line"
    USER_AGENT = "user_agent"
    JA3_HASH = "ja3_hash"
    JA3S_HASH = "ja3s_hash"
    
    # Other
    CVE = "cve"
    YARA_RULE = "yara_rule"
    SIGMA_RULE = "sigma_rule"


class ChainOfCustodyAction(str, Enum):
    """Actions tracked in chain of custody."""
    
    COLLECTED = "collected"
    TRANSFERRED = "transferred"
    RECEIVED = "received"
    ANALYZED = "analyzed"
    COPIED = "copied"
    EXPORTED = "exported"
    STORED = "stored"
    RETURNED = "returned"
    DESTROYED = "destroyed"
