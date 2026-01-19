# Auto Sleuth CLI Usage

This document covers terminal-only usage of Auto Sleuth. **For most users, we recommend using the [Desktop UI](#) instead** - it provides a better experience with visual task management, progress tracking, and automatic Python environment setup.

## When to Use CLI

- You prefer terminal workflows
- You're running on a headless server
- You're integrating Auto Sleuth into scripts or CI/CD

## Prerequisites

- Python 3.9+
- Claude Code CLI (`npm install -g @anthropic-ai/claude-code`)

### Installing Python

**Windows:**
```bash
winget install Python.Python.3.12
```

**macOS:**
```bash
brew install python@3.12
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt install python3.12 python3.12-venv
```

**Linux (Fedora):**
```bash
sudo dnf install python3.12
```

## Setup

**Step 1:** Navigate to the backend directory

```bash
cd apps/backend
```

**Step 2:** Set up Python environment

```bash
# Using uv (recommended)
uv venv && uv pip install -r requirements.txt

# Or using standard Python
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
```

**Step 3:** Configure environment

```bash
cp .env.example .env

# Get your OAuth token
claude setup-token

# Add the token to apps/backend/.env
# CLAUDE_CODE_OAUTH_TOKEN=your-token-here
```

## Creating Cases

All commands below should be run from the `apps/backend/` directory:

```bash
# Activate the virtual environment (if not already active)
source .venv/bin/activate

# Create a case interactively
python runners/case_runner.py --interactive

# Or with a task description
python runners/case_runner.py --task "Investigate suspicious OAuth token usage"

# Force a specific complexity level
python runners/case_runner.py --task "Fix button color" --complexity simple

# Continue an interrupted case
python runners/case_runner.py --continue 001-case
```

### Complexity Tiers

The case runner automatically assesses investigation complexity:

| Tier | Phases | When Used |
|------|--------|-----------|
| **SIMPLE** | 3 | 1-2 files, single service, no integrations (UI fixes, text changes) |
| **STANDARD** | 6 | 3-10 files, 1-2 services, minimal integrations (features, bug fixes) |
| **COMPLEX** | 8 | 10+ files, multiple services, external integrations |

## Running Investigations

```bash
# List all cases and their status
python run.py --list

# Run a specific case
python run.py --case 001
python run.py --case 001-incident-name

# Limit iterations for testing
python run.py --case 001 --max-iterations 5
```

## QA Validation

After all chunks are complete, QA validation runs automatically:

```bash
# Skip automatic QA
python run.py --case 001 --skip-qa

# Run QA validation manually
python run.py --case 001 --qa

# Check QA status
python run.py --case 001 --qa-status
```

The QA validation loop:
1. **QA Reviewer** checks all acceptance criteria
2. If issues found → creates `QA_FIX_REQUEST.md`
3. **QA Fixer** applies fixes
4. Loop repeats until approved (up to 50 iterations)

## Workspace Management

Auto Sleuth uses Git worktrees for isolated investigations:

```bash
# Test the feature in the isolated workspace
cd .auto-sleuth/worktrees/tasks/001-case/
npm run dev  # or your project's run command

# Return to backend directory to run management commands
cd apps/backend

# See what was changed
python run.py --case 001 --review

# Merge changes into your project
python run.py --case 001 --merge

# Discard if you don't like it
python run.py --case 001 --discard
```

## Interactive Controls

While the agent is running:

```bash
# Pause and add instructions
Ctrl+C (once)

# Exit immediately
Ctrl+C (twice)
```

**File-based alternative:**
```bash
# Create PAUSE file to pause after current session
touch .auto-sleuth/cases/001-case/PAUSE

# Add instructions
echo "Focus on analyzing the login anomalies first" > .auto-sleuth/cases/001-case/HUMAN_INPUT.md
```

## Case Validation

```bash
python validate_spec.py --spec-dir .auto-sleuth/cases/001-case --checkpoint all
```

## Environment Variables

Copy `.env.example` to `.env` and configure as needed:

```bash
cp .env.example .env
```

### Core Settings

| Variable | Required | Description |
|----------|----------|-------------|
| `CLAUDE_CODE_OAUTH_TOKEN` | Yes | OAuth token from `claude setup-token` |
| `AUTO_BUILD_MODEL` | No | Model override (default: claude-opus-4-5-20251101) |
| `DEFAULT_BRANCH` | No | Base branch for worktrees (auto-detects main/master) |
| `DEBUG` | No | Enable debug logging (default: false) |

### Integrations

| Variable | Required | Description |
|----------|----------|-------------|
| `LINEAR_API_KEY` | No | Linear API key for task sync |
| `GITLAB_TOKEN` | No | GitLab Personal Access Token |
| `GITLAB_INSTANCE_URL` | No | GitLab instance URL (defaults to gitlab.com) |

### Memory Layer (Graphiti)

| Variable | Required | Description |
|----------|----------|-------------|
| `GRAPHITI_ENABLED` | No | Enable Memory Layer (default: true) |
| `GRAPHITI_LLM_PROVIDER` | No | LLM provider: openai, anthropic, ollama, google, openrouter |
| `GRAPHITI_EMBEDDER_PROVIDER` | No | Embedder: openai, voyage, ollama, google, openrouter |

See `.env.example` for complete configuration options including provider-specific settings.
