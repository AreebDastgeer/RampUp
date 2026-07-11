import json
import re
import shutil
import tempfile
from pathlib import Path
from urllib.parse import urlparse

from git import Repo

from repo_intelligence import analyze_repository_intelligence

DEV_MODE = True
MAX_SCAN_DEPTH = 4
TOP_IMPORTANT_FILES = 5
MAX_README_EXCERPT_CHARS = 500

IGNORED_DIR_NAMES = frozenset({
    ".git",
    "__pycache__",
    "node_modules",
    ".next",
    "venv",
    ".venv",
    "build",
    "dist",
    ".idea",
    ".vscode",
})

ENTRY_POINT_FILENAMES = frozenset({
    "main.py",
    "app.py",
    "server.py",
    "manage.py",
    "wsgi.py",
    "asgi.py",
    "run.py",
    "server.js",
    "index.js",
    "app.js",
    "main.js",
    "index.ts",
    "main.ts",
    "app.ts",
    "server.ts",
    "main.go",
    "main.rs",
})

NEXT_APP_FILENAMES = frozenset({
    "page.tsx",
    "page.ts",
    "page.jsx",
    "page.js",
    "layout.tsx",
    "layout.ts",
    "layout.jsx",
    "layout.js",
})

DEPENDENCY_MANIFESTS = frozenset({
    "package.json",
    "requirements.txt",
    "pyproject.toml",
    "Pipfile",
    "poetry.lock",
    "Cargo.toml",
    "go.mod",
    "Gemfile",
})

FRAMEWORK_CONFIG_FILES = frozenset({
    "next.config.js",
    "next.config.ts",
    "next.config.mjs",
    "vite.config.ts",
    "vite.config.js",
    "tailwind.config.js",
    "tailwind.config.ts",
    "tsconfig.json",
    "pytest.ini",
    "jest.config.js",
    "jest.config.ts",
    "jest.config.mjs",
    "jest.config.cjs",
})

ROUTING_FILES = frozenset({
    "routes.py",
    "router.py",
    "urls.py",
    "api.py",
})

NOTABLE_PYTHON_PACKAGES = {
    "fastapi": "FastAPI",
    "django": "Django",
    "flask": "Flask",
    "uvicorn": "Uvicorn",
    "pytest": "pytest",
}

NOTABLE_NODE_PACKAGES = {
    "next": "Next.js",
    "react": "React",
    "vue": "Vue",
    "express": "Express",
    "jest": "Jest",
    "tailwindcss": "Tailwind CSS",
    "@tailwindcss/postcss": "Tailwind CSS",
    "typescript": "TypeScript",
}

KNOWN_ENTRY_POINT_CANDIDATES = (
    "main.py",
    "app.py",
    "server.py",
    "manage.py",
    "wsgi.py",
    "asgi.py",
    "run.py",
    "server.js",
    "index.js",
    "app.js",
    "main.js",
    "index.ts",
    "main.ts",
    "app.ts",
    "server.ts",
    "backend/main.py",
    "backend/app.py",
    "backend/server.py",
    "api/main.py",
    "src/main.py",
    "src/index.ts",
    "src/main.ts",
    "src/server.js",
    "frontend/app/page.tsx",
    "frontend/app/layout.tsx",
    "frontend/app/page.ts",
    "frontend/app/layout.ts",
    "app/page.tsx",
    "app/layout.tsx",
    "app/page.ts",
    "app/layout.ts",
)

API_METADATA_KEYS = (
    "name",
    "files",
    "directories",
    "has_readme",
    "readme_preview",
    "important_files",
    "technologies",
    "entry_points",
    "entry_point_details",
    "imports",
    "api_endpoints",
    "dependency_map",
    "repository_health",
    "code_analysis",
    "project_structure",
    "top_level_folders",
    "project_purpose",
)


def _extract_repo_name(github_url: str) -> str:
    path = urlparse(github_url.rstrip("/")).path.strip("/")
    name = path.split("/")[-1]
    if name.endswith(".git"):
        name = name[:-4]
    return name


