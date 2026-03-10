#!/usr/bin/env python3
"""
GSD Multi-Agent System - Verification Script

This script verifies that the GSD system is properly installed and configured.
It checks directories, files, imports, configuration, and runs basic tests.

Usage:
    python gsd_setup/verify.py
    python gsd_setup/verify.py --verbose
    python gsd_setup/verify.py --fix

Behavior:
    - Reads files from the selected project root
    - Imports the local orchestrator module from src/
    - Executes lightweight dependency and test checks
"""

import argparse
import importlib
import json
import re
import subprocess
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path


class GSDVerifier:
    """Verifier for GSD multi-agent workflow system installation."""

    def __init__(self, project_root: Path, verbose: bool = False):
        """Initialize verifier.

        Args:
            project_root: Root directory of the project
            verbose: Enable verbose output
        """
        self.project_root = project_root
        self.verbose = verbose
        self.checks_passed = 0
        self.checks_failed = 0
        self.issues: list[dict[str, str]] = []
        self._module_name_pattern = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

    def log(self, message: str, level: str = "INFO") -> None:
        """Log a message with level indicator."""
        if level == "DEBUG" and not self.verbose:
            return

        prefix = {
            "INFO": "ℹ️ ",
            "SUCCESS": "✅",
            "WARNING": "⚠️ ",
            "ERROR": "❌",
            "DEBUG": "🔍"
        }.get(level, "")
        print(f"{prefix} {message}")

    def describe_plan(self) -> None:
        """Print the checks this verifier will perform."""
        self.log(f"Verifying project root: {self.project_root}", "INFO")
        self.log(
            "This command reads files, imports the local orchestrator, and may run tests.",
            "INFO",
        )

    def _discover_module_dir(self) -> Path | None:
        """Return the first valid Python module directory under src/."""
        src_dir = self.project_root / "src"
        if not src_dir.exists():
            return None

        for directory in src_dir.iterdir():
            if not directory.is_dir() or directory.name.startswith("_"):
                continue
            if self._module_name_pattern.match(directory.name):
                return directory

            self.log(f"  Skipping invalid module name: {directory.name}", "WARNING")
            self.issues.append({
                "type": "module",
                "path": str(directory.relative_to(self.project_root)),
                "issue": "invalid module directory name",
                "fix": "Rename the module directory to a valid Python identifier"
            })

        return None

    def _discover_orchestrator_location(self) -> tuple[str, Path] | None:
        """Return the import target and file path for the orchestrator module."""
        src_dir = self.project_root / "src"
        flat_module = src_dir / "gsd_orchestrator.py"
        if flat_module.exists():
            return ("gsd_orchestrator", flat_module)

        module_dir = self._discover_module_dir()
        if module_dir is None:
            return None

        return (f"{module_dir.name}.gsd_orchestrator", module_dir / "gsd_orchestrator.py")

    @contextmanager
    def _temporary_sys_path(self, path: Path) -> Iterator[None]:
        """Temporarily prepend a path to sys.path for import checks."""
        sys.path.insert(0, str(path))
        try:
            yield
        finally:
            if sys.path and sys.path[0] == str(path):
                sys.path.pop(0)

    def check_directories(self) -> bool:
        """Check if required directories exist."""
        self.log("Checking directories...", "INFO")

        required_dirs = [
            ".claude",
            "antigravity",
            "scripts",
            "tests",
            "docs",
            "src",
        ]

        all_exist = True
        for dir_name in required_dirs:
            dir_path = self.project_root / dir_name
            if dir_path.exists():
                self.log(f"  {dir_name}/", "SUCCESS")
                self.checks_passed += 1
            else:
                self.log(f"  {dir_name}/ - MISSING", "ERROR")
                self.checks_failed += 1
                self.issues.append({
                    "type": "directory",
                    "path": dir_name,
                    "issue": "missing",
                    "fix": f"mkdir -p {dir_name}"
                })
                all_exist = False

        return all_exist

    def check_core_files(self) -> bool:
        """Check if core files exist."""
        self.log("Checking core files...", "INFO")

        core_files = [
            ".claude/settings.local.json",
            "antigravity/agent_policy.yaml",
            "skills-lock.json",
            "CLAUDE.md",
            "TASK_TOOL_CAPABILITY.md",
        ]

        all_exist = True
        for file_path in core_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                self.log(f"  {file_path}", "SUCCESS")
                self.checks_passed += 1
            else:
                self.log(f"  {file_path} - MISSING", "ERROR")
                self.checks_failed += 1
                self.issues.append({
                    "type": "file",
                    "path": file_path,
                    "issue": "missing",
                    "fix": f"Copy from gsd_setup/templates/{file_path}"
                })
                all_exist = False

        return all_exist

    def check_source_files(self) -> bool:
        """Check if source code files exist."""
        self.log("Checking source files...", "INFO")

        orchestrator_info = self._discover_orchestrator_location()
        if orchestrator_info is None:
            self.log("  No source module found", "ERROR")
            self.issues.append({
                "type": "module",
                "path": "src/",
                "issue": "no module directory",
                "fix": "Create src/your_module/ directory"
            })
            return False

        module_name, orchestrator_path = orchestrator_info
        self.log(f"  Found orchestrator module: {module_name}", "INFO")

        # Check for orchestrator
        if orchestrator_path.exists():
            self.log("  gsd_orchestrator.py", "SUCCESS")
            self.checks_passed += 1
        else:
            self.log("  gsd_orchestrator.py - MISSING", "ERROR")
            self.checks_failed += 1
            self.issues.append({
                "type": "file",
                "path": str(orchestrator_path.relative_to(self.project_root)),
                "issue": "missing",
                "fix": "Copy from gsd_setup/src/gsd_orchestrator.py"
            })

        return orchestrator_path.exists()

    def check_test_files(self) -> bool:
        """Check if test files exist."""
        self.log("Checking test files...", "INFO")

        test_files = [
            "tests/test_gsd_workflow.py",
            "tests/test_gsd_orchestrator.py",
        ]

        all_exist = True
        for file_path in test_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                self.log(f"  {file_path}", "SUCCESS")
                self.checks_passed += 1
            else:
                self.log(f"  {file_path} - MISSING", "WARNING")
                self.issues.append({
                    "type": "file",
                    "path": file_path,
                    "issue": "missing",
                    "fix": f"Copy from gsd_setup/{file_path}"
                })

        return all_exist

    def check_scripts(self) -> bool:
        """Check if utility scripts exist."""
        self.log("Checking utility scripts...", "INFO")

        scripts = [
            "scripts/demo_gsd_workflow.py",
            "scripts/demo_orchestrator.py",
            "scripts/validate_gsd_system.py",
        ]

        all_exist = True
        for script in scripts:
            full_path = self.project_root / script
            if full_path.exists():
                self.log(f"  {script}", "SUCCESS")
                self.checks_passed += 1
            else:
                self.log(f"  {script} - MISSING", "WARNING")
                self.issues.append({
                    "type": "file",
                    "path": script,
                    "issue": "missing",
                    "fix": f"Copy from gsd_setup/{script}"
                })

        return all_exist

    def check_configuration(self) -> bool:
        """Check configuration files are valid."""
        self.log("Checking configuration validity...", "INFO")

        # Check Claude settings
        settings_path = self.project_root / ".claude" / "settings.local.json"
        if settings_path.exists():
            try:
                with open(settings_path) as f:
                    settings = json.load(f)
                if "permissions" in settings:
                    self.log("  Claude settings valid", "SUCCESS")
                    self.checks_passed += 1
                else:
                    self.log("  Claude settings incomplete", "WARNING")
                    self.issues.append({
                        "type": "config",
                        "path": ".claude/settings.local.json",
                        "issue": "missing permissions",
                        "fix": "Add permissions section to settings"
                    })
            except json.JSONDecodeError as e:
                self.log(f"  Claude settings invalid JSON: {e}", "ERROR")
                self.checks_failed += 1
                return False

        # Check agent policy
        policy_path = self.project_root / "antigravity" / "agent_policy.yaml"
        if policy_path.exists():
            content = policy_path.read_text()
            if "opencode" in content.lower():
                self.log("  Agent policy includes OpenCode (FREE)", "SUCCESS")
                self.checks_passed += 1
            else:
                self.log("  Agent policy missing OpenCode configuration", "WARNING")
                self.issues.append({
                    "type": "config",
                    "path": "antigravity/agent_policy.yaml",
                    "issue": "missing OpenCode",
                    "fix": "Add OpenCode (MiniMax) configuration for FREE tier"
                })

        # Check skills
        skills_path = self.project_root / "skills-lock.json"
        if skills_path.exists():
            try:
                with open(skills_path) as f:
                    skills = json.load(f)
                if "gsd" in skills.get("skills", {}):
                    self.log("  GSD skill configured", "SUCCESS")
                    self.checks_passed += 1
                else:
                    self.log("  GSD skill not found", "WARNING")
                    self.issues.append({
                        "type": "config",
                        "path": "skills-lock.json",
                        "issue": "missing GSD skill",
                        "fix": "Add GSD skill to skills-lock.json"
                    })
            except json.JSONDecodeError:
                self.log("  Skills file invalid", "ERROR")
                self.checks_failed += 1

        return True

    def check_imports(self) -> bool:
        """Check if Python imports work."""
        self.log("Checking Python imports...", "INFO")

        orchestrator_info = self._discover_orchestrator_location()
        if orchestrator_info is None:
            self.log("  Cannot test imports - no module found", "WARNING")
            return False

        module_name, orchestrator_path = orchestrator_info

        try:
            with self._temporary_sys_path(self.project_root / "src"):
                module = importlib.import_module(module_name)

            if hasattr(module, "GSDOrchestrator"):
                self.log(f"  Can import {module_name}", "SUCCESS")
                self.checks_passed += 1
                return True
            else:
                self.log("  Import failed: GSDOrchestrator not found", "ERROR")
                self.checks_failed += 1
                self.issues.append({
                    "type": "import",
                    "path": str(orchestrator_path.relative_to(self.project_root)),
                    "issue": "import error",
                    "fix": "Check module structure and dependencies"
                })
                return False
        except Exception as e:
            self.log(f"  Import test failed: {e}", "ERROR")
            self.checks_failed += 1
            return False

    def check_dependencies(self) -> bool:
        """Check if required dependencies are installed."""
        self.log("Checking dependencies...", "INFO")

        required_packages = [
            "pytest",
            "ruff",
            "mypy",
            "yaml",
        ]

        all_installed = True
        for package in required_packages:
            try:
                result = subprocess.run(
                    [sys.executable, "-c", f"import {package}"],
                    capture_output=True,
                    cwd=self.project_root
                )
                if result.returncode == 0:
                    self.log(f"  {package} installed", "SUCCESS")
                    self.checks_passed += 1
                else:
                    self.log(f"  {package} NOT installed", "WARNING")
                    self.issues.append({
                        "type": "dependency",
                        "path": package,
                        "issue": "not installed",
                        "fix": f"pip install {package}"
                    })
                    all_installed = False
            except Exception:
                self.log(f"  {package} check failed", "WARNING")
                all_installed = False

        return all_installed

    def run_basic_test(self) -> bool:
        """Run a basic test to verify functionality."""
        self.log("Running basic functionality test...", "INFO")

        test_file = self.project_root / "tests" / "test_gsd_workflow.py"
        if not test_file.exists():
            self.log("  Test file not found - skipping", "WARNING")
            return False

        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", str(test_file), "-v", "--tb=short"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )

            if result.returncode == 0:
                # Count tests
                test_count = result.stdout.count(" PASSED")
                self.log(f"  {test_count} tests passed!", "SUCCESS")
                self.checks_passed += 1
                return True
            else:
                self.log("  Some tests failed", "WARNING")
                if self.verbose:
                    self.log(f"  Output: {result.stdout}", "DEBUG")
                return False
        except Exception as e:
            self.log(f"  Test execution failed: {e}", "ERROR")
            self.checks_failed += 1
            return False

    def check_documentation(self) -> bool:
        """Check if documentation exists."""
        self.log("Checking documentation...", "INFO")

        docs = [
            "docs/GSD_WORKFLOW_GUIDE.md",
            "docs/GSD_ORCHESTRATOR.md",
        ]

        all_exist = True
        for doc in docs:
            full_path = self.project_root / doc
            if full_path.exists():
                self.log(f"  {doc}", "SUCCESS")
                self.checks_passed += 1
            else:
                self.log(f"  {doc} - MISSING", "WARNING")
                self.issues.append({
                    "type": "file",
                    "path": doc,
                    "issue": "missing",
                    "fix": f"Copy from gsd_setup/{doc}"
                })

        return all_exist

    def generate_report(self) -> dict[str, object]:
        """Generate verification report."""
        return {
            "project_root": str(self.project_root),
            "checks_passed": self.checks_passed,
            "checks_failed": self.checks_failed,
            "total_checks": self.checks_passed + self.checks_failed,
            "status": "PASS" if self.checks_failed == 0 else "FAIL",
            "issues": self.issues,
        }

    def print_summary(self, report: dict[str, object]) -> None:
        """Print verification summary."""
        print("\n" + "="*60)
        print("📊 GSD SYSTEM VERIFICATION REPORT")
        print("="*60)

        print(f"\n📁 Project: {self.project_root}")
        print(f"✅ Passed: {report['checks_passed']}")
        print(f"❌ Failed: {report['checks_failed']}")
        print(f"📈 Total: {report['total_checks']}")

        if report['status'] == "PASS":
            print("\n🎉 Status: FULLY OPERATIONAL")
            print("\n✨ The GSD multi-agent system is ready to use!")
            print("\n💡 Next steps:")
            print("1. Try: python scripts/demo_orchestrator.py --all")
            print("2. Run: python scripts/demo_gsd_workflow.py --list-scenarios")
            print("3. Remember: OpenCode (MiniMax) is FREE - use it!")
        else:
            print("\n⚠️  Status: NEEDS ATTENTION")

            if report['issues']:
                print(f"\n🔧 Issues found ({len(report['issues'])}):")

                # Group by type
                by_type = {}
                for issue in report['issues']:
                    issue_type = issue['type']
                    if issue_type not in by_type:
                        by_type[issue_type] = []
                    by_type[issue_type].append(issue)

                for issue_type, items in by_type.items():
                    print(f"\n  {issue_type.upper()}:")
                    for item in items:
                        print(f"    - {item['path']}: {item['issue']}")
                        if self.verbose:
                            print(f"      Fix: {item['fix']}")

            print("\n📝 To fix issues:")
            print("1. Run: python gsd_setup/install.py --project-name YourProject")
            print("2. Or manually fix issues listed above")
            print("3. Then run this verification again")

    def attempt_fixes(self) -> bool:
        """Attempt to fix common issues automatically."""
        self.log("\n🔧 Attempting automatic fixes...", "INFO")

        fixed_count = 0
        for issue in self.issues:
            if issue['type'] == 'directory':
                # Create missing directory
                dir_path = self.project_root / issue['path']
                try:
                    dir_path.mkdir(parents=True, exist_ok=True)
                    self.log(f"  Created directory: {issue['path']}", "SUCCESS")
                    fixed_count += 1
                except Exception as e:
                    self.log(f"  Could not create {issue['path']}: {e}", "ERROR")

        self.log(f"\n✅ Fixed {fixed_count} issue(s)", "INFO")
        return fixed_count > 0

    def verify(self, fix: bool = False) -> bool:
        """Run complete verification.

        Args:
            fix: Attempt to fix issues automatically

        Returns:
            True if all checks pass, False otherwise
        """
        print("Verifying GSD Multi-Agent System Installation...")
        print("-" * 60)
        self.describe_plan()

        # Run all checks
        self.check_directories()
        self.check_core_files()
        self.check_source_files()
        self.check_test_files()
        self.check_scripts()
        self.check_configuration()
        self.check_imports()
        self.check_dependencies()
        self.check_documentation()
        self.run_basic_test()

        # Generate report
        report = self.generate_report()

        # Attempt fixes if requested
        if fix and report['issues']:
            if self.attempt_fixes():
                # Re-run verification after fixes
                self.log("\n🔄 Re-running verification after fixes...", "INFO")
                self.checks_passed = 0
                self.checks_failed = 0
                self.issues = []
                return self.verify(fix=False)

        # Print summary
        self.print_summary(report)

        # Save report
        report_path = self.project_root / "gsd_verification_report.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"\n📄 Report saved to: {report_path}")

        return report['status'] == "PASS"


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Verify GSD Multi-Agent System installation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Project root directory (default: current directory)"
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output"
    )

    parser.add_argument(
        "--fix",
        action="store_true",
        help="Attempt to fix common issues automatically"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug output"
    )

    args = parser.parse_args()

    if args.debug:
        args.verbose = True

    verifier = GSDVerifier(
        project_root=args.project_root,
        verbose=args.verbose
    )

    success = verifier.verify(fix=args.fix)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
