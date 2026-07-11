"""
Shared filesystem utilities for repository intelligence analyzers.

Keeps path-walking logic separate from github_service.py so analyzers stay
modular and testable without circular imports.
"""

from pathlib import Path

# Mirror github_service ignore list so scans stay consistent across the pipeline.
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

PYTHON_EXTENSIONS = frozenset({".py"})
JS_EXTENSIONS = frozenset({".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"})

MAX_SCAN_DEPTH = 6
MAX_PYTHON_FILES = 200
MAX_JS_FILES = 150


def should_ignore_path(path: Path) -> bool:
    return any(part in IGNORED_DIR_NAMES for part in path.parts)


def relative_posix_path(repo_path: Path, file_path: Path) -> str:
    return file_path.relative_to(repo_path).as_posix()


def iter_repo_files(
    repo_path: Path,
    extensions: frozenset[str] | None = None,
    max_depth: int = MAX_SCAN_DEPTH,
):
    """Yield repository files up to max_depth, optionally filtered by extension."""

    def walk(current: Path, depth: int):
        if depth > max_depth:
            return
        try:
            entries = sorted(current.iterdir(), key=lambda entry: entry.name.lower())
        except OSError:
            return
        for entry in entries:
            if should_ignore_path(entry):
                continue
            if entry.is_file():
                if extensions is None or entry.suffix.lower() in extensions:
                    yield entry
            elif entry.is_dir():
                yield from walk(entry, depth + 1)

    yield from walk(repo_path, 0)


def read_text_safe(path: Path, max_bytes: int = 512_000) -> str:
    try:
        raw = path.read_bytes()
        if len(raw) > max_bytes:
            raw = raw[:max_bytes]
        return raw.decode("utf-8", errors="replace")
    except OSError:
        return ""
