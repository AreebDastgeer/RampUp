"""
Repository Intelligence Engine — orchestrates all analyzers.

This is the single entry point called by github_service after cloning.
It runs real code analysis before the LLM is invoked, producing structured
metadata the API and onboarding prompt can treat as factual.
"""

from pathlib import Path

from repo_intelligence.entry_points import merge_entry_points
from repo_intelligence.health import detect_repository_health
from repo_intelligence.important_files import find_important_files
from repo_intelligence.frontend_analyzer import analyze_frontend_repository
from repo_intelligence.js_analyzer import (
    analyze_js_repository,
    detect_node_entry_from_package_json,
    js_analysis_to_dict,
)
from repo_intelligence.python_analyzer import (
    analyze_python_repository,
    python_analysis_to_dict,
)

# Map frequently imported packages to human-readable technology labels.
PACKAGE_TECH_LABELS = {
    "fastapi": "FastAPI",
    "flask": "Flask",
    "django": "Django",
    "uvicorn": "Uvicorn",
    "starlette": "Starlette",
    "pydantic": "Pydantic",
    "sqlalchemy": "SQLAlchemy",
    "pytest": "pytest",
    "next": "Next.js",
    "react": "React",
    "vue": "Vue",
    "express": "Express",
    "@nestjs/core": "NestJS",
    "typescript": "TypeScript",
}


def _merge_dependency_maps(python_edges: list[dict], js_edges: list[dict]) -> list[dict]:
    seen: set[tuple[str, str]] = set()
    merged: list[dict] = []
    for edge in python_edges + js_edges:
        key = (edge["source"], edge["target"])
        if key in seen:
            continue
        seen.add(key)
        merged.append(edge)
    return merged


def _merge_unique(existing: list[str], additions: list[str]) -> list[str]:
    merged = list(existing)
    seen = {item.lower() for item in merged}
    for item in additions:
        normalized = item.lower()
        if normalized in seen:
            continue
        seen.add(normalized)
        merged.append(item)
    return merged


def _merge_largest_files(python_list: list[dict], js_list: list[dict]) -> list[dict]:
    combined = python_list + js_list
    return sorted(combined, key=lambda item: (-item.get("lines", 0), item.get("path", "")))[:10]


def _merge_import_rankings(python_list: list[dict], js_list: list[dict]) -> list[dict]:
    combined = python_list + js_list
    return sorted(combined, key=lambda item: (-item.get("import_count", 0), item.get("path", "")))[:10]


def _technologies_from_imports(
    existing_tech: list[str],
    python_packages: list[dict],
    js_packages: list[dict],
) -> list[str]:
    """Augment manifest-based tech stack with packages found in source imports."""

    detected = list(existing_tech)
    seen = {t.lower() for t in detected}

    for entry in python_packages + js_packages:
        pkg = entry.get("package", "").lower()
        label = PACKAGE_TECH_LABELS.get(pkg)
        if label and label.lower() not in seen:
            seen.add(label.lower())
            detected.append(label)

    if any(p.get("package") == "fastapi" for p in python_packages) and "Python" not in detected:
        detected.append("Python")
    if js_packages and "Node.js" not in detected:
        detected.append("Node.js")

    return detected


def analyze_repository_intelligence(
    repo_path: Path,
    *,
    existing_tech_stack: list[str],
    filename_entry_points: list[str],
    legacy_file_scorer,
) -> dict:
    """
    Run the full intelligence pipeline on a cloned repository.

    Parameters
    ----------
    repo_path:
        Root of the shallow-cloned repository.
    existing_tech_stack:
        Technologies already detected from manifests (github_service).
    filename_entry_points:
        Entry points found by filename heuristics — kept as fallback.
    legacy_file_scorer:
        Callable(path) -> int from github_service._score_file for unscored files.
    """

    python_result = analyze_python_repository(repo_path)
    js_result = analyze_js_repository(repo_path)
    frontend_result = analyze_frontend_repository(repo_path)

    python_dict = python_analysis_to_dict(python_result)
    js_dict = js_analysis_to_dict(js_result)

    technologies = _merge_unique(
        _technologies_from_imports(
            existing_tech_stack,
            python_dict["imports"]["frequent_packages"],
            js_dict["imports"]["frequent_packages"],
        ),
        frontend_result["technologies"],
    )

    entry_paths, entry_details = merge_entry_points(
        repo_path,
        filename_entry_points,
        python_dict["detected_entry_points"],
        js_dict["detected_entry_points"]
        + frontend_result["entry_point_details"]
        + detect_node_entry_from_package_json(repo_path),
        technologies,
    )

    api_endpoints = python_dict["api_endpoints"] + js_dict["api_endpoints"]
    dependency_map = _merge_dependency_maps(
        python_dict["dependency_map"],
        js_dict["dependency_map"],
    )
    largest_files = _merge_largest_files(
        python_dict["largest_files"],
        js_dict["largest_files"],
    )
    files_with_most_imports = _merge_import_rankings(
        python_dict["files_with_most_imports"],
        js_dict["files_with_most_imports"],
    )

    important_files = find_important_files(
        repo_path,
        entry_point_paths=entry_paths,
        api_endpoints=api_endpoints,
        files_with_most_imports=files_with_most_imports,
        largest_files=largest_files,
        legacy_scorer=legacy_file_scorer,
    )

    repository_health = detect_repository_health(repo_path)

    # Merge per-file imports from Python and JS into one lookup table.
    imports_by_file = {
        **python_dict["imports"]["by_file"],
        **js_dict["imports"]["by_file"],
    }
    frequent_packages = sorted(
        {
            entry["package"]: entry["count"]
            for entry in (
                python_dict["imports"]["frequent_packages"]
                + js_dict["imports"]["frequent_packages"]
            )
        }.items(),
        key=lambda item: (-item[1], item[0]),
    )
    frequent_packages = [{"package": p, "count": c} for p, c in frequent_packages[:20]]

    return {
        "technologies": technologies,
        "entry_points": entry_paths,
        "entry_point_details": entry_details,
        "imports": {
            "by_file": imports_by_file,
            "frequent_packages": frequent_packages,
        },
        "api_endpoints": api_endpoints,
        "dependency_map": dependency_map,
        "repository_health": repository_health,
        "code_analysis": {
            "python_files_analyzed": python_dict["files_analyzed"],
            "javascript_files_analyzed": js_dict["files_analyzed"],
            "classes": python_dict["classes"],
            "functions": python_dict["functions"],
            "largest_files": largest_files,
            "files_with_most_imports": files_with_most_imports,
        },
        "important_files": important_files,
    }
