"""
Python AST analyzer — extracts factual structure from .py source files.

Uses the standard library ast module (no extra dependencies) to detect:
- imports (internal vs external)
- classes and top-level functions
- API route decorators (FastAPI, Flask)
- entry-point signals (__main__, uvicorn.run, etc.)
- per-file metrics for largest-files / most-imports ranking
"""

import ast
from dataclasses import dataclass, field
from pathlib import Path

from repo_intelligence.utils import (
    MAX_PYTHON_FILES,
    iter_repo_files,
    read_text_safe,
    relative_posix_path,
)

# HTTP methods exposed by common Python web framework decorators.
FASTAPI_HTTP_METHODS = frozenset({
    "get", "post", "put", "delete", "patch", "head", "options", "trace",
})

FLASK_HTTP_METHODS = frozenset({"route", "get", "post", "put", "delete", "patch"})


@dataclass
class ApiEndpoint:
    method: str
    path: str
    file: str
    line: int
    framework: str


@dataclass
class CodeSymbol:
    name: str
    kind: str  # "class" | "function"
    file: str
    line: int


@dataclass
class FileImports:
    internal: list[str] = field(default_factory=list)
    external: list[str] = field(default_factory=list)


@dataclass
class FileAnalysis:
    path: str
    line_count: int
    byte_size: int
    imports: FileImports
    classes: list[CodeSymbol] = field(default_factory=list)
    functions: list[CodeSymbol] = field(default_factory=list)
    endpoints: list[ApiEndpoint] = field(default_factory=list)
    is_entry_point: bool = False
    entry_point_reason: str = ""


@dataclass
class PythonAnalysisResult:
    files_analyzed: int
    file_analyses: dict[str, FileAnalysis]
    api_endpoints: list[ApiEndpoint]
    dependency_edges: list[dict[str, str]]
    largest_files: list[dict]
    files_with_most_imports: list[dict]
    detected_entry_points: list[dict]
    frequent_external_packages: list[dict]
    all_classes: list[CodeSymbol]
    all_functions: list[CodeSymbol]


def _string_from_node(node: ast.expr | None) -> str | None:
    if node is None:
        return None
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        parts = []
        for value in node.values:
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                parts.append(value.value)
        return "".join(parts) if parts else None
    return None


def _decorator_name(decorator: ast.expr) -> str | None:
    if isinstance(decorator, ast.Name):
        return decorator.id
    if isinstance(decorator, ast.Attribute):
        return decorator.attr
    if isinstance(decorator, ast.Call):
        return _decorator_name(decorator.func)
    return None


def _decorator_base_name(decorator: ast.expr) -> str | None:
    if isinstance(decorator, ast.Attribute):
        return decorator.attr
    if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute):
        return decorator.func.attr
    return None


def _decorator_owner(decorator: ast.expr) -> str | None:
    if isinstance(decorator, ast.Attribute) and isinstance(decorator.value, ast.Name):
        return decorator.value.id
    if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute):
        if isinstance(decorator.func.value, ast.Name):
            return decorator.func.value.id
    return None


def _extract_route_from_decorator(
    decorator: ast.expr,
    file_path: str,
    line: int,
) -> ApiEndpoint | None:
    if not isinstance(decorator, ast.Call):
        return None

    method_name = _decorator_base_name(decorator)
    if not method_name:
        return None

    path = None
    if decorator.args:
        path = _string_from_node(decorator.args[0])

    methods: list[str] = []
    framework = ""

    if method_name in FASTAPI_HTTP_METHODS:
        methods = [method_name.upper()]
        framework = "FastAPI"
    elif method_name == "route":
        framework = "Flask"
        methods = ["GET"]
        for keyword in decorator.keywords:
            if keyword.arg == "methods" and isinstance(keyword.value, ast.List):
                methods = []
                for elt in keyword.value.elts:
                    value = _string_from_node(elt)
                    if value:
                        methods.append(value.upper())
        if not methods:
            methods = ["GET"]
    elif method_name in FLASK_HTTP_METHODS - {"route"}:
        framework = "Flask"
        methods = [method_name.upper()]

    if not methods or not path:
        return None

    return ApiEndpoint(
        method=methods[0] if len(methods) == 1 else ",".join(methods),
        path=path,
        file=file_path,
        line=line,
        framework=framework,
    )


