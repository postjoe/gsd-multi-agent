"""End-to-end bootstrap tests for install and verify flows."""

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    """Load a Python module directly from a repository file."""
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


install_module = load_module("gsd_install_e2e", ROOT / "install.py")
verify_module = load_module("gsd_verify_e2e", ROOT / "verify.py")


def test_install_and_verify_dummy_project(tmp_path: Path) -> None:
    """Bootstrap a dummy project without dependency install and verify the result."""
    project_root = tmp_path / "dummy-project"
    project_root.mkdir()

    installer = install_module.GSDInstaller(
        project_root=project_root,
        project_name="Dummy Project",
    )

    assert installer.install(skip_deps=True, skip_tests=True) is True
    assert (project_root / "src" / "gsd_orchestrator.py").exists()
    assert (project_root / ".claude" / "settings.local.json").exists()

    verifier = verify_module.GSDVerifier(project_root=project_root)

    assert verifier.check_directories() is True
    assert verifier.check_core_files() is True
    assert verifier.check_source_files() is True
    assert verifier.check_imports() is True
