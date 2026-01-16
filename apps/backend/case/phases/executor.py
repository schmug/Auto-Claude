"""
Phase Executor
==============

Main class that executes individual phases of case creation.
Combines all phase implementation mixins.
"""

from collections.abc import Callable
from pathlib import Path

from .discovery_phases import DiscoveryPhaseMixin
from .planning_phases import PlanningPhaseMixin
from .requirements_phases import RequirementsPhaseMixin
from .case_phases import CasePhaseMixin
from .utils import run_script


class PhaseExecutor(
    DiscoveryPhaseMixin,
    RequirementsPhaseMixin,
    CasePhaseMixin,
    PlanningPhaseMixin,
):
    """
    Executes individual phases of case creation.

    This class combines multiple mixins, each handling a caseific category of phases:
    - DiscoveryPhaseMixin: Discovery and context gathering phases
    - RequirementsPhaseMixin: Requirements, historical context, and research phases
    - CasePhaseMixin: Case writing and self-critique phases
    - PlanningPhaseMixin: Investigation planning and validation phases
    """

    def __init__(
        self,
        project_dir: Path,
        case_dir: Path,
        task_description: str,
        case_validator,
        run_agent_fn: Callable,
        task_logger,
        ui_module,
    ):
        """
        Initialize the phase executor.

        Args:
            project_dir: Root directory of the project
            case_dir: Directory for case outputs
            task_description: Description of the task to implement
            case_validator: Validator for case files
            run_agent_fn: Async function to run agent with a prompt
            task_logger: Logger for task progress
            ui_module: UI module for status messages
        """
        self.project_dir = project_dir
        self.case_dir = case_dir
        self.task_description = task_description
        self.case_validator = case_validator
        self.run_agent_fn = run_agent_fn
        self.task_logger = task_logger
        self.ui = ui_module

    def _run_script(self, script: str, args: list[str]) -> tuple[bool, str]:
        """
        Run a Python script and return (success, output).

        Args:
            script: Name of the script to run
            args: Command-line arguments for the script

        Returns:
            Tuple of (success: bool, output: str)
        """
        return run_script(self.project_dir, script, args)
