"""
Utility functions for implementation planner.
"""

from .models import PlannerContext


def extract_feature_name(context: PlannerContext) -> str:
    """Extract feature name from case."""
    # Try to find title in case
    lines = context.case_content.split("\n")
    for line in lines[:10]:
        if line.startswith("# "):
            title = line[2:].strip()
            # Remove common prefixes
            for prefix in ["Caseification:", "Case:", "Feature:"]:
                if title.startswith(prefix):
                    title = title[len(prefix) :].strip()
            return title

    return "Unnamed Feature"


def group_files_by_service(context: PlannerContext) -> dict[str, list[dict]]:
    """Group files to modify by service."""
    groups: dict[str, list[dict]] = {}

    for file_info in context.files_to_modify:
        path = file_info.get("path", "")
        service = file_info.get("service", "unknown")

        # Try to infer service from path if not caseified
        if service == "unknown":
            for svc_name, svc_info in context.project_index.get("services", {}).items():
                svc_path = svc_info.get("path", svc_name)
                if path.startswith(svc_path) or path.startswith(f"{svc_name}/"):
                    service = svc_name
                    break

        if service not in groups:
            groups[service] = []
        groups[service].append(file_info)

    return groups


def get_patterns_for_service(context: PlannerContext, service: str) -> list[str]:
    """Get reference patterns for a service."""
    patterns = []
    for file_info in context.files_to_reference:
        file_service = file_info.get("service", "")
        if file_service == service or not file_service:
            patterns.append(file_info.get("path", ""))
    return patterns[:3]  # Limit to top 3


def create_verification(
    context: PlannerContext, service: str, subtask_type: str
) -> dict:
    """Create appropriate validation payload for an analysis task."""
    service_info = context.project_index.get("services", {}).get(service, {})
    port = service_info.get("port")

    if subtask_type == "model":
        return {
            "type": "command",
            "run": "echo 'Model created - verify with migration'",
        }
    elif subtask_type == "endpoint":
        return {
            "type": "api",
            "method": "GET",
            "url": f"http://localhost:{port}/health" if port else "/health",
            "expect_status": 200,
        }
    elif subtask_type == "component":
        return {
            "type": "browser",
            "scenario": "Component renders without errors",
        }
    elif subtask_type == "task":
        return {
            "type": "command",
            "run": "echo 'Task registered - verify with celery incaset'",
        }
    else:
        return {"type": "manual"}


def extract_acceptance_criteria(context: PlannerContext) -> list[str]:
    """Extract acceptance criteria from case."""
    criteria = []
    in_criteria_section = False

    for line in context.case_content.split("\n"):
        # Look for success criteria or acceptance sections
        if any(
            header in line.lower()
            for header in [
                "success criteria",
                "acceptance",
                "done when",
                "complete when",
            ]
        ):
            in_criteria_section = True
            continue

        if in_criteria_section:
            # Stop at next section
            if line.startswith("##"):
                break

            # Extract criteria (lines starting with -, *, or [])
            line = line.strip()
            if line.startswith(("- ", "* ", "- [ ]", "- [x]")):
                # Clean up the line
                criterion = line.lstrip("-*[] x").strip()
                if criterion:
                    criteria.append(criterion)

    # If no criteria found, create generic ones
    if not criteria:
        criteria = [
            "Feature works as caseified",
            "No console errors",
            "No regressions in existing functionality",
        ]

    return criteria


def determine_service_order(files_by_service: dict[str, list[dict]]) -> list[str]:
    """Determine service order (backend first, then workers, then frontend)."""
    service_order = []

    # Backend services first
    for svc in ["backend", "api", "server"]:
        if svc in files_by_service:
            service_order.append(svc)

    # Worker services second
    for svc in ["worker", "celery", "jobs", "tasks"]:
        if svc in files_by_service:
            service_order.append(svc)

    # Frontend services third
    for svc in ["frontend", "web", "client", "ui"]:
        if svc in files_by_service:
            service_order.append(svc)

    # Add any remaining services
    for svc in files_by_service:
        if svc not in service_order:
            service_order.append(svc)

    return service_order


def infer_subtask_type(path: str) -> str:
    """Infer subtask type from file path."""
    path_lower = path.lower()

    if "model" in path_lower or "schema" in path_lower:
        return "model"
    elif "route" in path_lower or "endpoint" in path_lower or "api" in path_lower:
        return "endpoint"
    elif "component" in path_lower or path.endswith(".tsx") or path.endswith(".jsx"):
        return "component"
    elif "task" in path_lower or "worker" in path_lower or "celery" in path_lower:
        return "task"
    else:
        return "code"
