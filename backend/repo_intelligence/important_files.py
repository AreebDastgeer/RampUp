"""
Usefulness-based important file scoring.

Replaces pure filename priority with signals from code analysis: entry points,
routing files, high-import hubs, services, models, and config manifests.
"""

from pathlib import Path

from repo_intelligence.utils import iter_repo_files, relative_posix_path

# Retain existing high-value filename signals from github_service.
ENTRY_POINT_FILENAMES = frozenset({
    "main.py", "app.py", "server.py", "manage.py", "wsgi.py", "asgi.py", "run.py",
    "server.js", "index.js", "app.js", "main.js", "index.ts", "main.ts", "app.ts", "server.ts",
})

NEXT_APP_FILENAMES = frozenset({
    "page.tsx", "page.ts", "page.jsx", "page.js",
    "layout.tsx", "layout.ts", "layout.jsx", "layout.js",
})

DEPENDENCY_MANIFESTS = frozenset({
    "package.json", "requirements.txt", "pyproject.toml", "Pipfile",
    "poetry.lock", "Cargo.toml", "go.mod", "Gemfile",
})

FRAMEWORK_CONFIG_FILES = frozenset({
    "next.config.js", "next.config.ts", "next.config.mjs",
    "vite.config.ts", "vite.config.js",
    "tailwind.config.js", "tailwind.config.ts",
    "tsconfig.json", "pytest.ini",
    "jest.config.js", "jest.config.ts", "jest.config.mjs", "jest.config.cjs",
})

ROUTING_FILES = frozenset({"routes.py", "router.py", "urls.py", "api.py"})
SERVICE_HINTS = ("service", "services", "handler", "controller", "router", "routes")
MODEL_HINTS = ("model", "models", "schema", "schemas", "entity", "entities")

TOP_IMPORTANT_FILES = 10


def score_file_usefulness(
    relative_path: str,
    *,
    entry_point_paths: set[str],
    api_endpoint_files: set[str],
    high_import_files: set[str],
    large_files: set[str],
) -> int:
    normalized = relative_path.replace("\\", "/")
    parts = normalized.split("/")
    name = parts[-1].lower()
    depth = len(parts)
    score = 0

    if normalized in entry_point_paths:
        score += 120

    if normalized in api_endpoint_files:
        score += 100

    if normalized in high_import_files:
        score += 85

    if normalized in large_files:
        score += 35

    if name == "readme.md":
        score += 90 if depth == 1 else 40

    if name in ENTRY_POINT_FILENAMES:
        score += 75

    if name in NEXT_APP_FILENAMES and "app" in parts:
        score += 80

    if name in DEPENDENCY_MANIFESTS:
        score += 70

    if name in FRAMEWORK_CONFIG_FILES:
        score += 65

    if name in ROUTING_FILES:
        score += 72

    path_lower = normalized.lower()
    if any(hint in path_lower for hint in SERVICE_HINTS):
        score += 55
    if any(hint in path_lower for hint in MODEL_HINTS):
        score += 50

    if name.startswith("dockerfile") or name.startswith("docker-compose"):
        score += 45

    if name == "conftest.py":
        score += 40

    # Exclude env examples unless nothing more useful was found.
    if name in {".env.example", ".env.sample"}:
        score = 0

    score -= max(0, depth - 4) * 6
    return score


def find_important_files(
    repo_path: Path,
    *,
    entry_point_paths: list[str],
    api_endpoints: list[dict],
    files_with_most_imports: list[dict],
    largest_files: list[dict],
    legacy_scorer,
) -> list[str]:
    """
    Rank files by usefulness using intelligence signals, falling back to
    legacy_scorer (github_service._score_file) for unscored files.
    """

    entry_set = set(entry_point_paths)
    endpoint_files = {ep["file"] for ep in api_endpoints if ep.get("file")}
    high_import = {item["path"] for item in files_with_most_imports[:5]}
    large_set = {item["path"] for item in largest_files[:5]}

    scored: list[tuple[int, str]] = []

    for file_path in iter_repo_files(repo_path, extensions=None, max_depth=5):
        rel = relative_posix_path(repo_path, file_path)
        score = score_file_usefulness(
            rel,
            entry_point_paths=entry_set,
            api_endpoint_files=endpoint_files,
            high_import_files=high_import,
            large_files=large_set,
        )
        if score <= 0:
            score = legacy_scorer(rel)
        if score > 0:
            scored.append((score, rel))

    scored.sort(key=lambda item: (-item[0], item[1].count("/"), item[1].lower()))

    important: list[str] = []
    seen: set[str] = set()
    for _, rel in scored:
        if rel in seen:
            continue
        # Skip env templates — rarely the best starting point for onboarding.
        if rel.split("/")[-1].lower() in {".env.example", ".env.sample"}:
            continue
        seen.add(rel)
        important.append(rel)
        if len(important) >= TOP_IMPORTANT_FILES:
            break

    return important
