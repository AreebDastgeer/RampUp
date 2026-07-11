"""
JavaScript/TypeScript analyzer — regex-based import and route extraction.

Full JS parsing would require an external parser; regex is sufficient for
collecting import statements and common Express/Fastify route patterns
without adding dependencies.
"""

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from repo_intelligence.utils import (
    JS_EXTENSIONS,
    MAX_JS_FILES,
    iter_repo_files,
    read_text_safe,
    relative_posix_path,
)

# Match ES module and CommonJS import patterns.
IMPORT_PATTERNS = [
    re.compile(r"""import\s+(?:[\w*{}\s,]+\s+from\s+)?['"]([^'"]+)['"]"""),
    re.compile(r"""require\s*\(\s*['"]([^'"]+)['"]\s*\)"""),
    re.compile(r"""import\s*\(\s*['"]([^'"]+)['"]\s*\)"""),
]

# Express / Fastify style route registrations.
ROUTE_PATTERNS = [
    re.compile(
        r"""(?:app|router|server|api|expressRouter)\s*\.\s*(get|post|put|delete|patch|all)\s*\(\s*['"`]([^'"`]+)['"`]""",
        re.IGNORECASE,
    ),
    re.compile(
        r"""\.route\s*\(\s*['"`]([^'"`]+)['"`]\s*\)\s*\.\s*(get|post|put|delete|patch)""",
        re.IGNORECASE,
    ),
]

ENTRY_POINT_PATTERNS = [
    (re.compile(r"""\.listen\s*\(\s*[\w\d]"""), "server.listen()"),
    (re.compile(r"""createServer\s*\("""), "http.createServer()"),
    (re.compile(r"""export\s+default\s+function\s+handler"""), "serverless handler"),
    (re.compile(r"""module\.exports\s*=\s*app"""), "express app export"),
]


@dataclass
class JsFileAnalysis:
    path: str
    line_count: int
    byte_size: int
    internal_imports: list[str] = field(default_factory=list)
    external_imports: list[str] = field(default_factory=list)


@dataclass
class JsAnalysisResult:
    files_analyzed: int
    file_analyses: dict[str, JsFileAnalysis]
    api_endpoints: list[dict]
    dependency_edges: list[dict]
    detected_entry_points: list[dict]
    frequent_external_packages: list[dict]
    largest_files: list[dict]
    files_with_most_imports: list[dict]


def _is_internal_import(import_path: str) -> bool:
    return import_path.startswith(".") or import_path.startswith("/")


def _normalize_internal_import(import_path: str, source_dir: str) -> str:
    """Resolve relative import to a repo-relative path string."""

    if import_path.startswith("/"):
        base = import_path.lstrip("/")
    else:
        parts = source_dir.split("/") if source_dir else []
        for segment in import_path.split("/"):
            if segment == ".":
                continue
            if segment == "..":
                if parts:
                    parts.pop()
            else:
                parts.append(segment)
        base = "/".join(parts)

    if not base.endswith((".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs")):
        for ext in (".ts", ".tsx", ".js", ".jsx"):
            candidate = base + ext
            if candidate:
                return candidate
        return base + ".ts"

    return base


def _extract_imports(content: str, rel_path: str) -> tuple[list[str], list[str]]:
    internal: list[str] = []
    external: list[str] = []
    seen_int: set[str] = set()
    seen_ext: set[str] = set()

    source_dir = "/".join(rel_path.split("/")[:-1])

    for pattern in IMPORT_PATTERNS:
        for match in pattern.finditer(content):
            raw = match.group(1).strip()
            if not raw or raw.startswith("node:"):
                continue

            if _is_internal_import(raw):
                normalized = _normalize_internal_import(raw, source_dir)
                if normalized not in seen_int:
                    seen_int.add(normalized)
                    internal.append(normalized)
            else:
                package = raw.split("/")[0]
                if raw.startswith("@"):
                    package = "/".join(raw.split("/")[:2])
                if package not in seen_ext:
                    seen_ext.add(package)
                    external.append(package)

    return sorted(internal), sorted(external)


def _extract_routes(content: str, rel_path: str) -> list[dict]:
    endpoints: list[dict] = []
    seen: set[tuple[str, str]] = set()

    for pattern in ROUTE_PATTERNS:
        for match in pattern.finditer(content):
            groups = match.groups()
            if len(groups) == 2:
                if pattern.pattern.startswith("""\\.route"""):
                    path, method = groups[0], groups[1]
                else:
                    method, path = groups[0], groups[1]
                key = (method.upper(), path)
                if key in seen:
                    continue
                seen.add(key)
                line = content[: match.start()].count("\n") + 1
                endpoints.append({
                    "method": method.upper(),
                    "path": path,
                    "file": rel_path,
                    "line": line,
                    "framework": "Express",
                })

    return endpoints


