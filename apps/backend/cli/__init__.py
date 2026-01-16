"""
Auto Sleuth CLI Package
=======================

Command-line interface for the Auto Sleuth autonomous coding framework.

This package provides a modular CLI structure:
- main.py: Argument parsing and command routing
- case_commands.py: Case listing and management
- build_commands.py: Build execution and follow-up tasks
- workspace_commands.py: Workspace management (merge, review, discard)
- qa_commands.py: QA validation commands
- utils.py: Shared utilities and configuration
"""

from .main import main

__all__ = ["main"]
