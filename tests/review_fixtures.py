#!/usr/bin/env python3
"""
Shared Fixtures for Review System Tests
========================================

Common fixtures used across review module tests.
"""

import json
from pathlib import Path
from typing import Generator

import pytest

from review.state import ReviewState


@pytest.fixture
def review_spec_dir(tmp_path: Path) -> Path:
    """Create a spec directory with spec.md and investigation_plan.json."""
    spec_dir = tmp_path / "spec"
    spec_dir.mkdir(parents=True)

    # Create spec.md
    spec_content = """# Test Feature

## Overview

This is a test feature specification for unit testing purposes.

## Workflow Type

**Type**: feature

## Files to Modify

| File | Service | What to Change |
|------|---------|---------------|
| `app/main.py` | backend | Add new endpoint |
| `src/components/Test.tsx` | frontend | Add new component |

## Files to Create

| File | Service | Purpose |
|------|---------|---------|
| `app/utils/helper.py` | backend | Helper functions |

## Success Criteria

The task is complete when:

- [ ] New endpoint responds correctly
- [ ] Component renders without errors
- [ ] All tests pass
"""
    (spec_dir / "spec.md").write_text(spec_content)

    # Create investigation_plan.json
    plan = {
        "case_id": "case-001",
        "case_name": "Test Feature",
        "investigation_type": "feature",
        "evidence_sources": ["backend", "frontend"],
        "phases": [
            {
                "phase": 1,
                "name": "Backend Foundation",
                "type": "analysis",
                "analysis_tasks": [
                    {
                        "id": "chunk-1-1",
                        "description": "Add new endpoint",
                        "evidence_source": "backend",
                        "status": "pending",
                    },
                ],
            },
        ],
        "final_acceptance": ["Feature works correctly"],
        "summary": {
            "total_phases": 1,
            "total_tasks": 1,
        },
    }
    (spec_dir / "investigation_plan.json").write_text(json.dumps(plan, indent=2))

    return spec_dir


@pytest.fixture
def complete_spec_dir(tmp_path: Path) -> Path:
    """Create a complete spec directory mimicking real spec_runner output."""
    spec_dir = tmp_path / "specs" / "001-test-feature"
    spec_dir.mkdir(parents=True)

    # Create a realistic spec.md
    spec_content = """# Specification: Test Feature Implementation

## Overview

This is a test feature that adds new functionality to the system.
It involves changes to both backend and frontend components.

## Workflow Type

**Type**: feature

**Rationale**: New capability requiring multiple coordinated changes.

## Task Scope

### Services Involved
- **backend** - API endpoints and business logic
- **frontend** - UI components and state management

### This Task Will:
- [ ] Add new REST API endpoint
- [ ] Create frontend form component
- [ ] Add validation logic
- [ ] Write unit tests

### Out of Scope:
- Database schema changes
- Authentication modifications

## Files to Modify

| File | Service | What to Change |
|------|---------|---------------|
| `app/api/routes.py` | backend | Add new endpoint |
| `src/components/Form.tsx` | frontend | Add form component |
| `app/services/processor.py` | backend | Add business logic |

## Files to Create

| File | Service | Purpose |
|------|---------|---------|
| `app/api/handlers/new_feature.py` | backend | Handler implementation |
| `src/components/NewFeature/index.tsx` | frontend | New component |
| `tests/test_new_feature.py` | backend | Unit tests |

## Requirements

### Functional Requirements

1. **API Endpoint**
   - Description: New endpoint for feature data
   - Acceptance: Returns correct JSON response

2. **Form Component**
   - Description: User-facing form for data entry
   - Acceptance: Form validates and submits correctly

## Success Criteria

The task is complete when:

- [ ] API endpoint returns correct response format
- [ ] Form component renders without errors
- [ ] Form validation works correctly
- [ ] Unit tests pass with >80% coverage
- [ ] Integration tests pass
"""
    (spec_dir / "spec.md").write_text(spec_content)

    # Create a realistic investigation_plan.json
    plan = {
        "case_id": "case-002",
        "case_name": "Test Feature Implementation",
        "investigation_type": "feature",
        "evidence_sources": ["backend", "frontend"],
        "phases": [
            {
                "phase": 1,
                "name": "Backend Foundation",
                "type": "analysis",
                "depends_on": [],
                "parallel_safe": True,
                "analysis_tasks": [
                    {
                        "id": "chunk-1-1",
                        "description": "Create API endpoint handler",
                        "evidence_source": "backend",
                        "artifacts_to_produce": ["app/api/handlers/new_feature.py"],
                        "artifacts_to_analyze": ["app/api/routes.py"],
                        "status": "pending",
                    },
                    {
                        "id": "chunk-1-2",
                        "description": "Add business logic",
                        "evidence_source": "backend",
                        "artifacts_to_analyze": ["app/services/processor.py"],
                        "status": "pending",
                    },
                ],
            },
            {
                "phase": 2,
                "name": "Frontend Implementation",
                "type": "analysis",
                "depends_on": [1],
                "parallel_safe": False,
                "analysis_tasks": [
                    {
                        "id": "chunk-2-1",
                        "description": "Create form component",
                        "evidence_source": "frontend",
                        "artifacts_to_produce": ["src/components/NewFeature/index.tsx"],
                        "artifacts_to_analyze": ["src/components/Form.tsx"],
                        "status": "pending",
                    },
                ],
            },
            {
                "phase": 3,
                "name": "Testing",
                "type": "validation",
                "depends_on": [1, 2],
                "parallel_safe": True,
                "analysis_tasks": [
                    {
                        "id": "chunk-3-1",
                        "description": "Add unit tests",
                        "evidence_source": "backend",
                        "artifacts_to_produce": ["tests/test_new_feature.py"],
                        "status": "pending",
                    },
                ],
            },
        ],
        "final_acceptance": [
            "All API endpoints work correctly",
            "Frontend components render without errors",
            "All tests pass",
        ],
        "summary": {
            "total_phases": 3,
            "total_tasks": 4,
            "evidence_sources": ["backend", "frontend"],
            "parallelism": {
                "max_parallel_phases": 1,
                "recommended_workers": 2,
            },
        },
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00",
    }
    (spec_dir / "investigation_plan.json").write_text(json.dumps(plan, indent=2))

    return spec_dir


@pytest.fixture
def approved_state() -> ReviewState:
    """Create an approved ReviewState."""
    return ReviewState(
        approved=True,
        approved_by="test_user",
        approved_at="2024-01-15T10:30:00",
        feedback=["Looks good!", "Minor suggestion added."],
        spec_hash="abc123",
        review_count=2,
    )


@pytest.fixture
def pending_state() -> ReviewState:
    """Create a pending (not approved) ReviewState."""
    return ReviewState(
        approved=False,
        approved_by="",
        approved_at="",
        feedback=["Need more details on API."],
        spec_hash="",
        review_count=1,
    )
