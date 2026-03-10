"""Security-focused tests for installer and verifier behavior."""

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    """Load a Python module directly from a repository file."""
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


install_module = load_module("gsd_install", ROOT / "install.py")
verify_module = load_module("gsd_verify", ROOT / "verify.py")


class TestInstallerSecurity:
    """Validate installer path safety checks."""

    def test_rejects_paths_outside_project_root(self, tmp_path: Path) -> None:
        installer = install_module.GSDInstaller(tmp_path, "DemoProject")

        with pytest.raises(install_module.InstallationSecurityError):
            installer._ensure_path_is_safe(tmp_path.parent / "escaped.txt")

    def test_writes_files_inside_project_root(self, tmp_path: Path) -> None:
        installer = install_module.GSDInstaller(tmp_path, "DemoProject")
        target = tmp_path / "nested" / "file.txt"

        installer._write_text_file(target, "safe")

        assert target.read_text(encoding="utf-8") == "safe"


class TestVerifierSecurity:
    """Validate verifier import and module discovery hardening."""

    def test_skips_invalid_module_names(self, tmp_path: Path) -> None:
        project_root = tmp_path / "demo"
        invalid_module = project_root / "src" / "bad-module"
        invalid_module.mkdir(parents=True)

        verifier = verify_module.GSDVerifier(project_root=project_root)

        assert verifier._discover_module_dir() is None
        assert any(issue["issue"] == "invalid module directory name" for issue in verifier.issues)

    def test_import_check_handles_project_paths_with_quotes(self, tmp_path: Path) -> None:
        project_root = tmp_path / "project's-demo"
        module_dir = project_root / "src" / "samplepkg"
        module_dir.mkdir(parents=True)
        (module_dir / "gsd_orchestrator.py").write_text(
            "class GSDOrchestrator:\n    pass\n",
            encoding="utf-8",
        )

        verifier = verify_module.GSDVerifier(project_root=project_root)

        assert verifier.check_imports() is True
