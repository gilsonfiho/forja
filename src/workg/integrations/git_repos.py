"""Descoberta e inspeção de repositórios Git locais.

Usa a CLI ``git`` via subprocess (sem dependência obrigatória) para coletar
metadados úteis de cada repositório encontrado sob uma raiz.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path

# Arquivos que sinalizam stack / práticas do repositório.
STACK_MARKERS: dict[str, str] = {
    "pyproject.toml": "python",
    "requirements.txt": "python",
    "package.json": "node",
    "pom.xml": "java/maven",
    "build.gradle": "java/gradle",
    "go.mod": "go",
    "Cargo.toml": "rust",
    "Dockerfile": "docker",
    "docker-compose.yml": "docker-compose",
    ".csproj": "dotnet",
}
CI_MARKERS: tuple[str, ...] = (
    ".github/workflows",
    ".gitlab-ci.yml",
    "Jenkinsfile",
    "azure-pipelines.yml",
)


@dataclass(slots=True)
class RepoInfo:
    name: str
    path: str
    current_branch: str | None = None
    last_commit: str | None = None
    last_commit_date: str | None = None
    remotes: list[str] = field(default_factory=list)
    dirty: bool = False
    ahead_behind: str | None = None
    stacks: list[str] = field(default_factory=list)
    has_ci: bool = False
    has_tests: bool = False
    has_readme: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "path": self.path,
            "current_branch": self.current_branch,
            "last_commit": self.last_commit,
            "last_commit_date": self.last_commit_date,
            "remotes": self.remotes,
            "dirty": self.dirty,
            "stacks": self.stacks,
            "has_ci": self.has_ci,
            "has_tests": self.has_tests,
            "has_readme": self.has_readme,
        }


def _git(path: Path, *args: str) -> str:
    try:
        out = subprocess.run(  # noqa: S603
            ["git", *args],
            cwd=path,
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
        return out.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def discover_repos(root: Path, max_depth: int = 3) -> list[Path]:
    """Encontra diretórios que contêm ``.git`` sob ``root`` até ``max_depth``."""
    root = Path(root)
    found: list[Path] = []
    if not root.exists():
        return found

    def _walk(directory: Path, depth: int) -> None:
        if depth > max_depth:
            return
        if (directory / ".git").exists():
            found.append(directory)
            return  # não desce dentro de um repo
        try:
            for child in sorted(directory.iterdir()):
                if child.is_dir() and not child.name.startswith("."):
                    _walk(child, depth + 1)
        except (PermissionError, OSError):
            return

    _walk(root, 0)
    return found


def inspect_repo(path: Path) -> RepoInfo:
    path = Path(path)
    info = RepoInfo(name=path.name, path=str(path))

    info.current_branch = _git(path, "rev-parse", "--abbrev-ref", "HEAD") or None
    info.last_commit = _git(path, "log", "-1", "--pretty=%h %s") or None
    info.last_commit_date = _git(path, "log", "-1", "--pretty=%cI") or None
    remotes = _git(path, "remote")
    info.remotes = [r for r in remotes.splitlines() if r]
    info.dirty = bool(_git(path, "status", "--porcelain"))

    names = {p.name for p in path.iterdir()} if path.exists() else set()
    stacks: set[str] = set()
    for marker, stack in STACK_MARKERS.items():
        if marker in names or any(n.endswith(marker) for n in names):
            stacks.add(stack)
    info.stacks = sorted(stacks)
    info.has_ci = any((path / m).exists() for m in CI_MARKERS)
    info.has_tests = any((path / d).exists() for d in ("tests", "test", "spec"))
    info.has_readme = any(n.lower().startswith("readme") for n in names)
    return info


def scan(root: Path, max_depth: int = 3) -> list[RepoInfo]:
    return [inspect_repo(p) for p in discover_repos(root, max_depth)]
