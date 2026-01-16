"""
Tool Registry
=============

Central registry for creating and managing auto-sleuth MCP tools.
"""

from pathlib import Path

try:
    from claude_agent_sdk import create_sdk_mcp_server

    SDK_TOOLS_AVAILABLE = True
except ImportError:
    SDK_TOOLS_AVAILABLE = False
    create_sdk_mcp_server = None

from .tools import (
    create_memory_tools,
    create_progress_tools,
    create_qa_tools,
    create_subtask_tools,
)


def create_all_tools(case_dir: Path, project_dir: Path) -> list:
    """
    Create all custom tools with the given case and project directories.

    Args:
        case_dir: Path to the case directory
        project_dir: Path to the project root

    Returns:
        List of all tool functions
    """
    if not SDK_TOOLS_AVAILABLE:
        return []

    all_tools = []

    # Create tools by category
    all_tools.extend(create_subtask_tools(case_dir, project_dir))
    all_tools.extend(create_progress_tools(case_dir, project_dir))
    all_tools.extend(create_memory_tools(case_dir, project_dir))
    all_tools.extend(create_qa_tools(case_dir, project_dir))

    return all_tools


def create_auto_sleuth_mcp_server(case_dir: Path, project_dir: Path):
    """
    Create an MCP server with auto-sleuth custom tools.

    Args:
        case_dir: Path to the case directory
        project_dir: Path to the project root

    Returns:
        MCP server instance, or None if SDK tools not available
    """
    if not SDK_TOOLS_AVAILABLE:
        return None

    tools = create_all_tools(case_dir, project_dir)

    return create_sdk_mcp_server(name="auto-sleuth", version="1.0.0", tools=tools)


def is_tools_available() -> bool:
    """Check if SDK tools functionality is available."""
    return SDK_TOOLS_AVAILABLE