def _should_ignore_path(path: Path) -> bool:
    return any(part in IGNORED_DIR_NAMES for part in path.parts)


def _relative_posix_path(repo_path: Path, file_path: Path) -> str:
    return file_path.relative_to(repo_path).as_posix()


def _count_files_and_directories(repo_path: Path) -> tuple[int, int]:
    file_count = 0
    dir_count = 0
    for item in repo_path.rglob("*"):
        if _should_ignore_path(item):
            continue
        if item.is_file():
            file_count += 1
        elif item.is_dir():
            dir_count += 1
    return file_count, dir_count


def _iter_repo_files(repo_path: Path, max_depth: int = MAX_SCAN_DEPTH):
    def walk(current: Path, depth: int):
        if depth > max_depth:
            return
        try:
            entries = sorted(current.iterdir(), key=lambda entry: entry.name.lower())
        except OSError:
            return
        for entry in entries:
            if _should_ignore_path(entry):
                continue
            if entry.is_file():
                yield entry
            elif entry.is_dir():
                yield from walk(entry, depth + 1)

    yield from walk(repo_path, 0)


def _score_file(relative_path: str) -> int:
    normalized = relative_path.replace("\\", "/")
    parts = normalized.split("/")
    name = parts[-1].lower()
    depth = len(parts)
    score = 0

    if name == "readme.md":
        score += 95 if depth == 1 else 45

    if name in ENTRY_POINT_FILENAMES:
        score += 90
        if depth == 2 and parts[0] in {"backend", "frontend", "src", "api", "server", "app"}:
            score += 20
        elif depth == 1:
            score += 10

    if name in NEXT_APP_FILENAMES and "app" in parts:
        score += 88 if name.startswith("page") else 82

    if name in DEPENDENCY_MANIFESTS:
        score += 78 if depth == 1 else 76

    if name in FRAMEWORK_CONFIG_FILES:
        score += 68

    if name in ROUTING_FILES:
        score += 62

    if name.startswith("dockerfile") or name.startswith("docker-compose"):
        score += 55

    if name in {"package-lock.json", "yarn.lock", "pnpm-lock.yaml"}:
        score += 40

    if name == "conftest.py":
        score += 45

    if name == ".env.example":
        score = 0

    score -= max(0, depth - 3) * 8
    return score


def _find_important_files(repo_path: Path) -> list[str]:
    scored: list[tuple[int, str]] = []

    for file_path in _iter_repo_files(repo_path):
        relative_path = _relative_posix_path(repo_path, file_path)
        score = _score_file(relative_path)
        if score <= 0:
            continue
        scored.append((score, relative_path))

    scored.sort(key=lambda item: (-item[0], item[1].count("/"), item[1].lower()))

    important: list[str] = []
    seen: set[str] = set()
    for _, relative_path in scored:
        if relative_path in seen:
            continue
        seen.add(relative_path)
        important.append(relative_path)
        if len(important) >= TOP_IMPORTANT_FILES:
            break

    return important


def _get_top_level_folders(repo_path: Path) -> list[str]:
    folders = []
    for item in sorted(repo_path.iterdir(), key=lambda entry: entry.name.lower()):
        if item.is_dir() and item.name not in IGNORED_DIR_NAMES and not _should_ignore_path(item):
            folders.append(item.name)
    return folders


def _find_entry_points(repo_path: Path) -> list[str]:
    found: list[str] = []
    seen: set[str] = set()

    def add(relative_path: str) -> None:
        if relative_path not in seen:
            seen.add(relative_path)
            found.append(relative_path)

    for candidate in KNOWN_ENTRY_POINT_CANDIDATES:
        if (repo_path / candidate).is_file():
            add(candidate)

    for file_path in _iter_repo_files(repo_path, max_depth=3):
        relative_path = _relative_posix_path(repo_path, file_path)
        parts = relative_path.split("/")
        name = parts[-1].lower()

        if name in ENTRY_POINT_FILENAMES and len(parts) <= 3:
            add(relative_path)
            continue

        if name in NEXT_APP_FILENAMES and "app" in parts and len(parts) <= 4:
            add(relative_path)

    return sorted(found, key=lambda path: (path.count("/"), path.lower()))