def _detect_js_entry_points(content: str, rel_path: str) -> list[dict]:
    found: list[dict] = []
    for pattern, reason in ENTRY_POINT_PATTERNS:
        if pattern.search(content):
            found.append({
                "path": rel_path,
                "reason": reason,
                "source": "js_heuristic",
            })
    return found


def analyze_js_repository(repo_path: Path) -> JsAnalysisResult:
    js_files = list(iter_repo_files(repo_path, extensions=JS_EXTENSIONS))
    js_files = js_files[:MAX_JS_FILES]

    file_analyses: dict[str, JsFileAnalysis] = {}
    all_endpoints: list[dict] = []
    all_entry_points: list[dict] = []
    dependency_edges: list[dict] = []

    for file_path in js_files:
        content = read_text_safe(file_path)
        if not content.strip():
            continue

        rel_path = relative_posix_path(repo_path, file_path)
        internal, external = _extract_imports(content, rel_path)
        endpoints = _extract_routes(content, rel_path)
        entry_points = _detect_js_entry_points(content, rel_path)

        analysis = JsFileAnalysis(
            path=rel_path,
            line_count=content.count("\n") + 1,
            byte_size=file_path.stat().st_size if file_path.exists() else 0,
            internal_imports=internal,
            external_imports=external,
        )
        file_analyses[rel_path] = analysis
        all_endpoints.extend(endpoints)
        all_entry_points.extend(entry_points)

        for target in internal:
            dependency_edges.append({"source": rel_path, "target": target})

    package_counts: dict[str, int] = {}
    for analysis in file_analyses.values():
        for pkg in analysis.external_imports:
            package_counts[pkg] = package_counts.get(pkg, 0) + 1

    largest_files = sorted(
        [
            {"path": a.path, "lines": a.line_count, "bytes": a.byte_size}
            for a in file_analyses.values()
        ],
        key=lambda item: (-item["lines"], item["path"]),
    )[:10]

    files_with_most_imports = sorted(
        [
            {
                "path": a.path,
                "import_count": len(a.internal_imports) + len(a.external_imports),
            }
            for a in file_analyses.values()
        ],
        key=lambda item: (-item["import_count"], item["path"]),
    )[:10]

    frequent_external_packages = [
        {"package": name, "count": count}
        for name, count in sorted(package_counts.items(), key=lambda item: (-item[1], item[0]))
    ][:15]

    return JsAnalysisResult(
        files_analyzed=len(file_analyses),
        file_analyses=file_analyses,
        api_endpoints=all_endpoints,
        dependency_edges=dependency_edges,
        detected_entry_points=all_entry_points,
        frequent_external_packages=frequent_external_packages,
        largest_files=largest_files,
        files_with_most_imports=files_with_most_imports,
    )


def js_analysis_to_dict(result: JsAnalysisResult) -> dict:
    imports_by_file = {
        path: {
            "internal": analysis.internal_imports,
            "external": analysis.external_imports,
        }
        for path, analysis in result.file_analyses.items()
        if analysis.internal_imports or analysis.external_imports
    }

    return {
        "files_analyzed": result.files_analyzed,
        "imports": {
            "by_file": imports_by_file,
            "frequent_packages": result.frequent_external_packages,
        },
        "api_endpoints": result.api_endpoints,
        "dependency_map": result.dependency_edges,
        "largest_files": result.largest_files,
        "files_with_most_imports": result.files_with_most_imports,
        "detected_entry_points": result.detected_entry_points,
    }


def detect_node_entry_from_package_json(repo_path: Path) -> list[dict]:
    """Read package.json main/bin/scripts fields as factual entry-point signals."""

    found: list[dict] = []
    for package_path in [repo_path / "package.json", *repo_path.glob("*/package.json")]:
        if not package_path.is_file():
            continue
        try:
            data = json.loads(package_path.read_text(encoding="utf-8", errors="replace"))
        except (json.JSONDecodeError, OSError):
            continue

        rel_base = relative_posix_path(repo_path, package_path.parent)
        prefix = f"{rel_base}/" if rel_base != "." else ""

        main = data.get("main")
        if isinstance(main, str) and main:
            found.append({
                "path": f"{prefix}{main}".replace("//", "/"),
                "reason": "package.json main field",
                "source": "package.json",
            })

        bin_field = data.get("bin")
        if isinstance(bin_field, str):
            found.append({
                "path": f"{prefix}{bin_field}".replace("//", "/"),
                "reason": "package.json bin field",
                "source": "package.json",
            })
        elif isinstance(bin_field, dict):
            for target in bin_field.values():
                if isinstance(target, str):
                    found.append({
                        "path": f"{prefix}{target}".replace("//", "/"),
                        "reason": "package.json bin field",
                        "source": "package.json",
                    })

        scripts = data.get("scripts", {})
        if isinstance(scripts, dict):
            for script_name in ("start", "dev", "serve"):
                if script_name in scripts:
                    found.append({
                        "path": f"{prefix}package.json",
                        "reason": f'npm script "{script_name}": {scripts[script_name]}',
                        "source": "package.json",
                    })
                    break

    return found
