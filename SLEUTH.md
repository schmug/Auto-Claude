# SLEUTH.md

This file provides guidance to AI agents when working with Auto-Sleuth DFIR investigations.

## Project Overview

Auto-Sleuth is a multi-agent autonomous Digital Forensics and Incident Response (DFIR) framework that conducts investigations through coordinated AI agent sessions. It uses the Claude Agent SDK to run agents in isolated workspaces with security controls.

**CRITICAL: All AI interactions use the Claude Agent SDK (`claude-agent-sdk` package), NOT the Anthropic API directly.**

## DFIR Focus

This tool is designed for digital forensics investigations, not software development:

- **Cases** replace "Specs" - Investigation definitions
- **Analysis Tasks** replace "Subtasks" - Forensic analysis steps
- **Evidence Sources** replace "Services" - Network, memory, endpoint, logs

## Key DFIR Principles

1. **Evidence Integrity**: Original evidence must NEVER be modified. All analysis outputs go to `./outputs/`
2. **Chain of Custody**: Document all evidence handling with timestamps and analyst attribution
3. **IOC Hunting**: Systematically search for indicators of compromise across evidence sources
4. **MITRE ATT&CK**: Map findings to MITRE ATT&CK techniques for standardized reporting

## Project Structure

```
auto-sleuth/
├── apps/
│   ├── backend/           # Python backend/CLI - ALL agent logic lives here
│   │   ├── core/          # Client, auth, security
│   │   ├── agents/        # Agent implementations
│   │   ├── spec_agents/   # Case creation agents
│   │   ├── integrations/  # Graphiti, Linear, GitHub
│   │   └── prompts/       # Agent system prompts (DFIR-focused)
│   └── frontend/          # Electron desktop UI
├── dfiq/                  # Google DFIQ framework (97 questions)
├── guides/                # Documentation
├── tests/                 # Test suite
└── scripts/               # Build and utility scripts
```

## Investigation Workflow

### Creating Cases

```bash
cd apps/backend

# Create a case interactively
python spec_runner.py --interactive

# Create case from incident description
python spec_runner.py --task "Investigate suspicious PowerShell execution"

# Force severity level (triage/low/medium/high/critical)
python spec_runner.py --task "Check for IOC" --complexity triage

# Run autonomous investigation
python run.py --spec 001

# List all cases
python run.py --list
```

### Case Directory Structure

```
.auto-sleuth/cases/001-incident-name/
├── case.md                    # Investigation definition
├── case_intake.json           # Incident details
├── investigation_plan.json    # Analysis phases and tasks
├── context.json               # Evidence index, patterns
├── investigation-progress.txt # Session-by-session notes
├── iocs/                      # IOC files
│   └── all_iocs.txt           # Master IOC list
├── outputs/                   # Analysis results (NEVER in evidence dir)
│   ├── phase-1/
│   │   ├── findings.json
│   │   └── timeline.csv
│   └── ioc_hits/
│       └── network_hits.json
└── memory/                    # Agent memory
```

## Evidence Types

The framework supports these evidence sources:

| Source       | Common Artifacts                 | Tools                  |
| ------------ | -------------------------------- | ---------------------- |
| **Network**  | PCAP, Zeek logs, NetFlow         | Zeek, tshark, Suricata |
| **Memory**   | RAM dumps, hibernation files     | Volatility3, Rekall    |
| **Endpoint** | Disk images, triage packages     | Autopsy, Plaso         |
| **Logs**     | Windows EVTX, syslog, cloud logs | Chainsaw, Sigma        |

## DFIQ Integration

The `dfiq/` directory contains Google's Digital Forensics Investigative Questions framework:

```python
from dfiq import DFIQ

dfiq = DFIQ(yaml_data_path='./dfiq')

# Find approaches for investigating browser downloads
question = dfiq.components.get("Q1001")
print(f"Question: {question.name}")
for approach_id in question.approaches:
    approach = dfiq.components.get(approach_id)
    print(f"  - {approach.name}")
```

## Agent Roles

| Agent                        | Purpose                                            |
| ---------------------------- | -------------------------------------------------- |
| **Investigation Planner**    | Creates analysis phases and tasks                  |
| **Evidence Analyzer**        | Executes forensic analysis (read-only on evidence) |
| **Evidence Validator**       | Validates findings, chain of custody               |
| **Severity Assessor**        | Determines investigation complexity                |
| **Case Intake**              | Gathers incident details                           |
| **Case Writer**              | Creates `case.md` document                         |
| **Threat Insight Extractor** | Extracts IOCs and attack patterns                  |

## Critical Rules

1. **Never modify original evidence** - Work only in `./outputs/`
2. **Verify hashes** - Check evidence integrity before analysis
3. **Document everything** - Chain of custody is paramount
4. **Use DFIQ** - Consult for standard investigation approaches
5. **Map to MITRE** - Link findings to ATT&CK techniques
