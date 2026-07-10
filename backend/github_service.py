import re
import shutil
import tempfile
from pathlib import Path
from urllib.parse import urlparse

from git import Repo

DEV_MODE = True

IMPORTANT_FILES = [
    "package.json",
    "requirements.txt",
    "pyproject.toml",
    "Dockerfile",
    "docker-compose.yml",
    ".env.example",
]

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


def _is_git_path(path: Path) -> bool:
    return ".git" in path.parts


def _count_files_and_directories(repo_path: Path) -> tuple[int, int]:
    file_count = 0
    dir_count = 0
    for item in repo_path.rglob("*"):
        if _is_git_path(item):
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
            if _is_git_path(item):
                continue
            found.append(filename)
            break
    return found


def _get_top_level_folders(repo_path: Path) -> list[str]:
    folders = []
    for item in sorted(repo_path.iterdir(), key=lambda entry: entry.name.lower()):
        if item.is_dir() and item.name != ".git" and not _is_git_path(item):
            folders.append(item.name)
    return folders


def _build_directory_tree(repo_path: Path, max_depth: int) -> str:
    lines = []

    def walk(path: Path, depth: int) -> None:
        if depth > max_depth:
            return
        for entry in sorted(path.iterdir(), key=lambda item: item.name.lower()):
            if not entry.is_dir() or entry.name == ".git" or _is_git_path(entry):
                continue
            lines.append(f"{'  ' * (depth - 1)}{entry.name}/")
            walk(entry, depth + 1)

    walk(repo_path, 1)
    return "\n".join(lines)


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
