"""
Phase Configuration Module
===========================

Handles model and thinking level configuration for different DFIR execution phases.
Reads configuration from case_metadata.json and provides resolved model IDs.
"""

import json
import os
from pathlib import Path
from typing import Literal, TypedDict

# Model shorthand to full model ID mapping
MODEL_ID_MAP: dict[str, str] = {
    "opus": "claude-opus-4-5-20251101",
    "sonnet": "claude-sonnet-4-5-20250929",
    "haiku": "claude-haiku-4-5-20251001",
}

# Thinking level to budget tokens mapping (None = no extended thinking)
# Values must match auto-dfir-ui/src/shared/constants/models.ts THINKING_BUDGET_MAP
THINKING_BUDGET_MAP: dict[str, int | None] = {
    "none": None,
    "low": 1024,
    "medium": 4096,  # Moderate analysis
    "high": 16384,  # Deep thinking for evidence validation
    "ultrathink": 65536,  # Maximum reasoning depth for complex analysis
}

# Case intake phase-specific thinking levels
# Heavy phases use ultrathink for deep analysis
# Light phases use medium after compaction
CASE_PHASE_THINKING_LEVELS: dict[str, str] = {
    # Heavy phases - ultrathink (discovery, case brief creation, self-critique)
    "discovery": "ultrathink",
    "case_brief_writing": "ultrathink",
    "self_critique": "ultrathink",
    # Light phases - medium (after first invocation with compaction)
    "requirements": "medium",
    "threat_research": "medium",
    "context": "medium",
    "planning": "medium",
    "validation": "medium",
    "quick_triage": "medium",
    "historical_context": "medium",
    "complexity_assessment": "medium",
}

# DFIR execution phases
# intake: Case intake and scoping
# planning: Investigation planning
# collection: Evidence collection
# analysis: Evidence analysis (requires deep thinking)
# enrichment: Threat intelligence enrichment
# validation: Evidence validation
# reporting: Report generation

# Default phase configuration for DFIR (fallback, matches 'Balanced' profile)
DEFAULT_PHASE_MODELS: dict[str, str] = {
    "intake": "sonnet",
    "planning": "sonnet",
    "collection": "sonnet",
    "analysis": "opus",  # Higher capability for complex forensic analysis
    "enrichment": "sonnet",
    "validation": "sonnet",
    "reporting": "sonnet",
}

DEFAULT_PHASE_THINKING: dict[str, str] = {
    "intake": "medium",
    "planning": "high",
    "collection": "medium",
    "analysis": "ultrathink",  # Deep analysis required for evidence examination
    "enrichment": "high",
    "validation": "high",
    "reporting": "medium",
}

# Legacy phase mapping for backward compatibility
LEGACY_PHASE_MAP: dict[str, str] = {
    "spec": "intake",
    "coding": "analysis",
    "qa": "validation",
}


class PhaseModelConfig(TypedDict, total=False):
    intake: str
    planning: str
    collection: str
    analysis: str
    enrichment: str
    validation: str
    reporting: str


class PhaseThinkingConfig(TypedDict, total=False):
    intake: str
    planning: str
    collection: str
    analysis: str
    enrichment: str
    validation: str
    reporting: str


class CaseMetadataConfig(TypedDict, total=False):
    """Structure of model-related fields in case_metadata.json"""

    isAutoProfile: bool
    phaseModels: PhaseModelConfig
    phaseThinking: PhaseThinkingConfig
    model: str
    thinkingLevel: str


Phase = Literal["intake", "planning", "collection", "analysis", "enrichment", "validation", "reporting"]


def resolve_model_id(model: str) -> str:
    """
    Resolve a model shorthand (haiku, sonnet, opus) to a full model ID.
    If the model is already a full ID, return it unchanged.

    Priority:
    1. Environment variable override (from API Profile)
    2. Hardcoded MODEL_ID_MAP
    3. Pass through unchanged (assume full model ID)

    Args:
        model: Model shorthand or full ID

    Returns:
        Full Claude model ID
    """
    # Check for environment variable override (from API Profile custom model mappings)
    if model in MODEL_ID_MAP:
        env_var_map = {
            "haiku": "ANTHROPIC_DEFAULT_HAIKU_MODEL",
            "sonnet": "ANTHROPIC_DEFAULT_SONNET_MODEL",
            "opus": "ANTHROPIC_DEFAULT_OPUS_MODEL",
        }
        env_var = env_var_map.get(model)
        if env_var:
            env_value = os.environ.get(env_var)
            if env_value:
                return env_value

        # Fall back to hardcoded mapping
        return MODEL_ID_MAP[model]

    # Already a full model ID or unknown shorthand
    return model


def get_thinking_budget(thinking_level: str) -> int | None:
    """
    Get the thinking budget for a thinking level.

    Args:
        thinking_level: Thinking level (none, low, medium, high, ultrathink)

    Returns:
        Token budget or None for no extended thinking
    """
    import logging

    if thinking_level not in THINKING_BUDGET_MAP:
        valid_levels = ", ".join(THINKING_BUDGET_MAP.keys())
        logging.warning(
            f"Invalid thinking_level '{thinking_level}'. Valid values: {valid_levels}. "
            f"Defaulting to 'medium'."
        )
        return THINKING_BUDGET_MAP["medium"]

    return THINKING_BUDGET_MAP[thinking_level]