def _iter_config_paths(repo_path: Path, filenames: tuple[str, ...]) -> list[Path]:
    paths: list[Path] = []
    for filename in filenames:
        root_path = repo_path / filename
        if root_path.is_file():
            paths.append(root_path)
        for child in sorted(repo_path.iterdir(), key=lambda entry: entry.name.lower()):
            if not child.is_dir() or _should_ignore_path(child):
                continue
            nested_path = child / filename
            if nested_path.is_file():
                paths.append(nested_path)
    return paths


def _sniff_python_framework(path: Path) -> list[str]:
    try:
        content = path.read_text(encoding="utf-8", errors="replace").lower()
    except OSError:
        return []

    detected: list[str] = []
    if "from fastapi" in content or "import fastapi" in content:
        detected.append("FastAPI")
    if "from flask" in content or "import flask" in content:
        detected.append("Flask")
    if "django" in content and ("django.conf" in content or "django.core" in content):
        detected.append("Django")
    return detected


def _detect_from_package_json(path: Path) -> list[str]:
    technologies = ["Node.js"]
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except (json.JSONDecodeError, OSError):
        return technologies

    deps = {
        **data.get("dependencies", {}),
        **data.get("devDependencies", {}),
    }
    dep_names = {name.lower() for name in deps}

    for package, label in NOTABLE_NODE_PACKAGES.items():
        if package in dep_names:
            technologies.append(label)

    config_root = path.parent
    if (config_root / "tsconfig.json").is_file() and "TypeScript" not in technologies:
        technologies.append("TypeScript")

    return technologies


def _detect_from_requirements(path: Path) -> list[str]:
    technologies = ["Python"]
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return technologies

    for line in lines:
        normalized = line.strip().lower().split("[", 1)[0]
        normalized = re.split(r"[<>=!~;]", normalized, maxsplit=1)[0].strip()
        if normalized in NOTABLE_PYTHON_PACKAGES:
            technologies.append(NOTABLE_PYTHON_PACKAGES[normalized])

    return technologies


def _detect_from_pyproject(path: Path) -> list[str]:
    technologies = ["Python"]
    try:
        content = path.read_text(encoding="utf-8", errors="replace").lower()
    except OSError:
        return technologies

    for package, label in NOTABLE_PYTHON_PACKAGES.items():
        if package in content:
            technologies.append(label)

    return technologies


def _detect_tech_stack(repo_path: Path, entry_points: list[str]) -> list[str]:
    detected: list[str] = []

    def add(items: list[str]) -> None:
        for item in items:
            if item not in detected:
                detected.append(item)

    for path in _iter_config_paths(repo_path, ("package.json",)):
        add(_detect_from_package_json(path))

    for path in _iter_config_paths(repo_path, ("requirements.txt",)):
        add(_detect_from_requirements(path))

    for path in _iter_config_paths(repo_path, ("pyproject.toml",)):
        add(_detect_from_pyproject(path))

    if _iter_config_paths(repo_path, ("Dockerfile",)):
        add(["Docker"])

    if _iter_config_paths(repo_path, ("docker-compose.yml", "docker-compose.yaml")):
        add(["Docker Compose"])

    if _iter_config_paths(repo_path, ("pytest.ini",)):
        add(["pytest"])

    if _iter_config_paths(
        repo_path,
        ("jest.config.js", "jest.config.ts", "jest.config.mjs", "jest.config.cjs"),
    ):
        add(["Jest"])

    for filename in ("conftest.py",):
        if any(
            not _should_ignore_path(path)
            for path in _iter_config_paths(repo_path, (filename,))
        ):
            add(["pytest"])
            break

    for entry_point in entry_points[:3]:
        path = repo_path / entry_point
        if path.suffix == ".py":
            add(_sniff_python_framework(path))

    return detected


