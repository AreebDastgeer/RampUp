import shutil
import tempfile
from pathlib import Path
from urllib.parse import urlparse

from git import Repo

IMPORTANT_FILES = [
    "package.json",
    "requirements.txt",
    "pyproject.toml",
    "Dockerfile",
    "docker-compose.yml",
    ".env.example",
]


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


def analyze_repository(github_url: str) -> dict:
    temp_dir = tempfile.mkdtemp()
    try:
        Repo.clone_from(github_url, temp_dir, depth=1)
        repo_path = Path(temp_dir)

        file_count, dir_count = _count_files_and_directories(repo_path)

        readme_path = repo_path / "README.md"
        has_readme = readme_path.is_file()
        readme_preview = ""
        if has_readme:
            readme_preview = readme_path.read_text(encoding="utf-8", errors="replace")[:1000]

        return {
            "name": _extract_repo_name(github_url),
            "files": file_count,
            "directories": dir_count,
            "has_readme": has_readme,
            "readme_preview": readme_preview,
            "important_files": _find_important_files(repo_path),
        }
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