def load_case_metadata(case_dir: Path) -> CaseMetadataConfig | None:
    """
    Load case_metadata.json from the case directory.

    Args:
        case_dir: Path to the case directory

    Returns:
        Parsed case metadata or None if not found
    """
    # Try new naming first, fall back to legacy
    metadata_path = case_dir / "case_metadata.json"
    if not metadata_path.exists():
        metadata_path = case_dir / "task_metadata.json"  # Legacy fallback
    if not metadata_path.exists():
        return None

    try:
        with open(metadata_path) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


# Alias for backward compatibility
load_task_metadata = load_case_metadata


def get_phase_model(
    case_dir: Path,
    phase: Phase,
    cli_model: str | None = None,
) -> str:
    """
    Get the resolved model ID for a specific DFIR execution phase.

    Priority:
    1. CLI argument (if provided)
    2. Phase-specific config from case_metadata.json (if auto profile)
    3. Single model from case_metadata.json (if not auto profile)
    4. Default phase configuration

    Args:
        case_dir: Path to the case directory
        phase: Execution phase (intake, planning, collection, analysis, enrichment, validation, reporting)
        cli_model: Model from CLI argument (optional)

    Returns:
        Resolved full model ID
    """
    # CLI argument takes precedence
    if cli_model:
        return resolve_model_id(cli_model)

    # Load case metadata
    metadata = load_case_metadata(case_dir)

    if metadata:
        # Check for auto profile with phase-specific config
        if metadata.get("isAutoProfile") and metadata.get("phaseModels"):
            phase_models = metadata["phaseModels"]
            model = phase_models.get(phase, DEFAULT_PHASE_MODELS.get(phase, "sonnet"))
            return resolve_model_id(model)

        # Non-auto profile: use single model
        if metadata.get("model"):
            return resolve_model_id(metadata["model"])

    # Fall back to default phase configuration
    return resolve_model_id(DEFAULT_PHASE_MODELS.get(phase, "sonnet"))


def get_phase_thinking(
    case_dir: Path,
    phase: Phase,
    cli_thinking: str | None = None,
) -> str:
    """
    Get the thinking level for a specific DFIR execution phase.

    Priority:
    1. CLI argument (if provided)
    2. Phase-specific config from case_metadata.json (if auto profile)
    3. Single thinking level from case_metadata.json (if not auto profile)
    4. Default phase configuration

    Args:
        case_dir: Path to the case directory
        phase: Execution phase (intake, planning, collection, analysis, enrichment, validation, reporting)
        cli_thinking: Thinking level from CLI argument (optional)

    Returns:
        Thinking level string
    """
    # CLI argument takes precedence
    if cli_thinking:
        return cli_thinking

    # Load case metadata
    metadata = load_case_metadata(case_dir)

    if metadata:
        # Check for auto profile with phase-specific config
        if metadata.get("isAutoProfile") and metadata.get("phaseThinking"):
            phase_thinking = metadata["phaseThinking"]
            return phase_thinking.get(phase, DEFAULT_PHASE_THINKING.get(phase, "medium"))

        # Non-auto profile: use single thinking level
        if metadata.get("thinkingLevel"):
            return metadata["thinkingLevel"]

    # Fall back to default phase configuration
    return DEFAULT_PHASE_THINKING.get(phase, "medium")


def get_phase_thinking_budget(
    case_dir: Path,
    phase: Phase,
    cli_thinking: str | None = None,
) -> int | None:
    """
    Get the thinking budget tokens for a specific DFIR execution phase.

    Args:
        case_dir: Path to the case directory
        phase: Execution phase (intake, planning, collection, analysis, enrichment, validation, reporting)
        cli_thinking: Thinking level from CLI argument (optional)

    Returns:
        Token budget or None for no extended thinking
    """
    thinking_level = get_phase_thinking(case_dir, phase, cli_thinking)
    return get_thinking_budget(thinking_level)


def get_phase_config(
    case_dir: Path,
    phase: Phase,
    cli_model: str | None = None,
    cli_thinking: str | None = None,
) -> tuple[str, str, int | None]:
    """
    Get the full configuration for a specific DFIR execution phase.

    Args:
        case_dir: Path to the case directory
        phase: Execution phase (intake, planning, collection, analysis, enrichment, validation, reporting)
        cli_model: Model from CLI argument (optional)
        cli_thinking: Thinking level from CLI argument (optional)

    Returns:
        Tuple of (model_id, thinking_level, thinking_budget)
    """
    model_id = get_phase_model(case_dir, phase, cli_model)
    thinking_level = get_phase_thinking(case_dir, phase, cli_thinking)
    thinking_budget = get_thinking_budget(thinking_level)

    return model_id, thinking_level, thinking_budget


def get_case_phase_thinking_budget(phase_name: str) -> int | None:
    """
    Get the thinking budget for a specific case intake phase.

    This maps granular case phases (discovery, case_brief_writing, etc.) to their
    appropriate thinking budgets based on CASE_PHASE_THINKING_LEVELS.

    Args:
        phase_name: Name of the case phase (e.g., 'discovery', 'case_brief_writing')

    Returns:
        Token budget for extended thinking, or None for no extended thinking
    """
    thinking_level = CASE_PHASE_THINKING_LEVELS.get(phase_name, "medium")
    return get_thinking_budget(thinking_level)


# Alias for backward compatibility
get_spec_phase_thinking_budget = get_case_phase_thinking_budget