def _extract_project_purpose(readme_text: str) -> str:
    cleaned = _clean_readme_text(readme_text)
    if not cleaned:
        return ""

    lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
    if not lines:
        return ""

    purpose_lines: list[str] = []
    for line in lines:
        if line.startswith("#"):
            heading = re.sub(r"^#+\s*", "", line).strip()
            if heading and heading.lower() not in {"table of contents", "contents", "license"}:
                purpose_lines.append(heading)
            continue
        if purpose_lines:
            purpose_lines.append(line)
            break
        purpose_lines.append(line)
        break

    purpose = " ".join(purpose_lines)
    return purpose[:220].strip()


def _build_compact_structure(
    repo_path: Path,
    important_files: list[str],
    entry_points: list[str],
    top_level_folders: list[str],
) -> str:
    focus_paths = set(important_files) | set(entry_points)
    for relative_path in list(focus_paths):
        parts = relative_path.split("/")
        for index in range(1, len(parts)):
            focus_paths.add("/".join(parts[:index]))

    lines: list[str] = []

    def append_tree(relative_dir: str, depth: int, max_depth: int) -> None:
        if depth > max_depth:
            return

        dir_path = repo_path / relative_dir if relative_dir else repo_path
        if relative_dir:
            lines.append(f"{'  ' * depth}{relative_dir.split('/')[-1]}/")

        child_depth = depth + 1 if relative_dir else depth
        child_max_depth = max_depth if relative_dir else max_depth

        try:
            entries = sorted(dir_path.iterdir(), key=lambda entry: entry.name.lower())
        except OSError:
            return

        child_dirs: list[str] = []
        child_files: list[str] = []

        for entry in entries:
            if _should_ignore_path(entry):
                continue
            rel = _relative_posix_path(repo_path, entry)
            if entry.is_dir():
                if rel in focus_paths or entry.name in top_level_folders:
                    child_dirs.append(rel)
            elif entry.is_file() and rel in focus_paths:
                child_files.append(entry.name)

        for directory in child_dirs:
            append_tree(directory, child_depth, child_max_depth)

        indent = "  " * (child_depth)
        for filename in child_files:
            lines.append(f"{indent}{filename}")

    if top_level_folders:
        for folder in top_level_folders:
            if folder in focus_paths or any(
                path.startswith(f"{folder}/") for path in focus_paths
            ):
                append_tree(folder, 0, 2)
    elif focus_paths:
        for relative_path in sorted(focus_paths):
            if "/" not in relative_path:
                lines.append(relative_path)

    deduped: list[str] = []
    seen: set[str] = set()
    for line in lines:
        if line not in seen:
            seen.add(line)
            deduped.append(line)

    return "\n".join(deduped)


def _clean_readme_text(text: str) -> str:
    text = re.sub(r"\[!\[[^\]]*\]\([^)]*\)\]\([^)]*\)", "", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\[\]\([^)]*\)", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    lines = [line.strip() for line in text.splitlines()]
    return "\n".join(line for line in lines if line).strip()


