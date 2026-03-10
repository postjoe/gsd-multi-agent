#!/usr/bin/env python3
"""
GSD Multi-Agent System - Universal Installation Script

This script automates the setup of the GSD workflow system in any project.
It handles directory creation, file copying, dependency installation, and verification.

Usage:
    python gsd_setup/install.py --project-name "YourProject"
    python gsd_setup/install.py --project-name "YourProject" --skip-tests
    python gsd_setup/install.py --dry-run

Behavior:
    - Writes scaffold files inside the selected project root only
    - Optionally installs pinned dependencies from gsd_requirements.txt
    - Optionally runs the local GSD test file after installation
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path


class InstallationSecurityError(RuntimeError):
    """Raised when the installer detects an unsafe destination path."""


class GSDInstaller:
    """Installer for GSD multi-agent workflow system."""

    def __init__(self, project_root: Path, project_name: str, dry_run: bool = False):
        """Initialize installer.

        Args:
            project_root: Root directory of the target project
            project_name: Name of the project being configured
            dry_run: If True, show what would be done without doing it
        """
        self.project_root = project_root
        self.project_name = project_name
        self.dry_run = dry_run
        self.gsd_setup_dir = Path(__file__).parent
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def _resolved_project_root(self) -> Path:
        """Return the canonical project root used for boundary checks."""
        return self.project_root.resolve()

    def _ensure_path_is_safe(self, path: Path) -> None:
        """Reject writes that resolve outside the requested project root."""
        project_root = self._resolved_project_root()

        try:
            resolved_parent = path.parent.resolve()
            resolved_parent.relative_to(project_root)
        except ValueError as exc:
            raise InstallationSecurityError(
                f"Refusing to write outside project root: {path}"
            ) from exc

        if path.exists():
            if path.is_symlink():
                raise InstallationSecurityError(f"Refusing to overwrite symlink: {path}")
            try:
                path.resolve().relative_to(project_root)
            except ValueError as exc:
                raise InstallationSecurityError(
                    f"Refusing to overwrite path outside project root: {path}"
                ) from exc

    def _write_text_file(self, path: Path, content: str) -> None:
        """Safely write UTF-8 text inside the target project root."""
        self._ensure_path_is_safe(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def log(self, message: str, level: str = "INFO") -> None:
        """Log a message with level indicator."""
        prefix = {
            "INFO": "ℹ️ ",
            "SUCCESS": "✅",
            "WARNING": "⚠️ ",
            "ERROR": "❌",
            "SKIP": "⏭️ "
        }.get(level, "")
        print(f"{prefix} {message}")

    def describe_plan(self) -> None:
        """Print the actions this installer will take."""
        self.log(f"Target project root: {self.project_root}", "INFO")
        self.log("Writes are restricted to the selected project root.", "INFO")
        self.log("Dependency installation is optional and uses pinned versions.", "INFO")
        self.log("Local tests may run unless --skip-tests is set.", "INFO")

    def create_directories(self) -> None:
        """Create required project directories."""
        directories = [
            ".claude",
            "antigravity",
            "scripts",
            "tests",
            "docs",
            "src",
        ]

        for dir_name in directories:
            dir_path = self.project_root / dir_name
            if dir_path.exists():
                self.log(f"Directory exists: {dir_name}", "SKIP")
            else:
                if not self.dry_run:
                    self._ensure_path_is_safe(dir_path)
                    dir_path.mkdir(parents=True, exist_ok=True)
                self.log(f"Created directory: {dir_name}", "SUCCESS")

    def copy_template_files(self) -> None:
        """Copy template files to project."""
        templates = {
            "templates/.claude/settings.local.json": ".claude/settings.local.json",
            "templates/antigravity/agent_policy.yaml": "antigravity/agent_policy.yaml",
            "templates/skills-lock.json": "skills-lock.json",
            "templates/CLAUDE.md": "CLAUDE.md",
            "templates/TASK_TOOL_CAPABILITY.md": "TASK_TOOL_CAPABILITY.md",
        }

        for source, dest in templates.items():
            source_path = self.gsd_setup_dir / source
            dest_path = self.project_root / dest

            if dest_path.exists():
                self.log(f"File exists: {dest}", "WARNING")
                self.warnings.append(f"Skipped existing file: {dest}")
            else:
                if not self.dry_run:
                    # Ensure parent directory exists
                    self._ensure_path_is_safe(dest_path)
                    dest_path.parent.mkdir(parents=True, exist_ok=True)

                    # Read template and customize
                    if source_path.exists():
                        content = source_path.read_text(encoding="utf-8")
                        # Replace placeholders
                        content = content.replace("{{PROJECT_NAME}}", self.project_name)
                        content = content.replace("{{PROJECT_PATH}}", str(self.project_root))
                        self._write_text_file(dest_path, content)
                    else:
                        # If template doesn't exist, create from embedded content
                        self._create_template_from_embedded(dest_path, Path(source).name)

                self.log(f"Installed: {dest}", "SUCCESS")

    def _create_template_from_embedded(self, dest_path: Path, template_name: str) -> None:
        """Create template from embedded content when file doesn't exist."""
        embedded_templates = {
            "settings.local.json": self._get_claude_settings(),
            "agent_policy.yaml": self._get_agent_policy(),
            "skills-lock.json": self._get_skills_lock(),
            "CLAUDE.md": self._get_claude_instructions(),
            "TASK_TOOL_CAPABILITY.md": self._get_task_capability_doc(),
        }

        content = embedded_templates.get(template_name, "")
        if content and not self.dry_run:
            self._write_text_file(dest_path, content)

    def _get_claude_settings(self) -> str:
        """Get default Claude settings."""
        settings = {
            "permissions": {
                "allow": [
                    "Bash(uv run pytest tests/ -v --tb=short)",
                    "Bash(uv run ruff check .)",
                    "Bash(uv run ruff format .)",
                    "Bash(uv run mypy src/ --ignore-missing-imports)",
                    "Bash(python gsd_setup/verify.py)",
                ],
                "deny": [],
                "ask": []
            }
        }
        return json.dumps(settings, indent=2)

    def _get_agent_policy(self) -> str:
        """Get default agent policy configuration."""
        return """project: {{PROJECT_NAME}}
model:
  # OpenCode/MiniMax - FREE tier (USE THIS!)
  opencode:
    lane: free_tier_optimization
    cost_per_1k: 0.00  # FREE!
    use_for:
      - documentation_generation
      - simple_refactoring
      - basic_implementation
      - readme_updates
      - code_comments
      - changelog_updates

  # Claude variants
  claude:
    opus:
      lane: architecture_and_hard_problems
      cost_per_1k: 0.015
      use_for:
        - complex_architecture_decisions
        - difficult_debugging
        - novel_algorithm_design
        - critical_security_review
    sonnet:
      lane: coordination_and_general_review
      cost_per_1k: 0.003
      use_for:
        - cross_agent_orchestration
        - spec_review
        - risk_analysis
        - general_code_review
    haiku:
      lane: fast_iteration_and_simple_tasks
      cost_per_1k: 0.001
      use_for:
        - quick_file_operations
        - simple_checks
        - fast_iteration
        - low_complexity_tasks

  # OpenAI Codex
  codex:
    lane: implementation_and_tests
    cost_per_1k: 0.002
    use_for:
      - feature_implementation
      - test_writing
      - refactoring
      - complex_implementation

  # Google Gemini
  gemini:
    lane: adversarial_qa
    cost_per_1k: 0.0025
    use_for:
      - edge_case_discovery
      - adversarial_testing
      - breaking_assumptions
      - stress_testing

task_rules:
  # Always prioritize FREE tier (OpenCode) when possible
  optimization_priority:
    - opencode  # FREE - use first!
    - haiku     # Cheapest paid
    - codex     # Implementation
    - gemini    # QA
    - sonnet    # Coordination
    - opus      # Only when critical

quality_gates:
  lint:
    - "uv run ruff check ."
    - "uv run ruff format --check ."
  typing:
    - "uv run mypy src --ignore-missing-imports"
  tests:
    - "uv run pytest tests/ -v"
"""

    def _get_skills_lock(self) -> str:
        """Get default skills configuration."""
        skills = {
            "version": 1,
            "skills": {
                "gsd": {
                    "source": "ctsstc/get-shit-done-skills",
                    "sourceType": "github",
                    "computedHash": (
                        "680208c668bd9ce5135c2b6b21c200406ef04a45450b3246adb3a573f11ab40c"
                    ),
                },
                "find-skills": {
                    "source": "vercel-labs/skills",
                    "sourceType": "github",
                    "computedHash": (
                        "25872a21881a950edc3db1f3329664d60405d539660ce05b3265db2de06a7dfd"
                    ),
                },
            }
        }
        return json.dumps(skills, indent=2)

    def _get_claude_instructions(self) -> str:
        """Get project-specific Claude instructions."""
        return f"""# {self.project_name} - Claude Instructions

## GSD Multi-Agent Workflow

This project uses the GSD (Get Shit Done) multi-agent workflow system.

### Key Points

1. **USE OPENCODE (MiniMax) FOR FREE TIER**
   - Documentation = OpenCode (FREE)
   - Simple refactoring = OpenCode (FREE)
   - Basic tasks = OpenCode (FREE)
   - This saves significant costs!

2. **Parallel Execution**
   - Multiple Task tools in ONE message = parallel
   - Proven with 3 agents, 2,940+ lines of code

3. **Cost Optimization Priority**
   - OpenCode (FREE) > Haiku > Codex > Gemini > Sonnet > Opus
   - Always optimize for lowest cost tier

4. **Task Tool Usage**
   ```python
   Task(
       description="Short description",
       prompt="Detailed instructions",
       subagent_type="general-purpose"
   )
   ```

See TASK_TOOL_CAPABILITY.md for details.
See docs/GSD_WORKFLOW_GUIDE.md for complete guide.
"""

    def _get_task_capability_doc(self) -> str:
        """Get Task tool capability documentation."""
        return """# Task Tool Capability Reference

## Critical: Claude CAN Use Multi-Agent Workflows

The Task tool enables parallel multi-agent execution in Claude Code.

## Supported Capabilities
- Parallel task delegation
- Documentation and implementation splits
- Test and verification workflows
- Cost-aware model routing

## Usage Pattern

### Single Agent
```python
Task(
    description="Implement feature",
    prompt="Detailed specs...",
    subagent_type="general-purpose"
)
```

### Parallel Agents (call in ONE message)
```python
Task(description="Task A", prompt="...", subagent_type="general-purpose")
Task(description="Task B", prompt="...", subagent_type="general-purpose")
Task(description="Task C", prompt="...", subagent_type="general-purpose")
```

## Remember
- OpenCode (MiniMax) is FREE - use it!
- Multiple Task calls in ONE message = parallel
- The capability is PROVEN and WORKING
"""

    def copy_source_files(self) -> None:
        """Copy source code files."""
        files_to_copy = {
            "src/gsd_orchestrator.py": "src/gsd_orchestrator.py",
            "tests/test_gsd_workflow.py": "tests/test_gsd_workflow.py",
            "tests/test_gsd_orchestrator.py": "tests/test_gsd_orchestrator.py",
            "scripts/demo_gsd_workflow.py": "scripts/demo_gsd_workflow.py",
            "scripts/demo_orchestrator.py": "scripts/demo_orchestrator.py",
            "scripts/validate_gsd_system.py": "scripts/validate_gsd_system.py",
            "docs/GSD_WORKFLOW_GUIDE.md": "docs/GSD_WORKFLOW_GUIDE.md",
            "docs/GSD_ORCHESTRATOR.md": "docs/GSD_ORCHESTRATOR.md",
        }

        for source, dest in files_to_copy.items():
            source_path = self.gsd_setup_dir / source
            dest_path = self.project_root / dest

            if dest_path.exists():
                self.log(f"File exists: {dest}", "WARNING")
            else:
                if not self.dry_run:
                    self._ensure_path_is_safe(dest_path)
                    dest_path.parent.mkdir(parents=True, exist_ok=True)

                    # For actual files that exist in gsd_setup
                    if source_path.exists():
                        content = source_path.read_text(encoding="utf-8")
                        self._write_text_file(dest_path, content)
                        self.log(f"Installed: {dest}", "SUCCESS")
                    else:
                        self.log(f"Source not found: {source}", "WARNING")
                        self.warnings.append(f"Missing source: {source}")

    def create_requirements(self) -> None:
        """Create requirements file if needed."""
        requirements_path = self.project_root / "gsd_requirements.txt"

        requirements = """# GSD Multi-Agent System Requirements
pytest==8.3.3
pytest-cov==5.0.0
ruff==0.6.8
mypy==1.11.2
pyyaml==6.0.2
"""

        if not self.dry_run:
            self._write_text_file(requirements_path, requirements)
        self.log("Created gsd_requirements.txt", "SUCCESS")

    def install_dependencies(self, skip: bool = False) -> None:
        """Install Python dependencies."""
        if skip:
            self.log("Skipping dependency installation", "SKIP")
            return

        self.log("Installing dependencies...", "INFO")

        if not self.dry_run:
            # Try uv first, fall back to pip
            try:
                subprocess.run(
                    ["uv", "pip", "install", "-r", "gsd_requirements.txt"],
                    cwd=self.project_root,
                    check=True,
                    capture_output=True
                )
                self.log("Dependencies installed with uv", "SUCCESS")
            except (subprocess.CalledProcessError, FileNotFoundError):
                try:
                    subprocess.run(
                        [sys.executable, "-m", "pip", "install", "-r", "gsd_requirements.txt"],
                        cwd=self.project_root,
                        check=True,
                        capture_output=True
                    )
                    self.log("Dependencies installed with pip", "SUCCESS")
                except subprocess.CalledProcessError as e:
                    self.errors.append(f"Failed to install dependencies: {e}")
                    self.log("Failed to install dependencies", "ERROR")

    def run_tests(self, skip: bool = False) -> None:
        """Run tests to verify installation."""
        if skip:
            self.log("Skipping tests", "SKIP")
            return

        self.log("Running verification tests...", "INFO")

        if not self.dry_run:
            test_file = self.project_root / "tests" / "test_gsd_workflow.py"
            if test_file.exists():
                try:
                    result = subprocess.run(
                        [sys.executable, "-m", "pytest", str(test_file), "-v"],
                        cwd=self.project_root,
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        self.log("All tests passed!", "SUCCESS")
                    else:
                        self.warnings.append("Some tests failed - check configuration")
                        self.log("Tests completed with warnings", "WARNING")
                except Exception as e:
                    self.warnings.append(f"Could not run tests: {e}")
                    self.log("Could not run tests", "WARNING")
            else:
                self.log("Test file not found", "WARNING")

    def create_example_config(self) -> None:
        """Create example configuration file."""
        config_path = self.project_root / "gsd_config.yaml"

        config = f"""# GSD Configuration for {self.project_name}

project:
  name: "{self.project_name}"
  type: "general"  # web_app, library, cli, api, etc.

priorities:
  cost_optimization: high  # Maximize OpenCode (FREE) usage
  parallel_execution: medium
  quality_gates: high

agent_preferences:
  documentation: opencode  # FREE!
  simple_tasks: opencode   # FREE!
  implementation: codex
  architecture: opus
  qa: gemini
  coordination: sonnet

task_defaults:
  test_coverage_min: 80
  documentation_required: true
  review_required: true

# Cost thresholds (per workflow)
cost_limits:
  warning_threshold: 0.10  # Warn if cost > $0.10
  error_threshold: 1.00    # Error if cost > $1.00
"""

        if not config_path.exists():
            if not self.dry_run:
                self._write_text_file(config_path, config)
            self.log("Created gsd_config.yaml", "SUCCESS")
        else:
            self.log("Config exists: gsd_config.yaml", "SKIP")

    def print_summary(self) -> None:
        """Print installation summary."""
        print("\n" + "="*60)
        print("🎉 GSD MULTI-AGENT SYSTEM INSTALLATION COMPLETE")
        print("="*60)

        if self.dry_run:
            print("\n⚠️  DRY RUN - No changes were made")

        print(f"\n📦 Project: {self.project_name}")
        print(f"📁 Location: {self.project_root}")

        if self.errors:
            print(f"\n❌ Errors: {len(self.errors)}")
            for error in self.errors:
                print(f"  - {error}")

        if self.warnings:
            print(f"\n⚠️  Warnings: {len(self.warnings)}")
            for warning in self.warnings:
                print(f"  - {warning}")

        print("\n✅ Next Steps:")
        print("1. Review .claude/settings.local.json before approving agent commands")
        print("2. Review gsd_config.yaml and customize for your project")
        print("3. Update CLAUDE.md with project-specific context")
        print("4. Run: python gsd_setup/verify.py")
        print("\n💡 Remember: OpenCode (MiniMax) is FREE - use it extensively!")

    def install(self, skip_deps: bool = False, skip_tests: bool = False) -> bool:
        """Run complete installation.

        Args:
            skip_deps: Skip dependency installation
            skip_tests: Skip test execution

        Returns:
            True if successful, False otherwise
        """
        try:
            self.log(f"Installing GSD system for {self.project_name}...", "INFO")
            self.describe_plan()

            self.create_directories()
            self.copy_template_files()
            self.copy_source_files()
            self.create_requirements()
            self.install_dependencies(skip_deps)
            self.create_example_config()
            self.run_tests(skip_tests)

            self.print_summary()

            return len(self.errors) == 0

        except Exception as e:
            self.log(f"Installation failed: {e}", "ERROR")
            self.errors.append(str(e))
            return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Install GSD Multi-Agent System in your project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        "--project-name",
        required=True,
        help="Name of your project"
    )

    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Project root directory (default: current directory)"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without doing it"
    )

    parser.add_argument(
        "--skip-deps",
        action="store_true",
        help="Skip dependency installation"
    )

    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip test execution"
    )

    args = parser.parse_args()

    installer = GSDInstaller(
        project_root=args.project_root,
        project_name=args.project_name,
        dry_run=args.dry_run
    )

    success = installer.install(
        skip_deps=args.skip_deps,
        skip_tests=args.skip_tests
    )

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