def _resolve_internal_module(
    module: str | None,
    name: str | None,
    source_file: Path,
    repo_path: Path,
    python_modules: set[str],
) -> str | None:
    """Map an import statement to a repository .py file when possible."""

    candidates: list[str] = []

    if module:
        dotted = module.replace(".", "/")
        candidates.extend([
            f"{dotted}.py",
            f"{dotted}/__init__.py",
        ])
        if source_file.parent != repo_path:
            rel_parent = source_file.parent.relative_to(repo_path).as_posix()
            candidates.append(f"{rel_parent}/{dotted}.py".replace("./", ""))
            candidates.append(f"{rel_parent}/{dotted}/__init__.py".replace("./", ""))

    if name and not module:
        rel_parent = source_file.parent.relative_to(repo_path).as_posix()
        if rel_parent != ".":
            candidates.append(f"{rel_parent}/{name}.py")
        candidates.append(f"{name}.py")

    for candidate in candidates:
        normalized = candidate.replace("//", "/").lstrip("/")
        if normalized in python_modules:
            return normalized

    return None


def _collect_imports(
    tree: ast.AST,
    source_file: Path,
    repo_path: Path,
    python_modules: set[str],
) -> FileImports:
    internal: list[str] = []
    external: list[str] = []
    seen_internal: set[str] = set()
    seen_external: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                top_level = alias.name.split(".")[0]
                resolved = _resolve_internal_module(alias.name, None, source_file, repo_path, python_modules)
                if resolved:
                    if resolved not in seen_internal:
                        seen_internal.add(resolved)
                        internal.append(resolved)
                elif top_level not in seen_external:
                    seen_external.add(top_level)
                    external.append(top_level)

        elif isinstance(node, ast.ImportFrom):
            if node.module is None:
                continue
            top_level = node.module.split(".")[0]
            resolved = _resolve_internal_module(node.module, None, source_file, repo_path, python_modules)
            if resolved:
                if resolved not in seen_internal:
                    seen_internal.add(resolved)
                    internal.append(resolved)
            elif node.level and node.level > 0:
                # Relative import — resolve against package structure.
                rel_parent = source_file.parent.relative_to(repo_path).as_posix()
                parts = rel_parent.split("/") if rel_parent != "." else []
                if node.level <= len(parts):
                    base_parts = parts[: len(parts) - node.level + 1] if node.level > 1 else parts
                else:
                    base_parts = []
                rel_module = "/".join(base_parts + node.module.split("."))
                rel_candidates = [f"{rel_module}.py", f"{rel_module}/__init__.py"]
                matched = next((c for c in rel_candidates if c in python_modules), None)
                if matched and matched not in seen_internal:
                    seen_internal.add(matched)
                    internal.append(matched)
            elif top_level not in seen_external:
                seen_external.add(top_level)
                external.append(top_level)

    return FileImports(internal=sorted(internal), external=sorted(external))


def _detect_entry_point_signals(tree: ast.AST) -> tuple[bool, str]:
    reasons: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            test = node.test
            if (
                isinstance(test, ast.Compare)
                and isinstance(test.left, ast.Name)
                and test.left.id == "__name__"
            ):
                for comparator in test.comparators:
                    if isinstance(comparator, ast.Constant) and comparator.value == "__main__":
                        reasons.append("__main__ guard")

        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute):
                if func.attr == "run" and isinstance(func.value, ast.Name):
                    if func.value.id in {"uvicorn", "app"}:
                        reasons.append(f"{func.value.id}.run()")
                if func.attr == "execute_from_command_line":
                    reasons.append("django management command")

    if reasons:
        return True, "; ".join(dict.fromkeys(reasons))
    return False, ""


def _analyze_single_file(
    file_path: Path,
    repo_path: Path,
    python_modules: set[str],
) -> FileAnalysis | None:
    content = read_text_safe(file_path)
    if not content.strip():
        return None

    try:
        tree = ast.parse(content, filename=str(file_path))
    except SyntaxError:
        return None

    rel_path = relative_posix_path(repo_path, file_path)
    imports = _collect_imports(tree, file_path, repo_path, python_modules)

    classes: list[CodeSymbol] = []
    functions: list[CodeSymbol] = []
    endpoints: list[ApiEndpoint] = []

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            classes.append(CodeSymbol(name=node.name, kind="class", file=rel_path, line=node.lineno))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append(CodeSymbol(name=node.name, kind="function", file=rel_path, line=node.lineno))
            for decorator in node.decorator_list:
                endpoint = _extract_route_from_decorator(decorator, rel_path, node.lineno)
                if endpoint:
                    endpoints.append(endpoint)

    is_entry, reason = _detect_entry_point_signals(tree)

    analysis = FileAnalysis(
        path=rel_path,
        line_count=content.count("\n") + (1 if content and not content.endswith("\n") else 0),
        byte_size=file_path.stat().st_size if file_path.exists() else len(content.encode()),
        imports=imports,
        classes=classes,
        functions=functions,
        endpoints=endpoints,
        is_entry_point=is_entry,
        entry_point_reason=reason,
    )
    return analysis