def _extract_metadata(repo_path: Path, github_url: str) -> dict:
    file_count, dir_count = _count_files_and_directories(repo_path)

    readme_path = repo_path / "README.md"
    has_readme = readme_path.is_file()
    readme_preview = ""
    readme_text = ""
    if has_readme:
        readme_text = readme_path.read_text(encoding="utf-8", errors="replace")
        readme_preview = readme_text[:1000]

    top_level_folders = _get_top_level_folders(repo_path)

    # Filename heuristics are kept as a fallback layer for entry-point detection.
    filename_entry_points = _find_entry_points(repo_path)
    tech_stack = _detect_tech_stack(repo_path, filename_entry_points)
    project_purpose = _extract_project_purpose(readme_text) if has_readme else ""

    # Run real code analysis before the LLM sees the repository.
    intelligence = analyze_repository_intelligence(
        repo_path,
        existing_tech_stack=tech_stack,
        filename_entry_points=filename_entry_points,
        legacy_file_scorer=_score_file,
    )

    entry_points = intelligence["entry_points"]
    important_files = intelligence["important_files"]
    technologies = intelligence["technologies"]

    compact_structure = _build_compact_structure(
        repo_path,
        important_files,
        entry_points,
        top_level_folders,
    )

    return {
        "name": _extract_repo_name(github_url),
        "files": file_count,
        "directories": dir_count,
        "has_readme": has_readme,
        "readme_preview": readme_preview,
        "important_files": important_files,
        "top_level_folders": top_level_folders,
        "github_url": github_url,
        "tech_stack": tech_stack,
        "technologies": technologies,
        "entry_points": entry_points,
        "entry_point_details": intelligence["entry_point_details"],
        "imports": intelligence["imports"],
        "api_endpoints": intelligence["api_endpoints"],
        "dependency_map": intelligence["dependency_map"],
        "repository_health": intelligence["repository_health"],
        "code_analysis": intelligence["code_analysis"],
        "project_purpose": project_purpose,
        "compact_structure": compact_structure,
        "project_structure": compact_structure,
    }


def _format_entry_point_details(details: list[dict]) -> str:
    lines = []
    for entry in details:
        path = entry.get("path", "")
        reason = entry.get("reason", "")
        source = entry.get("source", "")
        if reason:
            lines.append(f"- {path} ({reason}; detected via {source})")
        else:
            lines.append(f"- {path}")
    return "\n".join(lines)


def _format_api_endpoints(endpoints: list[dict]) -> str:
    lines = []
    for ep in endpoints[:30]:
        method = ep.get("method", "?")
        path = ep.get("path", "?")
        file = ep.get("file", "?")
        line = ep.get("line", "?")
        framework = ep.get("framework", "")
        suffix = f" [{framework}]" if framework else ""
        lines.append(f"- {method} {path} — {file}:{line}{suffix}")
    if len(endpoints) > 30:
        lines.append(f"- ... and {len(endpoints) - 30} more endpoints")
    return "\n".join(lines)


def _format_dependency_map(edges: list[dict]) -> str:
    grouped: dict[str, list[str]] = {}
    for edge in edges[:40]:
        source = edge.get("source", "")
        target = edge.get("target", "")
        grouped.setdefault(source, []).append(target)

    lines = []
    for source, targets in sorted(grouped.items()):
        lines.append(f"- {source} imports: {', '.join(targets)}")
    if len(edges) > 40:
        lines.append(f"- ... and {len(edges) - 40} more dependency edges")
    return "\n".join(lines)


def _format_repository_health(health: dict) -> str:
    flags = [
        ("README", health.get("readme_present")),
        ("License", health.get("license_present")),
        ("Tests", health.get("tests_detected")),
        ("Docker", health.get("docker_detected")),
        ("CI workflow", health.get("ci_workflow_detected")),
        ("GitHub Actions", health.get("github_actions_detected")),
        ("Env example", health.get("env_example_detected")),
    ]
    lines = [f"- {label}: {'yes' if value else 'no'}" for label, value in flags]
    managers = health.get("package_managers", [])
    if managers:
        lines.append(f"- Package managers: {', '.join(managers)}")
    return "\n".join(lines)


