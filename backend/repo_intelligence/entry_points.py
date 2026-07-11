"""
Dynamic entry-point detection — combines code signals with framework conventions.

Filename heuristics from github_service are preserved as a fallback layer;
AST/regex signals and manifest fields take priority because they reflect
what the code actually does.
"""

from pathlib import Path

from repo_intelligence.js_analyzer import detect_node_entry_from_package_json
from repo_intelligence.utils import iter_repo_files, relative_posix_path

# Framework-specific paths checked when conventional layout is detected.
FRAMEWORK_ENTRY_CANDIDATES = {
    "fastapi": ("main.py", "app.py", "server.py", "backend/main.py", "src/main.py"),
    "flask": ("app.py", "wsgi.py", "run.py", "backend/app.py"),
    "django": ("manage.py",),
    "next.js": (
        "app/page.tsx", "app/page.ts", "app/page.jsx", "app/page.js",
        "pages/index.tsx", "pages/index.ts", "pages/index.js",
        "src/app/page.tsx",
    ),
    "express": ("index.js", "server.js", "app.js", "src/index.ts", "src/server.ts"),
}


def _normalize_entry(entry: dict | str) -> dict:
    if isinstance(entry, str):
        return {"path": entry, "reason": "filename heuristic", "source": "filename"}
    return entry


def _dedupe_entries(entries: list[dict]) -> list[str]:
    """Return ordered unique paths for API compatibility with existing entry_points field."""

    seen: set[str] = set()
    ordered: list[str] = []
    for entry in entries:
        normalized = _normalize_entry(entry)
        path = normalized["path"]
        if path not in seen:
            seen.add(path)
            ordered.append(path)
    return ordered


def _dedupe_entry_details(entries: list[dict]) -> list[dict]:
    seen: set[str] = set()
    result: list[dict] = []
    for entry in entries:
        normalized = _normalize_entry(entry)
        if normalized["path"] in seen:
            continue
        seen.add(normalized["path"])
        result.append(normalized)
    return result


def detect_framework_entry_candidates(repo_path: Path, technologies: list[str]) -> list[dict]:
    """Add conventional paths when a framework is detected in the tech stack."""

    found: list[dict] = []
    tech_lower = {t.lower() for t in technologies}

    for framework, candidates in FRAMEWORK_ENTRY_CANDIDATES.items():
        if framework not in tech_lower and framework.replace(".", "") not in tech_lower:
            continue
        for candidate in candidates:
            if (repo_path / candidate).is_file():
                found.append({
                    "path": candidate,
                    "reason": f"{framework} convention",
                    "source": "framework_convention",
                })

    return found


def detect_nextjs_app_router_entries(repo_path: Path) -> list[dict]:
    """Next.js App Router pages are entry surfaces even without main.py."""

    found: list[dict] = []
    for file_path in iter_repo_files(repo_path, extensions=frozenset({".tsx", ".ts", ".jsx", ".js"}), max_depth=5):
        rel = relative_posix_path(repo_path, file_path)
        name = file_path.name.lower()
        if name in {"page.tsx", "page.ts", "page.jsx", "page.js"} and "/app/" in f"/{rel}/":
            found.append({
                "path": rel,
                "reason": "Next.js App Router page",
                "source": "nextjs_convention",
            })
    return found


def merge_entry_points(
    repo_path: Path,
    filename_entries: list[str],
    python_entries: list[dict],
    js_entries: list[dict],
    technologies: list[str],
) -> tuple[list[str], list[dict]]:
    """
    Merge all entry-point signals into API paths and detailed metadata.
    Code-detected entries are listed first (higher confidence).
    """

    combined: list[dict] = []

    combined.extend(python_entries)
    combined.extend(js_entries)
    combined.extend(detect_node_entry_from_package_json(repo_path))
    combined.extend(detect_framework_entry_candidates(repo_path, technologies))
    combined.extend(detect_nextjs_app_router_entries(repo_path))

    for path in filename_entries:
        combined.append({
            "path": path,
            "reason": "known entry filename",
            "source": "filename_heuristic",
        })

    detailed = _dedupe_entry_details(combined)
    paths = _dedupe_entries(detailed)
    return paths, detailed
