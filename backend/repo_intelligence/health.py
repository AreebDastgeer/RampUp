"""
Repository health detector — factual signals computed from the filesystem.

These booleans and labels are derived automatically (not inferred by the LLM)
so the dashboard and onboarding brief can cite concrete repository facts.
"""

from pathlib import Path

from repo_intelligence.utils import iter_repo_files, should_ignore_path

LICENSE_NAMES = frozenset({
    "license",
    "license.md",
    "license.txt",
    "copying",
    "copying.md",
})

PACKAGE_MANAGERS = (
    ("package.json", "npm/yarn/pnpm"),
    ("requirements.txt", "pip"),
    ("pyproject.toml", "poetry/uv/pip"),
    ("Pipfile", "pipenv"),
    ("poetry.lock", "poetry"),
    ("Cargo.toml", "cargo"),
    ("go.mod", "go modules"),
    ("Gemfile", "bundler"),
    ("pom.xml", "maven"),
    ("build.gradle", "gradle"),
)


def _has_readme(repo_path: Path) -> bool:
    for name in ("README.md", "Readme.md", "readme.md", "README.MD", "README"):
        if (repo_path / name).is_file():
            return True
    return False


def _has_license(repo_path: Path) -> bool:
    for item in repo_path.iterdir():
        if item.is_file() and item.name.lower() in LICENSE_NAMES:
            return True
    return False


def _detect_tests(repo_path: Path) -> bool:
    test_dir_names = {"tests", "test", "__tests__", "spec", "specs"}
    for item in repo_path.rglob("*"):
        if should_ignore_path(item):
            continue
        if item.is_dir() and item.name.lower() in test_dir_names:
            return True
        if item.is_file():
            name = item.name.lower()
            if (
                name.startswith("test_")
                or name.endswith("_test.py")
                or name.endswith(".test.js")
                or name.endswith(".test.ts")
                or name.endswith(".test.tsx")
                or name.endswith(".spec.js")
                or name.endswith(".spec.ts")
                or name.endswith(".spec.tsx")
            ):
                return True
    return False


def _detect_docker(repo_path: Path) -> bool:
    for item in repo_path.iterdir():
        if not item.is_file():
            continue
        lower = item.name.lower()
        if lower == "dockerfile" or lower.startswith("dockerfile.") or lower.startswith("docker-compose"):
            return True
    return False


def _detect_ci_workflow(repo_path: Path) -> bool:
    ci_paths = (
        repo_path / ".github" / "workflows",
        repo_path / ".gitlab-ci.yml",
        repo_path / ".circleci",
        repo_path / "azure-pipelines.yml",
        repo_path / "Jenkinsfile",
        repo_path / ".travis.yml",
    )
    for ci_path in ci_paths:
        if ci_path.is_file():
            return True
        if ci_path.is_dir():
            try:
                if any(ci_path.iterdir()):
                    return True
            except OSError:
                pass
    return False


def _detect_github_actions(repo_path: Path) -> bool:
    workflows = repo_path / ".github" / "workflows"
    if not workflows.is_dir():
        return False
    try:
        return any(
            item.suffix.lower() in {".yml", ".yaml"}
            for item in workflows.iterdir()
            if item.is_file()
        )
    except OSError:
        return False


def _detect_env_example(repo_path: Path) -> bool:
    for item in iter_repo_files(repo_path, extensions=None, max_depth=3):
        name = item.name.lower()
        if name in {".env.example", ".env.sample", ".env.template", "env.example"}:
            return True
    return False


def _detect_package_managers(repo_path: Path) -> list[str]:
    found: list[str] = []
    for filename, label in PACKAGE_MANAGERS:
        if (repo_path / filename).is_file():
            found.append(label)
        else:
            for child in repo_path.iterdir():
                if child.is_dir() and not should_ignore_path(child) and (child / filename).is_file():
                    if label not in found:
                        found.append(label)
    return found


def detect_repository_health(repo_path: Path) -> dict:
    return {
        "readme_present": _has_readme(repo_path),
        "license_present": _has_license(repo_path),
        "tests_detected": _detect_tests(repo_path),
        "docker_detected": _detect_docker(repo_path),
        "ci_workflow_detected": _detect_ci_workflow(repo_path),
        "github_actions_detected": _detect_github_actions(repo_path),
        "env_example_detected": _detect_env_example(repo_path),
        "package_managers": _detect_package_managers(repo_path),
    }
