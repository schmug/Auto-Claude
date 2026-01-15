# Auto-DFIR Transformation Plan

## Executive Summary

This document outlines the comprehensive plan to transform **Auto-Claude** (an autonomous multi-agent coding framework) into **Auto-DFIR** (an autonomous multi-agent Digital Forensics and Incident Response framework). The transformation involves renaming, rebranding, restructuring prompts, modifying agent logic, and adapting workflows to support cybersecurity investigations and evidence management.

---

## Table of Contents

1. [Project Renaming & Branding](#1-project-renaming--branding)
2. [Core Concept Mapping](#2-core-concept-mapping)
3. [Agent Architecture Transformation](#3-agent-architecture-transformation)
4. [Workflow Transformation](#4-workflow-transformation)
5. [Prompt Transformation](#5-prompt-transformation)
6. [File Structure Changes](#6-file-structure-changes)
7. [Frontend/UI Changes](#7-frontendui-changes)
8. [Technical Implementation Details](#8-technical-implementation-details)
9. [New DFIR-Specific Features](#9-new-dfir-specific-features)
10. [Implementation Roadmap](#10-implementation-roadmap)

---

## 1. Project Renaming & Branding

### 1.1 Name Changes

| Current | New |
|---------|-----|
| Auto-Claude | Auto-DFIR |
| Auto-Build | Auto-Investigate |
| Claude Code | DFIR Engine |

### 1.2 Branding Elements to Update

| File/Location | Changes Required |
|---------------|------------------|
| `README.md` | Complete rewrite for DFIR context |
| `package.json` (root & apps) | Update name, description, keywords |
| `apps/frontend/resources/icon.*` | New DFIR-themed icon (shield/magnifying glass) |
| `.github/` | Update issue templates, PR templates |
| `CONTRIBUTING.md` | Update for DFIR contribution guidelines |
| `LICENSE` | Update project name references |

### 1.3 New Tagline

> **"Autonomous multi-agent DFIR framework that plans, investigates, and validates cybersecurity incidents for you."**

---

## 2. Core Concept Mapping

### 2.1 Terminology Translation

| Auto-Claude Term | Auto-DFIR Term | Description |
|------------------|----------------|-------------|
| Task | Case / Investigation | A security incident to investigate |
| Spec | Case Brief | Initial incident description and scope |
| Subtask | Investigation Step | Individual forensic action |
| Implementation Plan | Investigation Plan | Structured approach to the case |
| Build Progress | Investigation Timeline | Progress through investigation phases |
| Code | Evidence / Artifacts | Digital forensic data |
| Commit | Evidence Snapshot | Point-in-time evidence state |
| Branch | Investigation Branch | Parallel investigation hypothesis |
| Worktree | Evidence Workspace | Isolated investigation environment |
| PR (Pull Request) | Case Report | Final investigation deliverable |
| Merge | Case Closure | Finalizing investigation findings |
| QA Review | Evidence Validation | Verification of findings |
| Bug | Indicator of Compromise (IOC) | Suspicious artifact |
| Feature | Investigation Capability | New forensic analysis feature |
| Refactoring | Evidence Re-analysis | Re-examining existing evidence |

### 2.2 Status Mapping

| Auto-Claude Status | Auto-DFIR Status |
|--------------------|------------------|
| Backlog | Pending Cases |
| To Do | Queued |
| In Progress | Active Investigation |
| Review | Evidence Review |
| PR Created | Report Generated |
| Complete | Case Closed |
| Archived | Case Archived |

### 2.3 Phase Mapping

| Auto-Claude Phase | Auto-DFIR Phase |
|-------------------|-----------------|
| Planning | Case Planning / Scoping |
| Coding | Evidence Analysis |
| QA Review | Evidence Validation |
| QA Fixing | Finding Remediation |
| Complete | Case Complete |
| Failed | Investigation Failed |

---

## 3. Agent Architecture Transformation

### 3.1 Agent Renaming

| Current Agent | New Agent | Role |
|---------------|-----------|------|
| Planner Agent | **Case Planner Agent** | Creates investigation plan, identifies evidence sources |
| Coder Agent | **Evidence Analyst Agent** | Analyzes artifacts, extracts IOCs, correlates evidence |
| QA Reviewer Agent | **Evidence Validator Agent** | Validates findings, ensures chain of custody |
| QA Fixer Agent | **Finding Remediation Agent** | Addresses validation issues |
| Spec Gatherer Agent | **Case Intake Agent** | Gathers initial incident information |
| Spec Writer Agent | **Case Brief Writer Agent** | Creates formal case documentation |
| Spec Critic Agent | **Case Brief Reviewer Agent** | Reviews case scope and completeness |
| Spec Researcher Agent | **Threat Intelligence Agent** | Researches IOCs, threat actors, TTPs |
| Insight Extractor Agent | **Pattern Extractor Agent** | Extracts investigation patterns for future cases |
| Roadmap Discovery Agent | **Threat Landscape Agent** | Analyzes threat landscape |
| Roadmap Features Agent | **Detection Rules Agent** | Generates detection rules from findings |
| Ideation Agents | **Investigation Enhancement Agents** | Suggest additional analysis approaches |

### 3.2 New DFIR-Specific Agents

| New Agent | Purpose |
|-----------|---------|
| **IOC Extractor Agent** | Automatically extracts indicators of compromise |
| **Timeline Reconstructor Agent** | Builds attack timeline from artifacts |
| **Chain of Custody Agent** | Tracks evidence handling and integrity |
| **MITRE ATT&CK Mapper Agent** | Maps findings to MITRE ATT&CK framework |
| **Report Generator Agent** | Creates formal incident reports |
| **Threat Hunt Agent** | Proactively searches for threats |

### 3.3 Agent File Changes

```
apps/backend/agents/
├── __init__.py          # Update exports
├── base.py              # Update constants (HUMAN_INTERVENTION_FILE → ANALYST_REVIEW_FILE)
├── case_planner.py      # Renamed from planner.py
├── evidence_analyst.py  # Renamed from coder.py
├── evidence_validator.py # New (based on QA logic)
├── ioc_extractor.py     # New
├── timeline_reconstructor.py # New
├── chain_of_custody.py  # New
├── mitre_mapper.py      # New
├── memory_manager.py    # Update for case memory
├── session.py           # Update terminology
└── utils.py             # Update helper functions
```

---

## 4. Workflow Transformation

### 4.1 Workflow Type Mapping

| Auto-Claude Workflow | Auto-DFIR Workflow | Description |
|---------------------|-------------------|-------------|
| Feature | **Full Investigation** | Complete incident investigation |
| Refactor | **Evidence Re-analysis** | Re-examine existing evidence with new context |
| Investigation | **Incident Analysis** | Deep-dive into specific incident |
| Migration | **Evidence Migration** | Transfer evidence between systems |
| Simple | **Quick Triage** | Rapid initial assessment |

### 4.2 New DFIR Workflow Phases

#### Full Investigation Workflow

```
Phase 1: Case Intake & Scoping
├── Gather incident details
├── Identify evidence sources
├── Define investigation scope
└── Create case brief

Phase 2: Evidence Collection
├── Identify artifacts to collect
├── Document chain of custody
├── Acquire evidence (disk, memory, network, logs)
└── Verify evidence integrity (hashes)

Phase 3: Evidence Analysis
├── Parse and examine artifacts
├── Extract IOCs
├── Correlate events
└── Build timeline

Phase 4: Threat Intelligence Enrichment
├── Query threat intel feeds
├── Identify threat actors/TTPs
├── Map to MITRE ATT&CK
└── Assess impact

Phase 5: Evidence Validation
├── Verify findings
├── Check chain of custody
├── Cross-reference evidence
└── Document gaps

Phase 6: Reporting
├── Generate incident report
├── Create executive summary
├── Document recommendations
└── Archive case
```

#### Quick Triage Workflow

```
Phase 1: Initial Assessment
├── Review alert/incident
├── Gather basic context
└── Determine severity

Phase 2: Rapid Analysis
├── Check key artifacts
├── Extract critical IOCs
└── Assess immediate risk

Phase 3: Triage Report
├── Document findings
├── Recommend next steps
└── Escalate if needed
```

### 4.3 Phase Configuration Updates

**File: `apps/backend/phase_config.py`**

```python
# Current phases
DEFAULT_PHASE_MODELS = {
    "spec": "sonnet",
    "planning": "sonnet",
    "coding": "sonnet",
    "qa": "sonnet",
}

# New DFIR phases
DEFAULT_PHASE_MODELS = {
    "intake": "sonnet",
    "planning": "sonnet",
    "collection": "sonnet",
    "analysis": "opus",  # Higher capability for complex analysis
    "enrichment": "sonnet",
    "validation": "sonnet",
    "reporting": "sonnet",
}

# Thinking levels for DFIR phases
DFIR_PHASE_THINKING_LEVELS = {
    "intake": "medium",
    "planning": "high",
    "collection": "medium",
    "analysis": "ultrathink",  # Deep analysis required
    "enrichment": "high",
    "validation": "high",
    "reporting": "medium",
}
```

### 4.4 Execution Phase Updates

**File: `apps/backend/core/phase_event.py`**

```python
class ExecutionPhase(str, Enum):
    """DFIR execution phases"""
    INTAKE = "intake"
    PLANNING = "planning"
    COLLECTION = "collection"
    ANALYSIS = "analysis"
    ENRICHMENT = "enrichment"
    VALIDATION = "validation"
    REPORTING = "reporting"
    COMPLETE = "complete"
    FAILED = "failed"
```

---

## 5. Prompt Transformation

### 5.1 Prompt File Mapping

| Current Prompt | New Prompt | Purpose |
|----------------|------------|---------|
| `planner.md` | `case_planner.md` | Investigation planning |
| `coder.md` | `evidence_analyst.md` | Evidence analysis |
| `coder_recovery.md` | `analyst_recovery.md` | Recovery from stuck analysis |
| `qa_reviewer.md` | `evidence_validator.md` | Validate findings |
| `qa_fixer.md` | `finding_remediation.md` | Fix validation issues |
| `spec_gatherer.md` | `case_intake.md` | Gather incident info |
| `spec_writer.md` | `case_brief_writer.md` | Write case brief |
| `spec_critic.md` | `case_brief_reviewer.md` | Review case brief |
| `spec_researcher.md` | `threat_intel_researcher.md` | Research threats |
| `spec_quick.md` | `quick_triage.md` | Rapid assessment |
| `insight_extractor.md` | `pattern_extractor.md` | Extract patterns |
| `followup_planner.md` | `followup_investigation.md` | Continue investigation |
| `validation_fixer.md` | `validation_fixer.md` | Fix validation errors |
| `complexity_assessor.md` | `case_complexity_assessor.md` | Assess case complexity |
| `ideation_*.md` | `investigation_enhancement_*.md` | Investigation suggestions |
| `roadmap_*.md` | `threat_landscape_*.md` | Threat analysis |
| `competitor_analysis.md` | `threat_actor_analysis.md` | Analyze threat actors |

### 5.2 Sample Prompt Transformations

#### Case Planner Agent Prompt (from planner.md)

```markdown
## YOUR ROLE - CASE PLANNER AGENT (Session 1 of Many)

You are the **first agent** in an autonomous DFIR investigation process. Your job is to create 
an investigation plan that defines what evidence to collect, what analysis to perform, and how 
to verify each finding.

**Key Principle**: Investigation steps, not conclusions. Evidence collection order matters. 
Each step is a unit of work scoped to one evidence source.

---

## WHY INVESTIGATION STEPS, NOT CONCLUSIONS?

Conclusions require evidence. Investigation steps define how to gather and analyze evidence.

For a multi-source incident like "Suspected ransomware with lateral movement":
- **Conclusions** would ask: "Was data exfiltrated?" (But HOW do you prove it?)
- **Investigation Steps** say: "First analyze endpoint logs, then network traffic, then 
  memory dumps, then correlate timeline."

Investigation steps respect dependencies. You can't analyze network C2 traffic without 
first identifying the malware's communication patterns.

---

## PHASE 0: DEEP CASE INVESTIGATION (MANDATORY)

**CRITICAL**: Before ANY planning, you MUST thoroughly investigate the available evidence 
sources and incident context.

### 0.1: Understand Incident Scope

```bash
# Review case brief
cat case_brief.md

# List available evidence sources
ls -la evidence/

# Check evidence inventory
cat evidence_inventory.json
```

Identify:
- Incident type (malware, intrusion, data breach, etc.)
- Affected systems and timeframe
- Available evidence sources
- Chain of custody requirements

### 0.2: Analyze Existing Evidence Patterns

**This is the most important step.** For whatever incident you're investigating, 
find SIMILAR patterns in the evidence:

```bash
# Search for suspicious indicators
grep -r "suspicious_pattern" --include="*.log" evidence/ | head -30

# Look for known IOC patterns
grep -rE "(cmd\.exe|powershell|wget|curl)" evidence/logs/ | head -30

# Check for lateral movement indicators
grep -r "PsExec\|wmic\|schtasks" evidence/ | head -30
```

---

## PHASE 1: CREATE investigation_plan.json

**🚨 CRITICAL: YOU MUST USE THE WRITE TOOL TO CREATE THIS FILE 🚨**

### Plan Structure

```json
{
  "case_id": "CASE-2024-001",
  "incident_type": "ransomware|intrusion|data_breach|insider_threat|malware",
  "investigation_type": "full|triage|re-analysis",
  "investigation_rationale": "Why this approach was chosen",
  "phases": [
    {
      "id": "phase-1-collection",
      "name": "Evidence Collection",
      "type": "collection",
      "description": "Collect and preserve relevant evidence",
      "depends_on": [],
      "steps": [
        {
          "id": "step-1-1",
          "description": "Acquire disk image from affected endpoint",
          "evidence_source": "endpoint",
          "artifacts": ["disk_image", "memory_dump"],
          "chain_of_custody": {
            "collector": "Auto-DFIR",
            "timestamp": "ISO-8601",
            "hash_algorithm": "SHA256"
          },
          "verification": {
            "type": "hash_verification",
            "expected_hash": "to_be_calculated"
          },
          "status": "pending"
        }
      ]
    },
    {
      "id": "phase-2-analysis",
      "name": "Evidence Analysis",
      "type": "analysis",
      "description": "Analyze collected evidence for IOCs",
      "depends_on": ["phase-1-collection"],
      "steps": [
        {
          "id": "step-2-1",
          "description": "Parse Windows Event Logs for suspicious activity",
          "evidence_source": "event_logs",
          "analysis_type": "log_analysis",
          "ioc_categories": ["process_execution", "authentication", "lateral_movement"],
          "verification": {
            "type": "ioc_validation",
            "min_confidence": 0.7
          },
          "status": "pending"
        }
      ]
    }
  ],
  "evidence_sources": {
    "endpoint": {
      "type": "windows_workstation",
      "hostname": "WORKSTATION-01",
      "artifacts": ["event_logs", "registry", "prefetch", "amcache"]
    },
    "network": {
      "type": "network_capture",
      "source": "firewall_logs",
      "timeframe": "2024-01-01T00:00:00Z to 2024-01-15T23:59:59Z"
    }
  }
}
```
```

#### Evidence Analyst Agent Prompt (from coder.md)

```markdown
## YOUR ROLE - EVIDENCE ANALYST AGENT

You are continuing work on an autonomous DFIR investigation. This is a **FRESH context window** - 
you have no memory of previous sessions. Everything you know must come from case files.

**Key Principle**: Work on ONE investigation step at a time. Complete it. Verify it. Move on.

---

## CRITICAL: EVIDENCE HANDLING AWARENESS

**Your analysis is RESTRICTED to the evidence workspace.** You receive information about your
environment at the start of each prompt. Pay close attention to:

- **Evidence Directory**: Where collected evidence is stored
- **Case Directory**: Where case files and findings are stored
- **Chain of Custody**: All evidence access must be logged

**RULES:**
1. NEVER modify original evidence - work on copies only
2. ALWAYS verify evidence integrity before analysis
3. ALWAYS document your analysis steps
4. ALWAYS record timestamps for all findings

---

## STEP 1: GET YOUR BEARINGS (MANDATORY)

```bash
# 1. Review case context
cat case_brief.md

# 2. Read the investigation plan
cat investigation_plan.json

# 3. Check investigation progress
cat investigation_timeline.md

# 4. Verify evidence integrity
cat evidence/chain_of_custody.json

# 5. Count progress
echo "Completed steps: $(grep -c '"status": "completed"' investigation_plan.json)"
echo "Pending steps: $(grep -c '"status": "pending"' investigation_plan.json)"
```

---

## STEP 2: UNDERSTAND THE PLAN STRUCTURE

The `investigation_plan.json` has this hierarchy:

```
Plan
  └─ Phases (ordered by dependencies)
       └─ Investigation Steps (the units of work you complete)
```

### Key Fields

| Field | Purpose |
|-------|---------|
| `investigation_type` | full, triage, re-analysis |
| `phases[].depends_on` | What phases must complete first |
| `steps[].evidence_source` | Which evidence this step analyzes |
| `steps[].analysis_type` | Type of analysis to perform |
| `steps[].ioc_categories` | What IOCs to look for |
| `steps[].verification` | How to validate findings |
| `steps[].status` | pending, in_progress, completed |

---

## STEP 3: PERFORM ANALYSIS

### 3.1: Evidence Integrity Check

Before analyzing any evidence, verify its integrity:

```bash
# Verify hash
sha256sum evidence/[artifact] | grep -q "[expected_hash]" && echo "VERIFIED" || echo "INTEGRITY FAILURE"
```

### 3.2: Analysis Execution

Based on the analysis type in your step:

#### Log Analysis
```bash
# Parse Windows Event Logs
cat evidence/logs/Security.evtx.json | jq '.[] | select(.EventID == 4624)'

# Look for suspicious process execution
grep -E "powershell|cmd\.exe|wscript" evidence/logs/*.log
```

#### Memory Analysis
```bash
# List running processes
volatility3 -f evidence/memory.dmp windows.pslist

# Check network connections
volatility3 -f evidence/memory.dmp windows.netscan
```

#### Network Analysis
```bash
# Analyze PCAP for suspicious traffic
tshark -r evidence/capture.pcap -Y "http.request or dns"

# Extract IOCs from network traffic
zeek -r evidence/capture.pcap
```

### 3.3: IOC Extraction

For each finding, document as an IOC:

```json
{
  "ioc_type": "ip_address|domain|file_hash|registry_key|process",
  "value": "the indicator value",
  "confidence": 0.0-1.0,
  "context": "where and how it was found",
  "mitre_attack": ["T1059.001", "T1021.002"],
  "timestamp": "when the activity occurred",
  "evidence_source": "which artifact contained this"
}
```

---

## STEP 4: UPDATE FINDINGS

After completing analysis, update the findings file:

```bash
# Append to findings
cat >> findings.json << 'EOF'
{
  "step_id": "step-X-X",
  "timestamp": "ISO-8601",
  "analyst": "Evidence Analyst Agent",
  "findings": [
    {
      "type": "ioc",
      "description": "Suspicious PowerShell execution detected",
      "evidence": "Event ID 4688 in Security.evtx",
      "iocs": [...]
    }
  ],
  "confidence": 0.85,
  "next_steps": ["Analyze related network traffic", "Check for persistence mechanisms"]
}
EOF
```

---

## STEP 5: MARK STEP COMPLETE

Update `investigation_plan.json` to mark the step as completed:

```json
{
  "id": "step-X-X",
  "status": "completed",
  "completed_at": "ISO-8601",
  "findings_count": N,
  "iocs_extracted": N
}
```
```

#### Evidence Validator Agent Prompt (from qa_reviewer.md)

```markdown
## YOUR ROLE - EVIDENCE VALIDATOR AGENT

You are the **Evidence Validation Agent** in an autonomous DFIR process. Your job is to validate 
that the investigation is complete, findings are accurate, and evidence chain of custody is intact.

**Key Principle**: You are the last line of defense. If you approve, the case report ships. Be thorough.

---

## WHY EVIDENCE VALIDATION MATTERS

The Evidence Analyst Agent may have:
- Completed all steps but missed critical artifacts
- Extracted IOCs without proper context
- Made findings without sufficient evidence
- Broken chain of custody
- Missed correlation opportunities
- Left gaps in the timeline

Your job is to catch ALL of these before case closure.

---

## PHASE 1: VERIFY CHAIN OF CUSTODY

```bash
# Check all evidence access logs
cat evidence/chain_of_custody.json

# Verify all evidence hashes
for file in evidence/artifacts/*; do
  sha256sum "$file" >> verification_hashes.txt
done

# Compare with original hashes
diff original_hashes.txt verification_hashes.txt
```

**STOP if chain of custody is broken.** Evidence integrity is paramount.

---

## PHASE 2: VERIFY ALL INVESTIGATION STEPS COMPLETED

```bash
# Count step status
echo "Completed: $(grep -c '"status": "completed"' investigation_plan.json)"
echo "Pending: $(grep -c '"status": "pending"' investigation_plan.json)"
```

---

## PHASE 3: VALIDATE FINDINGS

### 3.1: IOC Validation

For each extracted IOC:
- Verify it exists in the evidence
- Check confidence level is justified
- Validate MITRE ATT&CK mapping
- Cross-reference with threat intelligence

### 3.2: Timeline Validation

- Verify timeline is complete
- Check for gaps
- Validate timestamp consistency
- Ensure logical sequence of events

### 3.3: Evidence Correlation

- Verify findings are corroborated by multiple sources
- Check for contradictory evidence
- Validate attribution claims

---

## PHASE 4: GENERATE VALIDATION REPORT

```markdown
# Evidence Validation Report

**Case ID**: [case-id]
**Date**: [timestamp]
**Validator**: Evidence Validator Agent

## Summary

| Category | Status | Details |
|----------|--------|---------|
| Chain of Custody | ✓/✗ | All evidence verified |
| Investigation Steps | ✓/✗ | X/Y completed |
| IOC Validation | ✓/✗ | X IOCs verified |
| Timeline Completeness | ✓/✗ | No gaps detected |
| Evidence Correlation | ✓/✗ | Findings corroborated |

## Issues Found

### Critical (Blocks Case Closure)
1. [Issue description]

### Major (Should Address)
1. [Issue description]

## Verdict

**VALIDATION**: [APPROVED / REJECTED]
```
```

### 5.3 All Prompt Files to Transform

| File | Transformation Type | Priority |
|------|-------------------|----------|
| `planner.md` | Major rewrite | P0 |
| `coder.md` | Major rewrite | P0 |
| `qa_reviewer.md` | Major rewrite | P0 |
| `qa_fixer.md` | Moderate rewrite | P1 |
| `spec_gatherer.md` | Major rewrite | P0 |
| `spec_writer.md` | Major rewrite | P0 |
| `spec_critic.md` | Moderate rewrite | P1 |
| `spec_researcher.md` | Major rewrite | P0 |
| `spec_quick.md` | Moderate rewrite | P1 |
| `insight_extractor.md` | Moderate rewrite | P2 |
| `followup_planner.md` | Moderate rewrite | P1 |
| `validation_fixer.md` | Minor updates | P2 |
| `complexity_assessor.md` | Moderate rewrite | P1 |
| `coder_recovery.md` | Moderate rewrite | P1 |
| `ideation_code_improvements.md` | Rewrite for DFIR | P2 |
| `ideation_code_quality.md` | Rewrite for DFIR | P2 |
| `ideation_documentation.md` | Rewrite for DFIR | P2 |
| `ideation_performance.md` | Rewrite for DFIR | P2 |
| `ideation_security.md` | Rewrite for DFIR | P1 |
| `ideation_ui_ux.md` | Remove or repurpose | P3 |
| `roadmap_discovery.md` | Rewrite for threat landscape | P2 |
| `roadmap_features.md` | Rewrite for detection rules | P2 |
| `competitor_analysis.md` | Rewrite for threat actors | P2 |

---

## 6. File Structure Changes

### 6.1 Backend Directory Restructure

```
apps/backend/
├── agents/
│   ├── __init__.py
│   ├── base.py
│   ├── case_planner.py          # Renamed
│   ├── evidence_analyst.py      # Renamed
│   ├── evidence_validator.py    # New
│   ├── ioc_extractor.py         # New
│   ├── timeline_reconstructor.py # New
│   ├── chain_of_custody.py      # New
│   ├── mitre_mapper.py          # New
│   ├── memory_manager.py
│   ├── session.py
│   └── utils.py
├── analysis/
│   ├── __init__.py
│   ├── artifact_analyzer.py     # New
│   ├── log_parser.py            # New
│   ├── memory_analyzer.py       # New
│   ├── network_analyzer.py      # New
│   ├── ioc_scanner.py           # Renamed from security_scanner.py
│   ├── threat_intel.py          # New
│   └── timeline_builder.py      # New
├── evidence/
│   ├── __init__.py
│   ├── collector.py             # New
│   ├── chain_of_custody.py      # New
│   ├── integrity.py             # New
│   └── storage.py               # New
├── prompts/
│   ├── case_planner.md          # Renamed
│   ├── evidence_analyst.md      # Renamed
│   ├── evidence_validator.md    # Renamed
│   ├── case_intake.md           # Renamed
│   ├── case_brief_writer.md     # Renamed
│   ├── threat_intel_researcher.md # Renamed
│   ├── quick_triage.md          # Renamed
│   └── ... (all renamed prompts)
├── reporting/
│   ├── __init__.py
│   ├── case_report.py           # New
│   ├── executive_summary.py     # New
│   ├── ioc_report.py            # New
│   └── timeline_report.py       # New
├── cli/
│   ├── __init__.py
│   ├── main.py                  # Update commands
│   ├── case_commands.py         # Renamed from spec_commands.py
│   ├── investigation_commands.py # Renamed from build_commands.py
│   └── ...
└── core/
    ├── __init__.py
    ├── client.py
    ├── phase_event.py           # Update phases
    └── ...
```

### 6.2 Key File Renames

| Current File | New File |
|--------------|----------|
| `spec_runner.py` | `case_runner.py` |
| `spec_contract.json` | `case_contract.json` |
| `implementation_plan.json` | `investigation_plan.json` |
| `build-progress.txt` | `investigation_timeline.md` |
| `project_index.json` | `evidence_inventory.json` |
| `context.json` | `case_context.json` |
| `qa_report.md` | `validation_report.md` |
| `QA_FIX_REQUEST.md` | `VALIDATION_FIX_REQUEST.md` |
| `HUMAN_INPUT.md` | `ANALYST_INPUT.md` |
| `PAUSE` | `ANALYST_REVIEW` |
| `FOLLOWUP_REQUEST.md` | `ADDITIONAL_INVESTIGATION.md` |

### 6.3 New DFIR-Specific Files

```
case_directory/
├── case_brief.md                 # Initial incident description
├── investigation_plan.json       # Structured investigation plan
├── investigation_timeline.md     # Progress and timeline
├── evidence_inventory.json       # Available evidence sources
├── case_context.json             # Investigation context
├── findings.json                 # Extracted findings and IOCs
├── chain_of_custody.json         # Evidence handling log
├── mitre_mapping.json            # MITRE ATT&CK mappings
├── validation_report.md          # Validation results
├── case_report.md                # Final case report
├── executive_summary.md          # Executive summary
├── ioc_export.json               # Exportable IOCs (STIX/OpenIOC)
└── memory/
    ├── case_patterns.json        # Patterns from this case
    ├── threat_intel_cache.json   # Cached threat intel
    └── session_insights/         # Session-specific insights
```

---

## 7. Frontend/UI Changes

### 7.1 i18n Updates

#### `locales/en/common.json` Key Changes

```json
{
  "projectTab": {
    "settings": "Case settings",
    "showArchived": "Show archived cases",
    "hideArchived": "Hide archived cases"
  },
  "labels": {
    "loading": "Loading...",
    "analyzing": "Analyzing...",
    "collecting": "Collecting evidence...",
    "validating": "Validating findings..."
  }
}
```

#### `locales/en/tasks.json` → `locales/en/cases.json`

```json
{
  "status": {
    "pending": "Pending",
    "queued": "Queued",
    "active": "Active Investigation",
    "review": "Evidence Review",
    "reportGenerated": "Report Generated",
    "closed": "Case Closed",
    "archived": "Archived"
  },
  "actions": {
    "start": "Start Investigation",
    "stop": "Pause Investigation",
    "resume": "Resume Investigation",
    "archive": "Archive Case",
    "view": "View Case Details",
    "viewReport": "View Report"
  },
  "labels": {
    "running": "Investigating",
    "evidenceReview": "Evidence Review",
    "needsReview": "Needs Analyst Review",
    "validationFailed": "Validation Failed"
  },
  "columns": {
    "pending": "Pending Cases",
    "active": "Active Investigations",
    "review": "Evidence Review",
    "analyst_review": "Analyst Review",
    "closed": "Closed Cases"
  },
  "execution": {
    "phases": {
      "idle": "Idle",
      "intake": "Case Intake",
      "planning": "Planning",
      "collection": "Evidence Collection",
      "analysis": "Analysis",
      "enrichment": "Enrichment",
      "validation": "Validation",
      "reporting": "Reporting",
      "complete": "Complete",
      "failed": "Failed"
    }
  },
  "wizard": {
    "createTitle": "Create New Case",
    "createDescription": "Describe the security incident. The AI will analyze your input and create an investigation plan.",
    "descriptionPlaceholder": "Describe the incident, affected systems, timeline, and any known indicators. Be as specific as possible about what happened and what evidence is available."
  },
  "form": {
    "classification": {
      "values": {
        "category": {
          "malware": "Malware",
          "intrusion": "Intrusion",
          "data_breach": "Data Breach",
          "insider_threat": "Insider Threat",
          "ransomware": "Ransomware",
          "phishing": "Phishing",
          "apt": "APT"
        },
        "priority": {
          "low": "Low",
          "medium": "Medium",
          "high": "High",
          "critical": "Critical"
        },
        "complexity": {
          "simple": "Simple",
          "moderate": "Moderate",
          "complex": "Complex",
          "advanced": "Advanced"
        }
      }
    }
  }
}
```

### 7.2 Component Renames

| Current Component | New Component |
|-------------------|---------------|
| `KanbanBoard.tsx` | `CaseBoard.tsx` |
| `TaskCard.tsx` | `CaseCard.tsx` |
| `TaskDetails.tsx` | `CaseDetails.tsx` |
| `TaskWizard.tsx` | `CaseWizard.tsx` |
| `Ideation.tsx` | `InvestigationEnhancements.tsx` |
| `Insights.tsx` | `CaseInsights.tsx` |
| `Roadmap.tsx` | `ThreatLandscape.tsx` |
| `Changelog.tsx` | `CaseHistory.tsx` |

### 7.3 New UI Components

```
renderer/components/
├── CaseBoard.tsx                 # Case management board
├── CaseCard.tsx                  # Individual case card
├── CaseDetails.tsx               # Case detail view
├── CaseWizard.tsx                # New case creation
├── EvidenceViewer.tsx            # Evidence file viewer
├── TimelineViewer.tsx            # Investigation timeline
├── IOCTable.tsx                  # IOC display table
├── MitreAttackMatrix.tsx         # MITRE ATT&CK visualization
├── ChainOfCustodyLog.tsx         # Evidence handling log
├── FindingsPanel.tsx             # Findings display
├── ThreatIntelPanel.tsx          # Threat intel integration
├── ValidationStatus.tsx          # Validation status display
└── CaseReportViewer.tsx          # Report viewer
```

### 7.4 Icon Updates

Replace coding-related icons with DFIR-themed icons:
- Code icon → Magnifying glass (investigation)
- Build icon → Shield (security)
- Bug icon → Alert triangle (IOC)
- Feature icon → Folder (case)
- PR icon → Document (report)

---

## 8. Technical Implementation Details

### 8.1 Evidence Handling Module

**New file: `apps/backend/evidence/chain_of_custody.py`**

```python
"""
Chain of Custody Management
===========================
Tracks all evidence handling for legal admissibility.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import hashlib
import json

@dataclass
class CustodyEntry:
    """Single entry in chain of custody log."""
    timestamp: datetime
    action: str  # acquired, accessed, copied, transferred, analyzed
    actor: str   # agent or analyst name
    evidence_id: str
    hash_before: str
    hash_after: str
    notes: str = ""

@dataclass
class ChainOfCustody:
    """Complete chain of custody for a piece of evidence."""
    evidence_id: str
    original_hash: str
    hash_algorithm: str = "SHA256"
    entries: list[CustodyEntry] = field(default_factory=list)
    
    def add_entry(self, action: str, actor: str, notes: str = "") -> None:
        """Add a new custody entry."""
        current_hash = self._calculate_hash()
        entry = CustodyEntry(
            timestamp=datetime.utcnow(),
            action=action,
            actor=actor,
            evidence_id=self.evidence_id,
            hash_before=self.entries[-1].hash_after if self.entries else self.original_hash,
            hash_after=current_hash,
            notes=notes
        )
        self.entries.append(entry)
        
    def verify_integrity(self) -> bool:
        """Verify evidence hasn't been tampered with."""
        current_hash = self._calculate_hash()
        return current_hash == self.entries[-1].hash_after if self.entries else current_hash == self.original_hash
```

### 8.2 IOC Extraction Module

**New file: `apps/backend/analysis/ioc_extractor.py`**

```python
"""
IOC Extraction Module
=====================
Extracts Indicators of Compromise from various evidence sources.
"""

from dataclasses import dataclass
from enum import Enum
import re

class IOCType(str, Enum):
    IP_ADDRESS = "ip_address"
    DOMAIN = "domain"
    URL = "url"
    FILE_HASH_MD5 = "file_hash_md5"
    FILE_HASH_SHA1 = "file_hash_sha1"
    FILE_HASH_SHA256 = "file_hash_sha256"
    EMAIL = "email"
    REGISTRY_KEY = "registry_key"
    FILE_PATH = "file_path"
    PROCESS_NAME = "process_name"
    MUTEX = "mutex"
    USER_AGENT = "user_agent"

@dataclass
class IOC:
    """Indicator of Compromise."""
    type: IOCType
    value: str
    confidence: float  # 0.0 - 1.0
    source: str        # Evidence source
    context: str       # How/where found
    mitre_tactics: list[str] = None
    mitre_techniques: list[str] = None
    first_seen: str = None
    last_seen: str = None
    
class IOCExtractor:
    """Extract IOCs from various evidence types."""
    
    # Regex patterns for IOC extraction
    PATTERNS = {
        IOCType.IP_ADDRESS: r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
        IOCType.DOMAIN: r'\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b',
        IOCType.FILE_HASH_MD5: r'\b[a-fA-F0-9]{32}\b',
        IOCType.FILE_HASH_SHA1: r'\b[a-fA-F0-9]{40}\b',
        IOCType.FILE_HASH_SHA256: r'\b[a-fA-F0-9]{64}\b',
        IOCType.EMAIL: r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    }
    
    def extract_from_text(self, text: str, source: str) -> list[IOC]:
        """Extract IOCs from text content."""
        iocs = []
        for ioc_type, pattern in self.PATTERNS.items():
            matches = re.findall(pattern, text)
            for match in matches:
                iocs.append(IOC(
                    type=ioc_type,
                    value=match,
                    confidence=0.5,  # Base confidence, to be enriched
                    source=source,
                    context=f"Extracted via pattern matching from {source}"
                ))
        return iocs
```

### 8.3 MITRE ATT&CK Mapping

**New file: `apps/backend/analysis/mitre_mapper.py`**

```python
"""
MITRE ATT&CK Mapping Module
===========================
Maps findings to MITRE ATT&CK framework.
"""

from dataclasses import dataclass

@dataclass
class MITREMapping:
    """MITRE ATT&CK mapping for a finding."""
    tactic_id: str      # e.g., "TA0001"
    tactic_name: str    # e.g., "Initial Access"
    technique_id: str   # e.g., "T1566"
    technique_name: str # e.g., "Phishing"
    sub_technique_id: str = None  # e.g., "T1566.001"
    sub_technique_name: str = None  # e.g., "Spearphishing Attachment"
    confidence: float = 0.0
    evidence: list[str] = None

class MITREMapper:
    """Map findings to MITRE ATT&CK framework."""
    
    # Keyword to technique mapping (simplified)
    KEYWORD_MAPPINGS = {
        "powershell": ("T1059.001", "PowerShell"),
        "cmd.exe": ("T1059.003", "Windows Command Shell"),
        "wmic": ("T1047", "Windows Management Instrumentation"),
        "psexec": ("T1021.002", "SMB/Windows Admin Shares"),
        "mimikatz": ("T1003.001", "LSASS Memory"),
        "scheduled task": ("T1053.005", "Scheduled Task"),
        "registry run key": ("T1547.001", "Registry Run Keys"),
        # ... more mappings
    }
    
    def map_finding(self, finding: str) -> list[MITREMapping]:
        """Map a finding to MITRE ATT&CK techniques."""
        mappings = []
        finding_lower = finding.lower()
        
        for keyword, (technique_id, technique_name) in self.KEYWORD_MAPPINGS.items():
            if keyword in finding_lower:
                mappings.append(MITREMapping(
                    tactic_id="",  # To be enriched
                    tactic_name="",
                    technique_id=technique_id,
                    technique_name=technique_name,
                    confidence=0.7,
                    evidence=[finding]
                ))
        
        return mappings
```

### 8.4 Investigation Plan Schema

**New file: `apps/backend/investigation_plan.py`**

```python
"""
Investigation Plan Module
=========================
Defines the structure for DFIR investigation plans.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import json
from pathlib import Path

class InvestigationType(str, Enum):
    FULL = "full"
    TRIAGE = "triage"
    REANALYSIS = "reanalysis"

class IncidentType(str, Enum):
    MALWARE = "malware"
    INTRUSION = "intrusion"
    DATA_BREACH = "data_breach"
    INSIDER_THREAT = "insider_threat"
    RANSOMWARE = "ransomware"
    PHISHING = "phishing"
    APT = "apt"
    UNKNOWN = "unknown"

class StepStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"

@dataclass
class ChainOfCustodyInfo:
    """Chain of custody information for an investigation step."""
    collector: str
    timestamp: str
    hash_algorithm: str = "SHA256"
    original_hash: Optional[str] = None

@dataclass
class StepVerification:
    """Verification criteria for an investigation step."""
    type: str  # hash_verification, ioc_validation, manual_review
    expected_hash: Optional[str] = None
    min_confidence: Optional[float] = None
    criteria: Optional[str] = None

@dataclass
class InvestigationStep:
    """Single step in an investigation phase."""
    id: str
    description: str
    evidence_source: str
    status: StepStatus = StepStatus.PENDING
    analysis_type: Optional[str] = None
    artifacts: list[str] = field(default_factory=list)
    ioc_categories: list[str] = field(default_factory=list)
    chain_of_custody: Optional[ChainOfCustodyInfo] = None
    verification: Optional[StepVerification] = None
    findings_count: int = 0
    iocs_extracted: int = 0
    completed_at: Optional[str] = None

@dataclass
class InvestigationPhase:
    """Phase in an investigation plan."""
    id: str
    name: str
    type: str  # collection, analysis, enrichment, validation, reporting
    description: str
    depends_on: list[str] = field(default_factory=list)
    steps: list[InvestigationStep] = field(default_factory=list)

@dataclass
class EvidenceSource:
    """Evidence source definition."""
    type: str
    hostname: Optional[str] = None
    source: Optional[str] = None
    artifacts: list[str] = field(default_factory=list)
    timeframe: Optional[str] = None

@dataclass
class InvestigationPlan:
    """Complete investigation plan."""
    case_id: str
    incident_type: IncidentType
    investigation_type: InvestigationType
    investigation_rationale: str
    phases: list[InvestigationPhase] = field(default_factory=list)
    evidence_sources: dict[str, EvidenceSource] = field(default_factory=dict)
    status: str = "in_progress"
    
    @classmethod
    def load(cls, path: Path) -> "InvestigationPlan":
        """Load investigation plan from JSON file."""
        with open(path) as f:
            data = json.load(f)
        # Parse and return InvestigationPlan
        return cls(**data)
    
    def save(self, path: Path) -> None:
        """Save investigation plan to JSON file."""
        with open(path, 'w') as f:
            json.dump(self.__dict__, f, indent=2, default=str)
```

---

## 9. New DFIR-Specific Features

### 9.1 Threat Intelligence Integration

- Query VirusTotal, AbuseIPDB, Shodan
- Integrate with MISP
- Support for STIX/TAXII feeds
- Cache threat intel results

### 9.2 Evidence Format Support

- Windows Event Logs (EVTX)
- Linux logs (syslog, auth.log)
- Memory dumps (Volatility support)
- Network captures (PCAP)
- Disk images (E01, raw)
- Browser artifacts
- Registry hives

### 9.3 Report Generation

- Executive Summary (non-technical)
- Technical Report (detailed findings)
- IOC Export (STIX, OpenIOC, CSV)
- Timeline Report (chronological events)
- MITRE ATT&CK Report (technique mapping)

### 9.4 Case Management

- Case numbering and tracking
- Evidence inventory management
- Chain of custody logging
- Analyst assignment
- Case status workflow

### 9.5 Integration Points

- SIEM integration (Splunk, Elastic)
- Ticketing systems (Jira, ServiceNow)
- Threat intel platforms (MISP, OpenCTI)
- EDR platforms (CrowdStrike, Carbon Black)

---

## 10. Implementation Roadmap

### Phase 1: Core Transformation (Weeks 1-2)

**Priority: P0 - Critical Path**

1. **Rename and rebrand project**
   - Update package.json files
   - Rename repository
   - Update README.md
   - Update icons and branding

2. **Transform core prompts**
   - `planner.md` → `case_planner.md`
   - `coder.md` → `evidence_analyst.md`
   - `qa_reviewer.md` → `evidence_validator.md`
   - `spec_*.md` → `case_*.md`

3. **Update agent files**
   - Rename agent Python files
   - Update imports and references
   - Modify agent logic for DFIR context

4. **Update phase configuration**
   - New execution phases
   - Phase-specific models
   - Thinking level adjustments

### Phase 2: Evidence Handling (Weeks 3-4)

**Priority: P1 - Essential**

1. **Implement chain of custody module**
   - Evidence tracking
   - Hash verification
   - Custody logging

2. **Create IOC extraction module**
   - Pattern-based extraction
   - Confidence scoring
   - Deduplication

3. **Implement timeline builder**
   - Event correlation
   - Timestamp normalization
   - Gap detection

4. **Add MITRE ATT&CK mapping**
   - Technique identification
   - Tactic mapping
   - Confidence scoring

### Phase 3: Frontend Updates (Weeks 5-6)

**Priority: P1 - Essential**

1. **Update i18n files**
   - Translate all terminology
   - Add new DFIR-specific strings

2. **Rename components**
   - Update component names
   - Modify component logic

3. **Create new UI components**
   - Evidence viewer
   - Timeline viewer
   - IOC table
   - MITRE matrix visualization

4. **Update styling and icons**
   - DFIR-themed icons
   - Color scheme updates

### Phase 4: Advanced Features (Weeks 7-8)

**Priority: P2 - Important**

1. **Threat intelligence integration**
   - API integrations
   - Caching layer
   - Enrichment pipeline

2. **Report generation**
   - Template system
   - Multiple output formats
   - Executive summary generator

3. **Evidence format support**
   - Log parsers
   - Memory analysis integration
   - Network capture analysis

### Phase 5: Polish and Testing (Weeks 9-10)

**Priority: P2 - Important**

1. **Comprehensive testing**
   - Unit tests for new modules
   - Integration tests
   - End-to-end testing

2. **Documentation**
   - User guide
   - API documentation
   - Contribution guidelines

3. **Performance optimization**
   - Large evidence handling
   - Caching improvements
   - Memory management

---

## Appendix A: Complete File Mapping

| Current Path | New Path |
|--------------|----------|
| `apps/backend/prompts/planner.md` | `apps/backend/prompts/case_planner.md` |
| `apps/backend/prompts/coder.md` | `apps/backend/prompts/evidence_analyst.md` |
| `apps/backend/prompts/coder_recovery.md` | `apps/backend/prompts/analyst_recovery.md` |
| `apps/backend/prompts/qa_reviewer.md` | `apps/backend/prompts/evidence_validator.md` |
| `apps/backend/prompts/qa_fixer.md` | `apps/backend/prompts/finding_remediation.md` |
| `apps/backend/prompts/spec_gatherer.md` | `apps/backend/prompts/case_intake.md` |
| `apps/backend/prompts/spec_writer.md` | `apps/backend/prompts/case_brief_writer.md` |
| `apps/backend/prompts/spec_critic.md` | `apps/backend/prompts/case_brief_reviewer.md` |
| `apps/backend/prompts/spec_researcher.md` | `apps/backend/prompts/threat_intel_researcher.md` |
| `apps/backend/prompts/spec_quick.md` | `apps/backend/prompts/quick_triage.md` |
| `apps/backend/prompts/insight_extractor.md` | `apps/backend/prompts/pattern_extractor.md` |
| `apps/backend/prompts/followup_planner.md` | `apps/backend/prompts/followup_investigation.md` |
| `apps/backend/prompts/complexity_assessor.md` | `apps/backend/prompts/case_complexity_assessor.md` |
| `apps/backend/prompts/ideation_*.md` | `apps/backend/prompts/investigation_enhancement_*.md` |
| `apps/backend/prompts/roadmap_*.md` | `apps/backend/prompts/threat_landscape_*.md` |
| `apps/backend/prompts/competitor_analysis.md` | `apps/backend/prompts/threat_actor_analysis.md` |
| `apps/backend/agents/planner.py` | `apps/backend/agents/case_planner.py` |
| `apps/backend/agents/coder.py` | `apps/backend/agents/evidence_analyst.py` |
| `apps/backend/security_scanner.py` | `apps/backend/analysis/ioc_scanner.py` |
| `apps/frontend/src/shared/i18n/locales/en/tasks.json` | `apps/frontend/src/shared/i18n/locales/en/cases.json` |

---

## Appendix B: Terminology Quick Reference

| Coding Term | DFIR Term |
|-------------|-----------|
| Task | Case |
| Spec | Case Brief |
| Subtask | Investigation Step |
| Implementation Plan | Investigation Plan |
| Build | Investigation |
| Code | Evidence/Artifacts |
| Commit | Evidence Snapshot |
| Branch | Investigation Branch |
| Worktree | Evidence Workspace |
| Pull Request | Case Report |
| Merge | Case Closure |
| QA | Evidence Validation |
| Bug | IOC |
| Feature | Investigation Capability |
| Refactor | Re-analysis |
| Test | Verification |
| Deploy | Report |

---

## Appendix C: MITRE ATT&CK Integration Reference

### Tactics (High-Level Goals)
- TA0001: Initial Access
- TA0002: Execution
- TA0003: Persistence
- TA0004: Privilege Escalation
- TA0005: Defense Evasion
- TA0006: Credential Access
- TA0007: Discovery
- TA0008: Lateral Movement
- TA0009: Collection
- TA0010: Exfiltration
- TA0011: Command and Control
- TA0040: Impact

### Common Techniques for Automated Detection
- T1059: Command and Scripting Interpreter
- T1021: Remote Services
- T1053: Scheduled Task/Job
- T1547: Boot or Logon Autostart Execution
- T1003: OS Credential Dumping
- T1071: Application Layer Protocol
- T1105: Ingress Tool Transfer

---

*Document Version: 1.0*
*Last Updated: January 2026*
*Author: Auto-DFIR Transformation Team*
