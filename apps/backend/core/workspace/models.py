#!/usr/bin/env python3
"""
Workspace Models
================

Data classes and enums for workspace management.
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class WorkspaceMode(Enum):
    """How auto-sleuth should work."""

    ISOLATED = "isolated"  # Work in a separate worktree (safe)
    DIRECT = "direct"  # Work directly in user's project


class WorkspaceChoice(Enum):
    """User's choice after build completes."""

    MERGE = "merge"  # Add changes to project
    REVIEW = "review"  # Show what changed
    TEST = "test"  # Validate the case in the staging worktree
    LATER = "later"  # Decide later


@dataclass
class ParallelMergeTask:
    """A file merge task to be executed in parallel."""

    file_path: str
    main_content: str
    worktree_content: str
    base_content: str | None
    case_name: str
    project_dir: Path


@dataclass
class ParallelMergeResult:
    """Result of a parallel merge task."""

    file_path: str
    merged_content: str | None
    success: bool
    error: str | None = None
    was_auto_merged: bool = False  # True if git auto-merged without AI


class MergeLockError(Exception):
    """Raised when a merge lock cannot be acquired."""

    pass


class MergeLock:
    """
    Context manager for merge locking to prevent concurrent merges.

    Uses a lock file in .auto-sleuth/ to ensure only one merge operation
    runs at a time for a given project.
    """

    def __init__(self, project_dir: Path, case_name: str):
        self.project_dir = project_dir
        self.case_name = case_name
        self.lock_dir = project_dir / ".auto-sleuth" / ".locks"
        self.lock_file = self.lock_dir / f"merge-{case_name}.lock"
        self.acquired = False

    def __enter__(self):
        """Acquire the merge lock."""
        import os
        import time

        self.lock_dir.mkdir(parents=True, exist_ok=True)

        # Try to acquire lock with timeout
        max_wait = 30  # seconds
        start_time = time.time()

        while True:
            try:
                # Try to create lock file exclusively
                fd = os.open(
                    str(self.lock_file),
                    os.O_CREAT | os.O_EXCL | os.O_WRONLY,
                    0o644,
                )
                os.close(fd)

                # Write our PID to the lock file
                self.lock_file.write_text(str(os.getpid()))
                self.acquired = True
                return self

            except FileExistsError:
                # Lock file exists - check if process is still running
                if self.lock_file.exists():
                    try:
                        pid = int(self.lock_file.read_text().strip())
                        # Import locally to avoid circular dependency
                        import os as _os

                        try:
                            _os.kill(pid, 0)
                            is_running = True
                        except (OSError, ProcessLookupError):
                            is_running = False

                        if not is_running:
                            # Stale lock - remove it
                            self.lock_file.unlink()
                            continue
                    except (ValueError, ProcessLookupError):
                        # Invalid PID or can't check - remove stale lock
                        self.lock_file.unlink()
                        continue

                # Active lock - wait or timeout
                if time.time() - start_time >= max_wait:
                    raise MergeLockError(
                        f"Could not acquire merge lock for {self.case_name} after {max_wait}s"
                    )

                time.sleep(0.5)

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Release the merge lock."""
        if self.acquired and self.lock_file.exists():
            try:
                self.lock_file.unlink()
            except Exception:
                pass  # Best effort cleanup


class CaseNumberLockError(Exception):
    """Raised when a case number lock cannot be acquired."""

    pass


class CaseNumberLock:
    """
    Context manager for case number coordination across main project and worktrees.

    Prevents race conditions when creating cases by:
    1. Acquiring an exclusive file lock
    2. Scanning ALL case locations (main + worktrees)
    3. Finding global maximum case number
    4. Allowing atomic case directory creation
    5. Releasing lock
    """

    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.lock_dir = project_dir / ".auto-sleuth" / ".locks"
        self.lock_file = self.lock_dir / "case-numbering.lock"
        self.acquired = False
        self._global_max: int | None = None

    def __enter__(self) -> "CaseNumberLock":
        """Acquire the case numbering lock."""
        import os
        import time

        self.lock_dir.mkdir(parents=True, exist_ok=True)

        max_wait = 30  # seconds
        start_time = time.time()

        while True:
            try:
                # Try to create lock file exclusively (atomic operation)
                fd = os.open(
                    str(self.lock_file),
                    os.O_CREAT | os.O_EXCL | os.O_WRONLY,
                    0o644,
                )
                os.close(fd)

                # Write our PID to the lock file
                self.lock_file.write_text(str(os.getpid()))
                self.acquired = True
                return self

            except FileExistsError:
                # Lock file exists - check if process is still running
                if self.lock_file.exists():
                    try:
                        pid = int(self.lock_file.read_text().strip())
                        import os as _os

                        try:
                            _os.kill(pid, 0)
                            is_running = True
                        except (OSError, ProcessLookupError):
                            is_running = False

                        if not is_running:
                            # Stale lock - remove it
                            self.lock_file.unlink()
                            continue
                    except (ValueError, ProcessLookupError):
                        # Invalid PID or can't check - remove stale lock
                        self.lock_file.unlink()
                        continue

                # Active lock - wait or timeout
                if time.time() - start_time >= max_wait:
                    raise CaseNumberLockError(
                        f"Could not acquire case numbering lock after {max_wait}s"
                    )

                time.sleep(0.1)  # Shorter sleep for case creation

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Release the case numbering lock."""
        if self.acquired and self.lock_file.exists():
            try:
                self.lock_file.unlink()
            except Exception:
                pass  # Best effort cleanup

    def get_next_case_number(self) -> int:
        """
        Scan all case locations and return the next available case number.

        Must be called while lock is held.

        Returns:
            Next available case number (global max + 1)
        """
        if not self.acquired:
            raise CaseNumberLockError(
                "Lock must be acquired before getting next case number"
            )

        if self._global_max is not None:
            return self._global_max + 1

        max_number = 0

        # 1. Scan main project cases
        main_cases_dir = self.project_dir / ".auto-sleuth" / "cases"
        max_number = max(max_number, self._scan_cases_dir(main_cases_dir))

        # 2. Scan all worktree cases
        worktrees_dir = self.project_dir / ".auto-sleuth" / "worktrees" / "tasks"
        if worktrees_dir.exists():
            for worktree in worktrees_dir.iterdir():
                if worktree.is_dir():
                    worktree_cases = worktree / ".auto-sleuth" / "cases"
                    max_number = max(max_number, self._scan_cases_dir(worktree_cases))

        self._global_max = max_number
        return max_number + 1

    def _scan_cases_dir(self, cases_dir: Path) -> int:
        """Scan a cases directory and return the highest case number found."""
        if not cases_dir.exists():
            return 0

        max_num = 0
        for folder in cases_dir.glob("[0-9][0-9][0-9]-*"):
            try:
                num = int(folder.name[:3])
                max_num = max(max_num, num)
            except ValueError:
                pass

        return max_num
