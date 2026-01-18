"""
Requirements Gathering Module
==============================

Interactive and automated requirements collection from users.
"""

import json
import os
import shlex
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path


def open_editor_for_input(field_name: str) -> str:
    """Open the user's editor for long-form text input."""
    editor = os.environ.get("EDITOR", os.environ.get("VISUAL", "nano"))

    # Create temp file with helpful instructions
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(f"# Enter your {field_name.replace('_', ' ')} below\n")
        f.write("# Lines starting with # will be ignored\n")
        f.write("# Save and close the editor when done\n\n")
        temp_path = f.name

    try:
        # Parse editor command (handles "code --wait" etc.)
        editor_cmd = shlex.split(editor)
        editor_cmd.append(temp_path)

        # Open editor
        result = subprocess.run(editor_cmd)

        if result.returncode != 0:
            return ""

        # Read the content
        with open(temp_path) as f:
            lines = f.readlines()

        # Filter out comment lines and join
        content_lines = [
            line.rstrip() for line in lines if not line.strip().startswith("#")
        ]
        return "\n".join(content_lines).strip()

    finally:
        # Clean up temp file
        try:
            os.unlink(temp_path)
        except OSError:
            pass


def gather_requirements_interactively(ui_module) -> dict:
    """Gather requirements interactively from the user via CLI prompts.

    Args:
        ui_module: UI module with formatting functions (bold, muted, etc.)
    """
    print()
    print(f"  {ui_module.muted('Answer the following questions to define your task:')}")
    print()

    # Task description - multi-line support with editor option
    print(f"  {ui_module.bold('1. What incident or activity should we investigate?')}")
    print(f"     {ui_module.muted('(Describe the suspicious activity, alert, or case)')}")
    edit_hint = 'Type "edit" to open in your editor, or enter text below'
    print(f"     {ui_module.muted(edit_hint)}")
    print(
        f"     {ui_module.muted('(Press Enter often for new lines, blank line = done)')}"
    )

    task = ""
    task_lines = []
    while True:
        try:
            line = input("     > " if not task_lines else "       ")

            # Check for editor command on first line
            if not task_lines and line.strip().lower() == "edit":
                task = open_editor_for_input("task_description")
                if task:
                    print(
                        f"     {ui_module.muted(f'Got {len(task)} chars from editor')}"
                    )
                break

            if not line and task_lines:  # Blank line and we have content = done
                break
            if line:
                task_lines.append(line)
        except EOFError:
            break

    # If we collected lines (not from editor)
    if task_lines:
        task = " ".join(task_lines).strip()

    if not task:
        task = "No task description provided"
    print()

    # Investigation type
    print(f"  {ui_module.bold('2. What type of investigation is this?')}")
    print(f"     {ui_module.muted('[1] triage            - Initial assessment of alerts/incidents')}")
    print(f"     {ui_module.muted('[2] intrusion         - Unauthorized access or lateral movement')}")
    print(f"     {ui_module.muted('[3] malware           - Malicious code analysis and containment')}")
    print(f"     {ui_module.muted('[4] insider_threat    - Malicious or negligent insider activity')}")
    print(f"     {ui_module.muted('[5] data_breach       - Data exposure or exfiltration')}")
    print(f"     {ui_module.muted('[6] incident_response - Response coordination and containment')}")
    print(f"     {ui_module.muted('[7] incident_analysis - Deep-dive root cause analysis')}")
    print(f"     {ui_module.muted('[8] ransomware        - Ransomware detection and recovery')}")
    print(f"     {ui_module.muted('[9] phishing          - Phishing campaign investigation')}")
    print(f"     {ui_module.muted('[10] threat_hunting   - Proactive hunting activities')}")
    investigation_choice = input("     > ").strip()
    investigation_map = {
        "1": "triage",
        "triage": "triage",
        "2": "intrusion",
        "intrusion": "intrusion",
        "3": "malware",
        "malware": "malware",
        "4": "insider_threat",
        "insider": "insider_threat",
        "insider_threat": "insider_threat",
        "5": "data_breach",
        "breach": "data_breach",
        "data_breach": "data_breach",
        "6": "incident_response",
        "response": "incident_response",
        "incident_response": "incident_response",
        "7": "incident_analysis",
        "analysis": "incident_analysis",
        "incident_analysis": "incident_analysis",
        "8": "ransomware",
        "ransomware": "ransomware",
        "9": "phishing",
        "phish": "phishing",
        "phishing": "phishing",
        "10": "threat_hunting",
        "hunting": "threat_hunting",
        "threat_hunting": "threat_hunting",
    }
    investigation_type = investigation_map.get(investigation_choice.lower(), "triage")
    print()

    # Evidence sources (optional)
    print(f"  {ui_module.bold('3. What evidence sources should we prioritize?')}")
    print(
        f"     {ui_module.muted('(Comma-separated, e.g., endpoint telemetry, email logs, proxy logs)')}"
    )
    evidence_input = input("     > ").strip()
    evidence_sources = [
        source.strip()
        for source in evidence_input.split(",")
        if source.strip()
    ]
    print()

    # Additional context (optional) - multi-line support
    print(f"  {ui_module.bold('4. Any additional context or constraints?')}")
    print(
        f"     {ui_module.muted('(Press Enter to skip, or enter a blank line when done)')}"
    )

    context_lines = []
    while True:
        try:
            line = input("     > " if not context_lines else "       ")
            if not line:  # Blank line = done (allows skip on first empty)
                break
            context_lines.append(line)
        except EOFError:
            break

    additional_context = " ".join(context_lines).strip()
    print()

    return {
        "task_description": task,
        "investigation_type": investigation_type,
        "evidence_sources": evidence_sources,
        "additional_context": additional_context if additional_context else None,
        "created_at": datetime.now().isoformat(),
    }


def create_requirements_from_task(task_description: str) -> dict:
    """Create minimal requirements dictionary from task description."""
    return {
        "task_description": task_description,
        "investigation_type": "triage",  # Default, agent will refine
        "evidence_sources": [],
        "created_at": datetime.now().isoformat(),
    }


def save_requirements(case_dir: Path, requirements: dict) -> Path:
    """Save requirements to file."""
    requirements_file = case_dir / "requirements.json"
    with open(requirements_file, "w") as f:
        json.dump(requirements, f, indent=2)
    return requirements_file


def load_requirements(case_dir: Path) -> dict | None:
    """Load requirements from file if it exists."""
    requirements_file = case_dir / "requirements.json"
    if not requirements_file.exists():
        return None

    with open(requirements_file) as f:
        return json.load(f)
