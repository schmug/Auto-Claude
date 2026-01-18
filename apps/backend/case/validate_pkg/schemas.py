"""
Validation Schemas
==================

JSON schemas and constants used for validating case outputs.
"""

# JSON Schemas for validation
INVESTIGATION_PLAN_SCHEMA = {
    # Core DFIR investigation plan shape.
    "required_fields": ["case_id", "case_name", "phases"],
    "optional_fields": [
        "case_type",
        "investigation_type",
        "investigation_rationale",
        "description",
        "client",
        "lead_analyst",
        "evidence_sources",
        "investigation_objectives",
        "final_deliverables",
        "final_acceptance",
        "created_at",
        "updated_at",
        "created_by",
        "case_file",
        "summary",
        "validation_strategy",
        "qa_acceptance",
        "qa_signoff",
        "status",
        "plan_status",
        "validation_status",
        "analyst_notes",
        "recovery_note",
        "metadata",
    ],
    "phase_schema": {
        # Support both numeric and string identifiers for phase IDs.
        "required_fields_either": [["phase", "id"]],
        "required_fields": ["name", "analysis_tasks"],
        "optional_fields": [
            "type",
            "depends_on",
            "parallel_safe",
            "description",
            "phase",
            "id",
            "evidence_scope",
            "expected_outputs",
        ],
        "phase_types": [
            "intake",
            "collection",
            "analysis",
            "correlation",
            "validation",
            "reporting",
            "evidence_collection",
            "evidence_preservation",
            "ioc_extraction",
            "timeline_reconstruction",
            "threat_intel_enrichment",
            "mitre_mapping",
            "remediation",
        ],
    },
    "task_schema": {
        "required_fields": ["id", "description", "status"],
        "optional_fields": [
            "evidence_source",
            "evidence_sources",
            "all_sources",
            "artifacts_to_analyze",
            "artifacts_to_examine",
            "artifacts_to_produce",
            "reference_patterns",
            "analysis_type",
            "ioc_categories",
            "ioc_type",
            "ioc_types",
            "ioc_value",
            "validation",
            "chain_of_custody",
            "notes",
            "timeline_scope",
            "output_files",
            "findings",
            "iocs_extracted",
            "error_message",
            "attempt_count",
            "depends_on",
            "started_at",
            "completed_at",
        ],
        "status_values": [
            "pending",
            "in_progress",
            "completed",
            "blocked",
            "failed",
            "skipped",
            "needs_review",
        ],
    },
    "verification_schema": {
        "required_fields": ["type"],
        "optional_fields": [
            "run",
            "url",
            "method",
            "expect_status",
            "expect_contains",
            "scenario",
            "steps",
            # DFIR validation payloads
            "command",
            "expected",
            "file",
            "regex",
            "instructions",
            "expected_min",
            "expected_max",
        ],
        "verification_types": [
            "command",
            "api",
            "browser",
            "component",
            "manual",
            "none",
            "e2e",
            # DFIR-specific verification types
            "count",      # Verify record/artifact count
            "pattern",    # Verify pattern presence in output
            "hash",       # Verify file hash integrity
            "timeline",   # Verify timeline consistency
            "artifact",   # Verify artifact exists/format
        ],
    },
}

CONTEXT_SCHEMA = {
    "required_fields": ["task_description"],
    "optional_fields": [
        "scoped_services",
        "files_to_modify",
        "files_to_reference",
        "patterns",
        "service_contexts",
        "created_at",
    ],
}

PROJECT_INDEX_SCHEMA = {
    "required_fields": ["project_type"],
    "optional_fields": [
        "services",
        "infrastructure",
        "conventions",
        "root_path",
        "created_at",
        "git_info",
    ],
    "project_types": ["single", "monorepo"],
}

SPEC_REQUIRED_SECTIONS = [
    "Overview",
    "Investigation Type",
    "Incident Scope",
    "Evidence Sources",
    "Initial IOCs",
    "Success Criteria",
]

SPEC_RECOMMENDED_SECTIONS = [
    "MITRE ATT&CK Mapping",
    "Artifacts to Analyze",
    "Detection Patterns",
    "Investigation Objectives",
    "Analysis Environment",
    "Validation Acceptance Criteria",
    "Constraints",
]
