#!/usr/bin/env python3
"""
Auto Sleuth Framework
=====================

A multi-session autonomous DFIR framework for conducting investigations and incident response.
Uses subtask-based investigation plans with phase dependencies.

Key Features:
- Safe evidence isolation (analyzes in separate workspace by default)
- Parallel assessment with Git worktrees
- Smart recovery from interruptions
- Linear integration for case management

Usage:
    python auto-sleuth/run.py --case 001-incident-name
    python auto-sleuth/run.py --case 001
    python auto-sleuth/run.py --list

    # Case management
    python auto-sleuth/run.py --case 001 --merge     # Add completed findings to project
    python auto-sleuth/run.py --case 001 --review    # See what was analyzed
    python auto-sleuth/run.py --case 001 --discard   # Delete case (requires confirmation)

Prerequisites:
    - CLAUDE_CODE_OAUTH_TOKEN environment variable set (run: claude setup-token)
    - Case created via: claude /case
    - Claude Code CLI installed
"""

import sys

# Python version check - must be before any imports using 3.10+ syntax
if sys.version_info < (3, 10):  # noqa: UP036
    sys.exit(
        f"Error: Auto Sleuth requires Python 3.10 or higher.\n"
        f"You are running Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}\n"
        f"\n"
        f"Please upgrade Python: https://www.python.org/downloads/"
    )

import io

# Configure safe encoding on Windows BEFORE any imports that might print
# This handles both TTY and piped output (e.g., from Electron)
if sys.platform == "win32":
    for _stream_name in ("stdout", "stderr"):
        _stream = getattr(sys, _stream_name)
        # Method 1: Try reconfigure (works for TTY)
        if hasattr(_stream, "reconfigure"):
            try:
                _stream.reconfigure(encoding="utf-8", errors="replace")
                continue
            except (AttributeError, io.UnsupportedOperation, OSError):
                pass
        # Method 2: Wrap with TextIOWrapper for piped output
        try:
            if hasattr(_stream, "buffer"):
                _new_stream = io.TextIOWrapper(
                    _stream.buffer,
                    encoding="utf-8",
                    errors="replace",
                    line_buffering=True,
                )
                setattr(sys, _stream_name, _new_stream)
        except (AttributeError, io.UnsupportedOperation, OSError):
            pass
    # Clean up temporary variables
    del _stream_name, _stream
    if "_new_stream" in dir():
        del _new_stream

from cli import main

if __name__ == "__main__":
    main()
