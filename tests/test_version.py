import tomllib
from pathlib import Path

from forja import __version__


def test_version_matches_pyproject():
    pyproject = Path(__file__).resolve().parent.parent / "pyproject.toml"
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    assert data["project"]["version"] == __version__


def test_version_in_changelog():
    changelog = Path(__file__).resolve().parent.parent / "CHANGELOG.md"
    assert f"[{__version__}]" in changelog.read_text(encoding="utf-8")
