# DFIR Research Notes

## Core DFIR Concepts

### DFIR Definition
Digital Forensics and Incident Response (DFIR) combines two cybersecurity disciplines:
1. **Digital Forensics**: Investigation of cyberthreats to gather digital evidence for litigation
2. **Incident Response**: Detection and mitigation of cyberattacks in progress

### Key DFIR Phases (NIST Framework)

#### Digital Forensics Steps:
1. **Data Collection** - Collect from OS, user accounts, mobile devices, hardware/software
   - File system forensics
   - Memory forensics (RAM)
   - Network forensics
   - Application forensics
2. **Examination** - Comb through data for signs of cybercriminal activity
3. **Analysis** - Process, correlate, extract insights; reference threat intelligence
4. **Reporting** - Compile report explaining what happened, identify suspects

#### Incident Response Steps:
1. **Preparation** - Assess risks, identify vulnerabilities, draft IRPs
2. **Detection and Analysis** - Monitor network, analyze data, triage alerts
3. **Containment** - Stop threat from spreading
4. **Eradication** - Remove threat from network
5. **Recovery** - Restore damaged systems
6. **Post-incident Review** - Understand breach, prepare for future

### Evidence Types & Artifacts

#### Indicators of Compromise (IOCs):
- Maliciously used IP addresses
- URLs and domains
- File hashes (MD5, SHA1, SHA256)
- Registry keys
- Unusual network traffic patterns
- Unauthorized access attempts
- Malware signatures
- Command and control (C2) communications
- Suspicious process executions
- Abnormal user behavior

#### Forensic Artifact Categories:
- **File System**: Files, folders, deleted data, metadata
- **Memory**: Running processes, network connections, encryption keys
- **Network**: Traffic logs, DNS queries, connection records
- **Application**: Logs, configuration files, user data
- **Registry**: System configuration, user activity, installed software
- **Browser**: History, cookies, cache, downloads
- **Email**: Headers, attachments, metadata

### Chain of Custody

**Definition**: Process for tracking how evidence is gathered, handled, and transferred

**Key Requirements**:
- Document every person who handles evidence
- Record dates, times, and locations of transfers
- Maintain evidence integrity (hashes)
- Secure original evidence, work on copies
- Create permanent records (forms)
- Prove evidence wasn't tampered with

**Chain of Custody Form Elements**:
- Case/incident identifier
- Evidence description
- Collection date/time/location
- Collector information
- Transfer records (who, when, why)
- Storage location
- Hash values for integrity verification

### Timeline Analysis

**Purpose**: Reconstruct sequence of events during an incident

**Key Components**:
- Aggregate timestamps from multiple sources
- Correlate events across different artifact types
- Identify anomalies and suspicious patterns
- Establish attack timeline (initial access → lateral movement → exfiltration)

## DFIR Tools Categories

1. **SIEM** - Security Information and Event Management
2. **SOAR** - Security Orchestration, Automation, and Response
3. **EDR** - Endpoint Detection and Response
4. **XDR** - Extended Detection and Response
5. **Forensic Analysis Tools** - Disk imaging, memory analysis, network capture
6. **Threat Intelligence Platforms** - IOC databases, threat feeds

## Mapping to Auto-Claude Architecture

### Current Auto-Claude → DFIR Equivalent

| Auto-Claude Component | DFIR Equivalent |
|----------------------|-----------------|
| Task/Spec | Case/Investigation |
| Planner Agent | Investigation Planner |
| Coder Agent | Evidence Analyzer |
| QA Reviewer | Evidence Validator |
| Subtasks | Investigation Steps |
| Build Progress | Investigation Timeline |
| Implementation Plan | Investigation Plan |
| Worktree | Evidence Workspace |
| Memory/Context | Case Knowledge Base |

### Workflow Mapping

| Auto-Claude Workflow | DFIR Workflow |
|---------------------|---------------|
| Feature Development | Full Investigation |
| Bug Investigation | Incident Analysis |
| Refactoring | Evidence Re-analysis |
| Simple Task | Quick Triage |

