"""
Execution phase event protocol for frontend synchronization.

Protocol: __EXEC_PHASE__:{"phase":"analysis","message":"Starting"}

DFIR Execution Phases:
- intake: Case intake and scoping
- planning: Investigation planning
- collection: Evidence collection
- analysis: Evidence analysis
- enrichment: Threat intelligence enrichment
- validation: Evidence validation
- reporting: Report generation
- complete: Investigation complete
- failed: Investigation failed
"""

import json
import os
import sys
from enum import Enum
from typing import Any

PHASE_MARKER_PREFIX = "__EXEC_PHASE__:"
_DEBUG = os.environ.get("DEBUG", "").lower() in ("1", "true", "yes")


class ExecutionPhase(str, Enum):
    """Maps to frontend's ExecutionPhase type for case card badges.
    
    DFIR Investigation Phases:
    - INTAKE: Initial case intake and scoping
    - PLANNING: Creating the investigation plan
    - COLLECTION: Evidence collection and preservation
    - ANALYSIS: Evidence analysis and IOC extraction
    - ENRICHMENT: Threat intelligence enrichment
    - VALIDATION: Evidence validation and chain of custody verification
    - REPORTING: Report generation
    - COMPLETE: Investigation complete
    - FAILED: Investigation failed
    """

    # DFIR Phases
    INTAKE = "intake"
    PLANNING = "planning"
    COLLECTION = "collection"
    ANALYSIS = "analysis"
    ENRICHMENT = "enrichment"
    VALIDATION = "validation"
    REPORTING = "reporting"
    COMPLETE = "complete"
    FAILED = "failed"
    
    # Legacy aliases for backward compatibility
    CODING = "analysis"  # Maps to ANALYSIS
    QA_REVIEW = "validation"  # Maps to VALIDATION
    QA_FIXING = "validation"  # Maps to VALIDATION


# Legacy phase mapping for backward compatibility
LEGACY_PHASE_MAP = {
    "coding": ExecutionPhase.ANALYSIS,
    "qa_review": ExecutionPhase.VALIDATION,
    "qa_fixing": ExecutionPhase.VALIDATION,
}


def emit_phase(
    phase: ExecutionPhase | str,
    message: str = "",
    *,
    progress: int | None = None,
    subtask: str | None = None,
    investigation_step: str | None = None,
    iocs_found: int | None = None,
) -> None:
    """Emit structured phase event to stdout for frontend parsing.
    
    Args:
        phase: Current execution phase
        message: Human-readable status message
        progress: Progress percentage (0-100)
        subtask: Current subtask/step being executed
        investigation_step: Current investigation step ID
        iocs_found: Number of IOCs found so far
    """
    phase_value = phase.value if isinstance(phase, ExecutionPhase) else phase
    
    # Map legacy phases to DFIR phases
    if phase_value in LEGACY_PHASE_MAP:
        phase_value = LEGACY_PHASE_MAP[phase_value].value

    payload: dict[str, Any] = {
        "phase": phase_value,
        "message": message,
    }

    if progress is not None:
        if not (0 <= progress <= 100):
            progress = max(0, min(100, progress))
        payload["progress"] = progress

    if subtask is not None:
        payload["subtask"] = subtask
        
    # DFIR-specific fields
    if investigation_step is not None:
        payload["investigation_step"] = investigation_step
        
    if iocs_found is not None:
        payload["iocs_found"] = iocs_found

    try:
        print(f"{PHASE_MARKER_PREFIX}{json.dumps(payload, default=str)}", flush=True)
    except (OSError, UnicodeEncodeError) as e:
        if _DEBUG:
            try:
                sys.stderr.write(f"[phase_event] emit failed: {e}\n")
                sys.stderr.flush()
            except (OSError, UnicodeEncodeError):
                pass  # Truly silent on complete I/O failure


def emit_investigation_progress(
    phase: ExecutionPhase,
    step_id: str,
    step_description: str,
    completed_steps: int,
    total_steps: int,
    iocs_found: int = 0,
) -> None:
    """Emit investigation progress event with step details.
    
    Args:
        phase: Current execution phase
        step_id: Investigation step ID (e.g., "step-2-1")
        step_description: Human-readable step description
        completed_steps: Number of completed steps
        total_steps: Total number of steps
        iocs_found: Number of IOCs found so far
    """
    progress = int((completed_steps / total_steps) * 100) if total_steps > 0 else 0
    
    emit_phase(
        phase=phase,
        message=step_description,
        progress=progress,
        investigation_step=step_id,
        iocs_found=iocs_found,
    )
