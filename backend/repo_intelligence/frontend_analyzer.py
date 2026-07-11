"""
Minimal frontend analyzer — detects common frontend frameworks and entry surfaces.

This stays intentionally light-weight: package.json signals and a small set of
conventional app entry files are enough for frontend onboarding without adding
heavy parsing or extra dependencies.
"""

import json
from pathlib import Path

from repo_intelligence.utils import iter_repo_files, read_text_safe

FRONTEND_PACKAGE_LABELS = {
    "next": "Next.js",
    "react": "React",
    "react-dom": "React DOM",
    "vue": "Vue",
    "svelte": "Svelte",
    "astro": "Astro",
    "remix": "Remix",
    "vite": "Vite",
    "tailwindcss": "Tailwind CSS",
    "@tailwindcss/postcss": "Tailwind CSS",
    "typescript": "TypeScript",
}

FRONTEND_ENTRY_CANDIDATES = (
    ("app/page.tsx", "Next.js App Router page"),
    ("app/page.ts", "Next.js App Router page"),
    ("app/page.jsx", "Next.js App Router page"),
    ("app/page.js", "Next.js App Router page"),
    ("src/app/page.tsx", "Next.js App Router page"),
    ("src/app/page.ts", "Next.js App Router page"),
    ("pages/index.tsx", "classic page entry"),
    ("pages/index.ts", "classic page entry"),
    ("pages/index.jsx", "classic page entry"),
    ("pages/index.js", "classic page entry"),
    ("src/pages/index.tsx", "classic page entry"),
    ("src/pages/index.ts", "classic page entry"),
    ("src/pages/index.jsx", "classic page entry"),
    ("src/pages/index.js", "classic page entry"),
    ("src/main.tsx", "SPA bootstrap"),
    ("src/main.ts", "SPA bootstrap"),
    ("src/main.jsx", "SPA bootstrap"),
    ("src/main.js", "SPA bootstrap"),
    ("main.tsx", "SPA bootstrap"),
    ("main.ts", "SPA bootstrap"),
    ("main.jsx", "SPA bootstrap"),
    ("main.js", "SPA bootstrap"),
    ("src/index.tsx", "SPA bootstrap"),
    ("src/index.ts", "SPA bootstrap"),
    ("src/index.jsx", "SPA bootstrap"),
    ("src/index.js", "SPA bootstrap"),
    ("index.tsx", "SPA bootstrap"),
    ("index.ts", "SPA bootstrap"),
    ("index.jsx", "SPA bootstrap"),
    ("index.js", "SPA bootstrap"),
    ("src/App.tsx", "root component"),
    ("src/App.ts", "root component"),
    ("src/App.jsx", "root component"),
    ("src/App.js", "root component"),
    ("App.tsx", "root component"),
    ("App.ts", "root component"),
    ("App.jsx", "root component"),
    ("App.js", "root component"),
    ("index.html", "frontend shell"),
)


def _unique_add(items: list[str], value: str) -> None:
    if value not in items:
        items.append(value)


def _package_json_paths(repo_path: Path) -> list[Path]:
    paths: list[Path] = []
    for file_path in iter_repo_files(repo_path, extensions=frozenset({".json"}), max_depth=4):
        if file_path.name == "package.json":
            paths.append(file_path)
        if len(paths) >= 3:
            break
    return paths


def _detect_from_package_json(path: Path) -> list[str]:
    labels = ["Frontend"]
    try:
        data = json.loads(read_text_safe(path))
    except json.JSONDecodeError:
        return labels

    deps = {
        **data.get("dependencies", {}),
        **data.get("devDependencies", {}),
    }
    dep_names = {name.lower() for name in deps}

    for package, label in FRONTEND_PACKAGE_LABELS.items():
        if package in dep_names:
            _unique_add(labels, label)

    return labels


def analyze_frontend_repository(repo_path: Path) -> dict:
    technologies: list[str] = []
    entry_details: list[dict] = []
    seen_entries: set[str] = set()
    package_json_paths = _package_json_paths(repo_path)

    for package_json in package_json_paths:
        for label in _detect_from_package_json(package_json):
            _unique_add(technologies, label)

    for relative_path, reason in FRONTEND_ENTRY_CANDIDATES:
        if (repo_path / relative_path).is_file() and relative_path not in seen_entries:
            seen_entries.add(relative_path)
            entry_details.append({
                "path": relative_path,
                "reason": reason,
                "source": "frontend_convention",
            })

    if not technologies and entry_details:
        technologies.append("Frontend")

    entry_points = [entry["path"] for entry in entry_details]

    return {
        "files_analyzed": len(package_json_paths),
        "technologies": technologies,
        "entry_points": entry_points,
        "entry_point_details": entry_details,
    }