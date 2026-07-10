import json
import re
import shutil
import tempfile
from pathlib import Path
from urllib.parse import urlparse

from git import Repo

DEV_MODE = True

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

IMPORTANT_FILES = [
    "package.json",
    "requirements.txt",
    "pyproject.toml",
    "Dockerfile",
    "docker-compose.yml",
    ".env.example",
]

ROOT_ENTRY_POINTS = (
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
)

NOTABLE_PYTHON_PACKAGES = {
    "fastapi": "FastAPI",
    "django": "Django",
    "flask": "Flask",
    "uvicorn": "Uvicorn",
    "sqlalchemy": "SQLAlchemy",
    "pydantic": "Pydantic",
    "pytest": "pytest",
}

API_METADATA_KEYS = (
    "name",
    "files",
    "directories",
    "has_readme",
    "readme_preview",
    "important_files",
)


def _extract_repo_name(github_url: str) -> str:
    path = urlparse(github_url.rstrip("/")).path.strip("/")
    name = path.split("/")[-1]
    if name.endswith(".git"):
        name = name[:-4]
    return name


def _should_ignore_path(path: Path) -> bool:
    return any(part in IGNORED_DIR_NAMES for part in path.parts)


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


def _find_important_files(repo_path: Path) -> list[str]:
    found = []
    for filename in IMPORTANT_FILES:
        for item in repo_path.rglob(filename):
            if _should_ignore_path(item):
                continue
            found.append(filename)
            break
    return found


def _get_top_level_folders(repo_path: Path) -> list[str]:
    folders = []
    for item in sorted(repo_path.iterdir(), key=lambda entry: entry.name.lower()):
        if item.is_dir() and item.name not in IGNORED_DIR_NAMES and not _should_ignore_path(item):
            folders.append(item.name)
    return folders


def _build_directory_tree(repo_path: Path, max_depth: int) -> str:
    lines = []

    def walk(path: Path, depth: int) -> None:
        if depth > max_depth:
            return
        for entry in sorted(path.iterdir(), key=lambda item: item.name.lower()):
            if not entry.is_dir() or entry.name in IGNORED_DIR_NAMES or _should_ignore_path(entry):
                continue
            lines.append(f"{'  ' * (depth - 1)}{entry.name}/")
            walk(entry, depth + 1)

    walk(repo_path, 1)
    return "\n".join(lines)


def _find_root_entry_points(repo_path: Path) -> list[str]:
    return sorted(
        name for name in ROOT_ENTRY_POINTS if (repo_path / name).is_file()
    )


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

    if "next" in dep_names:
        technologies.append("Next.js")
    if "react" in dep_names:
        technologies.append("React")
    if "vue" in dep_names:
        technologies.append("Vue")
    if "svelte" in dep_names or "@sveltejs/kit" in dep_names:
        technologies.append("Svelte")
    if "express" in dep_names:
        technologies.append("Express")
    if "tailwindcss" in dep_names or "@tailwindcss/postcss" in dep_names:
        technologies.append("Tailwind CSS")

    config_root = path.parent
    if (config_root / "tsconfig.json").is_file() or "typescript" in dep_names:
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


def _detect_tech_stack(repo_path: Path) -> list[str]:
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

    if _iter_config_paths(repo_path, ("Cargo.toml",)):
        add(["Rust"])

    if _iter_config_paths(repo_path, ("go.mod",)):
        add(["Go"])

    if _iter_config_paths(repo_path, ("Dockerfile",)):
        add(["Docker"])

    if _iter_config_paths(repo_path, ("docker-compose.yml", "docker-compose.yaml")):
        add(["Docker Compose"])

    return detected


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
    if has_readme:
        readme_preview = readme_path.read_text(encoding="utf-8", errors="replace")[:1000]

    tree_depth = 2 if DEV_MODE else 5

    return {
        "name": _extract_repo_name(github_url),
        "files": file_count,
        "directories": dir_count,
        "has_readme": has_readme,
        "readme_preview": readme_preview,
        "important_files": _find_important_files(repo_path),
        "top_level_folders": _get_top_level_folders(repo_path),
        "directory_tree": _build_directory_tree(repo_path, tree_depth),
        "github_url": github_url,
        "tech_stack": _detect_tech_stack(repo_path),
        "entry_points": _find_root_entry_points(repo_path),
    }


def build_repository_summary(metadata: dict) -> str:
    max_readme_chars = 500 if DEV_MODE else 500
    tree_depth = 2 if DEV_MODE else 5

    name = metadata["name"]
    github_url = metadata.get("github_url", "")
    files = metadata["files"]
    directories = metadata["directories"]
    has_readme = metadata["has_readme"]
    important_files = metadata.get("important_files", [])
    top_level_folders = metadata.get("top_level_folders", [])
    tech_stack = metadata.get("tech_stack", [])
    entry_points = metadata.get("entry_points", [])

    readme_excerpt = ""
    if has_readme and metadata.get("readme_preview"):
        readme_excerpt = _clean_readme_text(metadata["readme_preview"])[:max_readme_chars]

    directory_tree = metadata.get("directory_tree", "")
    if not directory_tree and top_level_folders:
        directory_tree = "\n".join(f"{folder}/" for folder in top_level_folders)

    sections = [
        f"Repository: {name}",
        f"URL: {github_url}",
        f"Files: {files} | Directories: {directories}",
        f"README: {'yes' if has_readme else 'no'}",
    ]

    if tech_stack:
        sections.append(f"Detected Tech Stack: {', '.join(tech_stack)}")

    if entry_points:
        sections.append(f"Root entry points: {', '.join(entry_points)}")

    if important_files:
        sections.append(f"Important files: {', '.join(important_files)}")

    if top_level_folders:
        sections.append(f"Top-level folders: {', '.join(top_level_folders)}")

    if directory_tree:
        sections.append(f"Directory tree (depth {tree_depth}):\n{directory_tree}")

    if readme_excerpt:
        sections.append(f"README excerpt:\n{readme_excerpt}")

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