def build_repository_summary(metadata: dict) -> str:
    name = metadata["name"]
    github_url = metadata.get("github_url", "")
    has_readme = metadata["has_readme"]
    important_files = metadata.get("important_files", [])
    technologies = metadata.get("technologies") or metadata.get("tech_stack", [])
    entry_points = metadata.get("entry_points", [])
    entry_point_details = metadata.get("entry_point_details", [])
    project_purpose = metadata.get("project_purpose", "")
    compact_structure = metadata.get("project_structure") or metadata.get("compact_structure", "")
    api_endpoints = metadata.get("api_endpoints", [])
    dependency_map = metadata.get("dependency_map", [])
    repository_health = metadata.get("repository_health", {})
    code_analysis = metadata.get("code_analysis", {})
    imports_meta = metadata.get("imports", {})

    readme_excerpt = ""
    if has_readme and metadata.get("readme_preview"):
        readme_excerpt = _clean_readme_text(metadata["readme_preview"])[:MAX_README_EXCERPT_CHARS]

    sections = [
        "===== FACTUAL REPOSITORY INTELLIGENCE (verified by static analysis) =====",
        f"Repository: {name}",
        f"URL: {github_url}",
    ]

    if project_purpose:
        sections.append(f"Project purpose (from README): {project_purpose}")

    if technologies:
        sections.append(f"Technologies (detected): {', '.join(technologies)}")

    if repository_health:
        sections.append("Repository health:\n" + _format_repository_health(repository_health))

    if important_files:
        sections.append("Important files (usefulness-ranked):\n" + "\n".join(f"- {path}" for path in important_files))

    if entry_point_details:
        sections.append("Entry points (code-detected):\n" + _format_entry_point_details(entry_point_details))
    elif entry_points:
        sections.append("Entry points:\n" + "\n".join(f"- {path}" for path in entry_points))

    if api_endpoints:
        sections.append("API endpoints (parsed from source):\n" + _format_api_endpoints(api_endpoints))

    frequent_packages = imports_meta.get("frequent_packages", [])
    if frequent_packages:
        pkg_summary = ", ".join(
            f"{item['package']} ({item['count']} files)" for item in frequent_packages[:12]
        )
        sections.append(f"Frequently imported packages: {pkg_summary}")

    if dependency_map:
        sections.append("Dependency map (internal imports):\n" + _format_dependency_map(dependency_map))

    largest_files = code_analysis.get("largest_files", [])
    if largest_files:
        lines = [f"- {item['path']} ({item.get('lines', '?')} lines)" for item in largest_files[:8]]
        sections.append("Largest source files:\n" + "\n".join(lines))

    heavy_import_files = code_analysis.get("files_with_most_imports", [])
    if heavy_import_files:
        lines = [
            f"- {item['path']} ({item.get('import_count', '?')} imports)"
            for item in heavy_import_files[:8]
        ]
        sections.append("Files with most imports:\n" + "\n".join(lines))

    classes = code_analysis.get("classes", [])
    if classes:
        lines = [f"- {c['name']} in {c['file']}:{c['line']}" for c in classes[:15]]
        sections.append("Detected classes:\n" + "\n".join(lines))

    functions = code_analysis.get("functions", [])
    if functions:
        lines = [f"- {f['name']} in {f['file']}:{f['line']}" for f in functions[:15]]
        sections.append("Detected top-level functions:\n" + "\n".join(lines))

    if compact_structure:
        sections.append(f"Project structure:\n{compact_structure}")

    if readme_excerpt:
        sections.append(f"README excerpt:\n{readme_excerpt}")

    sections.append(
        "===== END FACTUAL REPOSITORY INTELLIGENCE =====\n"
        "Use ONLY the facts above. Explain WHY each detected file, endpoint, "
        "dependency, or technology matters. Never invent files or frameworks."
    )

    return "\n".join(sections)


def analyze_repository_complete(github_url: str) -> tuple[dict, str]:
    temp_dir = tempfile.mkdtemp()
    try:
        Repo.clone_from(github_url, temp_dir, depth=1)
        repo_path = Path(temp_dir)
        metadata = _extract_metadata(repo_path, github_url)
        api_data = {key: metadata[key] for key in API_METADATA_KEYS}
        summary = build_repository_summary(metadata)
        return api_data, summary
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def analyze_repository(github_url: str) -> dict:
    repository, _ = analyze_repository_complete(github_url)
    return repository
