"""
Utility functions for task logging.
"""

from pathlib import Path

from .logger import TaskLogger

# Global logger instance for easy access
_current_logger: TaskLogger | None = None


def get_task_logger(
    case_dir: Path | None = None, emit_markers: bool = True
) -> TaskLogger | None:
    """
    Get or create a task logger for the given case directory.

    Args:
        case_dir: Path to the case directory (creates new logger if different from current)
        emit_markers: Whether to emit streaming markers

    Returns:
        TaskLogger instance or None if no case_dir
    """
    global _current_logger

    if case_dir is None:
        return _current_logger

    if _current_logger is None or _current_logger.case_dir != case_dir:
        _current_logger = TaskLogger(case_dir, emit_markers)

    return _current_logger


def clear_task_logger() -> None:
    """Clear the global task logger."""
    global _current_logger
    _current_logger = None


def update_task_logger_path(new_case_dir: Path) -> None:
    """
    Update the global task logger's case directory after a rename.

    This should be called after renaming a case directory to ensure
    the logger continues writing to the correct location.

    Args:
        new_case_dir: The new path to the case directory
    """
    global _current_logger

    if _current_logger is None:
        return

    # Update the logger's internal paths
    _current_logger.case_dir = Path(new_case_dir)
    _current_logger.log_file = _current_logger.case_dir / TaskLogger.LOG_FILE

    # Update case_id in the storage
    _current_logger.storage.update_case_id(new_case_dir.name)

    # Save to the new location
    _current_logger.storage.save()