def analyze_python_repository(repo_path: Path) -> PythonAnalysisResult:
    """
    Walk all Python files and build structured analysis from AST parsing.
    Caps file count to keep analysis fast on large monorepos.
    """

    python_files = list(iter_repo_files(repo_path, extensions=frozenset({".py"})))
    python_files = python_files[:MAX_PYTHON_FILES]

    python_modules = {
        relative_posix_path(repo_path, path)
        for path in python_files
    }

    file_analyses: dict[str, FileAnalysis] = {}
    all_endpoints: list[ApiEndpoint] = []
    all_classes: list[CodeSymbol] = []
    all_functions: list[CodeSymbol] = []
    detected_entry_points: list[dict] = []

    for file_path in python_files:
        analysis = _analyze_single_file(file_path, repo_path, python_modules)
        if not analysis:
            continue

        file_analyses[analysis.path] = analysis
        all_classes.extend(analysis.classes)
        all_functions.extend(analysis.functions)

        all_endpoints.extend(analysis.endpoints)

        if analysis.is_entry_point:
            detected_entry_points.append({
                "path": analysis.path,
                "reason": analysis.entry_point_reason,
                "source": "python_ast",
            })

    # Build lightweight dependency map (file -> files it imports).
    dependency_edges: list[dict[str, str]] = []
    for path, analysis in file_analyses.items():
        for target in analysis.imports.internal:
            dependency_edges.append({"source": path, "target": target})

    # Rank files by size and import count for dashboard-style insights.
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
                "import_count": len(a.imports.internal) + len(a.imports.external),
                "internal_count": len(a.imports.internal),
                "external_count": len(a.imports.external),
            }
            for a in file_analyses.values()
        ],
        key=lambda item: (-item["import_count"], item["path"]),
    )[:10]

    # Aggregate external package frequency across all files.
    package_counts: dict[str, int] = {}
    for analysis in file_analyses.values():
        for package in analysis.imports.external:
            package_counts[package] = package_counts.get(package, 0) + 1

    frequent_external_packages = [
        {"package": name, "count": count}
        for name, count in sorted(package_counts.items(), key=lambda item: (-item[1], item[0]))
    ][:15]

    return PythonAnalysisResult(
        files_analyzed=len(file_analyses),
        file_analyses=file_analyses,
        api_endpoints=all_endpoints,
        dependency_edges=dependency_edges,
        largest_files=largest_files,
        files_with_most_imports=files_with_most_imports,
        detected_entry_points=detected_entry_points,
        frequent_external_packages=frequent_external_packages,
        all_classes=all_classes[:50],
        all_functions=all_functions[:80],
    )


def python_analysis_to_dict(result: PythonAnalysisResult) -> dict:
    """Serialize PythonAnalysisResult for API / LLM consumption."""

    imports_by_file = {
        path: {
            "internal": analysis.imports.internal,
            "external": analysis.imports.external,
        }
        for path, analysis in result.file_analyses.items()
        if analysis.imports.internal or analysis.imports.external
    }

    return {
        "files_analyzed": result.files_analyzed,
        "imports": {
            "by_file": imports_by_file,
            "frequent_packages": result.frequent_external_packages,
        },
        "api_endpoints": [
            {
                "method": ep.method,
                "path": ep.path,
                "file": ep.file,
                "line": ep.line,
                "framework": ep.framework,
            }
            for ep in result.api_endpoints
        ],
        "dependency_map": result.dependency_edges,
        "largest_files": result.largest_files,
        "files_with_most_imports": result.files_with_most_imports,
        "detected_entry_points": result.detected_entry_points,
        "classes": [
            {"name": s.name, "file": s.file, "line": s.line}
            for s in result.all_classes
        ],
        "functions": [
            {"name": s.name, "file": s.file, "line": s.line}
            for s in result.all_functions
        ],
    }
