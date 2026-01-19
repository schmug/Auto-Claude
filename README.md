# Auto Sleuth

**Autonomous multi-agent DFIR framework that plans, investigates, and validates cybersecurity incidents for you.**

![Auto Sleuth Case Board](.github/assets/Auto-Claude-Kanban.png)

[![License](https://img.shields.io/badge/license-AGPL--3.0-green?style=flat-square)](./agpl-3.0.txt)
[![Discord](https://img.shields.io/badge/Discord-Join%20Community-5865F2?style=flat-square&logo=discord&logoColor=white)](https://discord.gg/KCXaPBr4Dj)

---

## Overview

Auto Sleuth is an AI-powered Digital Forensics and Incident Response platform that leverages autonomous agents to automate the entire investigation lifecycle. From initial case intake to final reporting, Auto Sleuth handles evidence collection, analysis, IOC extraction, timeline reconstruction, and evidence validation—all while maintaining chain of custody.

Built on the foundation of [Auto-Claude](https://github.com/AndyMik90/Auto-Claude), Auto Sleuth transforms the multi-agent coding framework into a powerful cybersecurity investigation tool.

---

## Download

### Requirements

- **Claude Pro/Max subscription** - [Get one here](https://claude.ai/upgrade)
- **Claude Code CLI** - `npm install -g @anthropic-ai/claude-code`
- **Git repository** - For case and evidence management

---

## Quick Start

1. **Download and install** the app for your platform
2. **Open your evidence workspace** - Select a git repository folder
3. **Connect Claude** - The app will guide you through OAuth setup
4. **Create a case** - Describe the security incident to investigate
5. **Watch it work** - Agents plan, analyze, and validate autonomously

---

## Features

| Feature | Description |
|---------|-------------|
| **Autonomous Investigations** | Describe the incident; agents handle planning, analysis, and validation |
| **Parallel Execution** | Run multiple investigations simultaneously with up to 12 agent terminals |
| **Isolated Evidence Workspaces** | All analysis happens in git worktrees - original evidence stays protected |
| **Self-Validating QA** | Built-in evidence validation loop catches issues before final report |
| **Chain of Custody** | Complete audit trail for all evidence handling |
| **IOC Extraction** | Automatic extraction of IPs, domains, hashes, and other indicators |
| **MITRE ATT&CK Mapping** | Automatic mapping of findings to ATT&CK techniques |
| **Timeline Reconstruction** | Chronological event correlation across multiple sources |
| **Cross-Platform** | Native desktop apps for Windows, macOS, and Linux |

---

## Investigation Agents

| Agent | Role |
|-------|------|
| **Case Planner Agent** | Creates structured investigation plans based on incident details |
| **Evidence Analyst Agent** | Analyzes digital artifacts, extracts IOCs, and correlates evidence |
| **Evidence Validator Agent** | Validates findings and ensures chain of custody integrity |
| **Threat Intelligence Agent** | Enriches investigations with threat intel and MITRE ATT&CK mappings |
| **Timeline Reconstructor Agent** | Builds chronological timeline from multiple evidence sources |
| **Report Generator Agent** | Creates formal incident reports and executive summaries |

---

## Investigation Workflow

### Phase 1: Case Intake & Scoping
- Gather incident details
- Identify evidence sources
- Define investigation scope
- Create case brief

### Phase 2: Evidence Collection
- Identify artifacts to collect
- Document chain of custody
- Acquire evidence (disk, memory, network, logs)
- Verify evidence integrity (hashes)

### Phase 3: Evidence Analysis
- Parse and examine artifacts
- Extract IOCs
- Correlate events
- Build timeline

### Phase 4: Threat Intelligence Enrichment
- Query threat intel feeds
- Identify threat actors/TTPs
- Map to MITRE ATT&CK
- Assess impact

### Phase 5: Evidence Validation
- Verify findings
- Check chain of custody
- Cross-reference evidence
- Document gaps

### Phase 6: Reporting
- Generate incident report
- Create executive summary
- Document recommendations
- Archive case

---

## Interface

### Case Board
Visual case management from intake through closure. Create cases and monitor agent progress in real-time.

### Agent Terminals
AI-powered terminals with one-click case context injection. Spawn multiple agents for parallel analysis.

![Agent Terminals](.github/assets/Auto-Claude-Agents-terminals.png)

### Threat Landscape
AI-assisted threat analysis with IOC enrichment and MITRE ATT&CK visualization.

![Investigation Roadmap](.github/assets/Auto-Claude-roadmap.png)

---

## Evidence Types Supported

| Category | Artifacts |
|----------|-----------|
| **File System** | Files, folders, deleted data, metadata |
| **Memory** | Running processes, network connections, encryption keys |
| **Network** | Traffic logs, DNS queries, connection records |
| **Application** | Logs, configuration files, user data |
| **Registry** | System configuration, user activity, installed software |
| **Browser** | History, cookies, cache, downloads |
| **Email** | Headers, attachments, metadata |

---

## IOC Types Extracted

| Type | Description |
|------|-------------|
| IP Address | IPv4 and IPv6 addresses |
| Domain | Domain names and subdomains |
| URL | Full URLs including paths |
| File Hash | MD5, SHA1, SHA256 hashes |
| Email | Email addresses |
| Registry Key | Windows registry paths |
| File Path | File system paths |
| Process Name | Executable names |
| User Agent | HTTP user agent strings |

---

## Project Structure

```
Auto Sleuth/
├── apps/
│   ├── backend/
│   │   ├── agents/           # AI agent implementations
│   │   ├── analysis/         # Forensic analysis modules
│   │   ├── evidence/         # Evidence handling modules
│   │   ├── prompts/          # Agent prompt templates
│   │   └── reporting/        # Report generation
│   └── frontend/
│       └── src/
│           ├── renderer/     # React UI components
│           └── shared/       # Shared utilities
├── libs/                     # Shared libraries
└── docs/                     # Documentation
```

---

## CLI Usage

For headless operation, CI/CD integration, or terminal-only workflows:

```bash
cd apps/backend

# Create a case interactively
python runners/case_runner.py --interactive

# Run autonomous investigation
python run.py --case 001

# Review and merge
python run.py --case 001 --review
python run.py --case 001 --merge
```

---

## Development

Want to build from source or contribute? See [CONTRIBUTING.md](CONTRIBUTING.md) for complete development setup instructions.

### Available Scripts

| Command | Description |
|---------|-------------|
| `npm run install:all` | Install backend and frontend dependencies |
| `npm start` | Build and run the desktop app |
| `npm run dev` | Run in development mode with hot reload |
| `npm run package` | Package for current platform |
| `npm test` | Run frontend tests |
| `npm run test:backend` | Run backend tests |

---

## Security

Auto Sleuth uses a three-layer security model:

1. **OS Sandbox** - Analysis commands run in isolation
2. **Filesystem Restrictions** - Operations limited to evidence workspace
3. **Chain of Custody** - Complete audit trail for evidence handling

---

## Contributing

We welcome contributions! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Development setup instructions
- Code style guidelines
- Testing requirements
- Pull request process

---

## Community

- **Discord** - [Join our community](https://discord.gg/KCXaPBr4Dj)
- **Issues** - [Report bugs or request features](https://github.com/schmug/Auto-DFIR/issues)
- **Discussions** - [Ask questions](https://github.com/schmug/Auto-DFIR/discussions)

---

## License

**AGPL-3.0** - GNU Affero General Public License v3.0

Auto Sleuth is free to use. If you modify and distribute it, or run it as a service, your code must also be open source under AGPL-3.0.

---

## Acknowledgments

- Built on the foundation of [Auto-Claude](https://github.com/AndyMik90/Auto-Claude)
- DFIR methodology based on [NIST SP 800-86](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-86.pdf)
- MITRE ATT&CK framework integration
