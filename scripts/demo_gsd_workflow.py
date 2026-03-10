#!/usr/bin/env python3
"""GSD Multi-Agent Workflow Demonstration Script.

This script demonstrates how to coordinate multiple agents for different tasks
using the GSD (Get Shit Done) workflow pattern.

Key Concepts Demonstrated:
- Task decomposition strategies
- Agent role assignment based on complexity and requirements
- Parallel execution patterns for maximum efficiency
- Result aggregation and coordination
- Error handling and logging

Usage:
    uv run python scripts/demo_gsd_workflow.py --scenario <scenario_name>
    uv run python scripts/demo_gsd_workflow.py --list-scenarios
    uv run python scripts/demo_gsd_workflow.py --scenario full-feature --verbose

License: MIT
"""

import argparse
import json
import logging
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

# Setup paths for imports
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Create a simple console logger for demo scripts."""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(levelname)s %(name)s: %(message)s"))
        logger.addHandler(handler)

    logger.propagate = False
    return logger


class AgentType(Enum):
    """Agent types based on antigravity/agent_policy.yaml."""

    OPUS = "claude-opus"
    SONNET = "claude-sonnet"
    HAIKU = "claude-haiku"
    CODEX = "openai-codex"
    OPENCODE = "minimax-opencode"
    GEMINI = "google-gemini"


class TaskComplexity(Enum):
    """Task complexity levels for agent assignment."""

    TRIVIAL = "trivial"
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    CRITICAL = "critical"


@dataclass
class Task:
    """Represents a single task in the workflow."""

    id: str
    description: str
    prompt: str
    complexity: TaskComplexity
    assigned_agent: AgentType
    dependencies: list[str] = field(default_factory=list)
    estimated_tokens: int = 0
    status: str = "pending"
    result: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert task to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "description": self.description,
            "prompt": self.prompt,
            "complexity": self.complexity.value,
            "assigned_agent": self.assigned_agent.value,
            "dependencies": self.dependencies,
            "estimated_tokens": self.estimated_tokens,
            "status": self.status,
            "result": self.result,
        }


@dataclass
class WorkflowResult:
    """Aggregated results from workflow execution."""

    scenario: str
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    total_tokens_estimated: int
    execution_start: datetime
    execution_end: datetime | None = None
    tasks: list[Task] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert result to dictionary for JSON serialization."""
        return {
            "scenario": self.scenario,
            "total_tasks": self.total_tasks,
            "completed_tasks": self.completed_tasks,
            "failed_tasks": self.failed_tasks,
            "total_tokens_estimated": self.total_tokens_estimated,
            "execution_start": self.execution_start.isoformat(),
            "execution_end": self.execution_end.isoformat() if self.execution_end else None,
            "tasks": [task.to_dict() for task in self.tasks],
        }


class AgentAssigner:
    """Assigns agents to tasks based on complexity and requirements."""

    @staticmethod
    def assign_agent(complexity: TaskComplexity, task_type: str) -> AgentType:
        """Assign appropriate agent based on task characteristics.

        Args:
            complexity: Task complexity level
            task_type: Type of task (e.g., 'architecture', 'implementation', 'tests')

        Returns:
            Assigned agent type
        """
        # Architecture and critical decisions
        if complexity == TaskComplexity.CRITICAL or task_type == "architecture":
            return AgentType.OPUS

        # Complex implementation or debugging
        if complexity == TaskComplexity.COMPLEX:
            if task_type in ["debugging", "security"]:
                return AgentType.OPUS
            return AgentType.CODEX

        # Moderate complexity - standard implementation
        if complexity == TaskComplexity.MODERATE:
            if task_type in ["implementation", "tests", "refactoring"]:
                return AgentType.CODEX
            if task_type == "documentation":
                return AgentType.OPENCODE
            return AgentType.SONNET

        # Simple tasks
        if complexity == TaskComplexity.SIMPLE:
            if task_type == "documentation":
                return AgentType.OPENCODE
            if task_type == "qa":
                return AgentType.GEMINI
            return AgentType.HAIKU

        # Trivial tasks - fastest agent
        return AgentType.HAIKU


class WorkflowOrchestrator:
    """Orchestrates multi-agent workflow execution."""

    def __init__(self, logger: logging.Logger) -> None:
        """Initialize the orchestrator.

        Args:
            logger: Logger instance for tracking execution
        """
        self.logger = logger
        self.assigner = AgentAssigner()

    def decompose_feature(self, feature_name: str) -> list[Task]:
        """Decompose a feature into tasks with appropriate agent assignments.

        Args:
            feature_name: Name of the feature to decompose

        Returns:
            List of tasks with assigned agents
        """
        self.logger.info(f"Decomposing feature: {feature_name}")

        tasks = [
            Task(
                id="arch-001",
                description="Define feature architecture and data models",
                prompt=f"Design the architecture for {feature_name} feature",
                complexity=TaskComplexity.CRITICAL,
                assigned_agent=self.assigner.assign_agent(TaskComplexity.CRITICAL, "architecture"),
                estimated_tokens=5000,
            ),
            Task(
                id="impl-001",
                description="Implement core feature logic",
                prompt=f"Implement the {feature_name} core logic based on architecture",
                complexity=TaskComplexity.COMPLEX,
                assigned_agent=self.assigner.assign_agent(TaskComplexity.COMPLEX, "implementation"),
                dependencies=["arch-001"],
                estimated_tokens=8000,
            ),
            Task(
                id="test-001",
                description="Write comprehensive test suite",
                prompt=f"Create tests for {feature_name} with >80% coverage",
                complexity=TaskComplexity.MODERATE,
                assigned_agent=self.assigner.assign_agent(TaskComplexity.MODERATE, "tests"),
                dependencies=["impl-001"],
                estimated_tokens=6000,
            ),
            Task(
                id="qa-001",
                description="Adversarial QA and edge case discovery",
                prompt=f"Test {feature_name} for edge cases and failure modes",
                complexity=TaskComplexity.SIMPLE,
                assigned_agent=self.assigner.assign_agent(TaskComplexity.SIMPLE, "qa"),
                dependencies=["test-001"],
                estimated_tokens=3000,
            ),
            Task(
                id="docs-001",
                description="Generate documentation",
                prompt=f"Create comprehensive documentation for {feature_name}",
                complexity=TaskComplexity.SIMPLE,
                assigned_agent=self.assigner.assign_agent(TaskComplexity.SIMPLE, "documentation"),
                dependencies=["impl-001"],
                estimated_tokens=2000,
            ),
        ]

        return tasks

    def identify_parallel_tasks(self, tasks: list[Task]) -> list[list[Task]]:
        """Identify tasks that can run in parallel.

        Args:
            tasks: List of all tasks in the workflow

        Returns:
            List of task waves (each wave can run in parallel)
        """
        # Build dependency map
        dep_map: dict[str, set[str]] = {}
        for task in tasks:
            dep_map[task.id] = set(task.dependencies)

        waves: list[list[Task]] = []
        remaining = set(task.id for task in tasks)

        while remaining:
            # Find tasks with no remaining dependencies
            wave_ids = {
                task_id for task_id in remaining if not dep_map[task_id].intersection(remaining)
            }

            if not wave_ids:
                self.logger.error("Circular dependency detected!")
                break

            # Create wave
            wave = [task for task in tasks if task.id in wave_ids]
            waves.append(wave)

            # Remove wave tasks from remaining
            remaining -= wave_ids

        return waves

    def execute_workflow(
        self, tasks: list[Task], scenario: str, dry_run: bool = True
    ) -> WorkflowResult:
        """Execute multi-agent workflow.

        Args:
            tasks: List of tasks to execute
            scenario: Scenario name for logging
            dry_run: If True, simulate execution without running agents

        Returns:
            Workflow execution results
        """
        result = WorkflowResult(
            scenario=scenario,
            total_tasks=len(tasks),
            completed_tasks=0,
            failed_tasks=0,
            total_tokens_estimated=sum(t.estimated_tokens for t in tasks),
            execution_start=datetime.now(),
            tasks=tasks,
        )

        self.logger.info(f"Starting workflow: {scenario}")
        self.logger.info(f"Total tasks: {len(tasks)}")
        self.logger.info(f"Estimated tokens: {result.total_tokens_estimated}")

        # Identify parallel execution waves
        waves = self.identify_parallel_tasks(tasks)
        self.logger.info(f"Execution waves: {len(waves)}")

        # Execute each wave
        for wave_num, wave in enumerate(waves, 1):
            self.logger.info(f"\n--- Wave {wave_num}: {len(wave)} parallel tasks ---")

            for task in wave:
                self.logger.info(
                    f"Task {task.id}: {task.description} [{task.assigned_agent.value}]"
                )

            if dry_run:
                # Simulate execution
                for task in wave:
                    task.status = "completed"
                    task.result = {
                        "simulated": True,
                        "agent": task.assigned_agent.value,
                        "tokens_used": task.estimated_tokens,
                    }
                    result.completed_tasks += 1
            else:
                # In real execution, this would spawn actual Task agents
                self.logger.warning(
                    "Real execution not implemented in demo. "
                    "Use Claude's Task tool directly in production."
                )

        result.execution_end = datetime.now()
        self.logger.info(f"\nWorkflow completed: {scenario}")

        return result


def scenario_full_feature(orchestrator: WorkflowOrchestrator) -> WorkflowResult:
    """Demonstrate full feature development workflow.

    Args:
        orchestrator: Workflow orchestrator instance

    Returns:
        Workflow execution results
    """
    tasks = orchestrator.decompose_feature("Analytics Dashboard")
    return orchestrator.execute_workflow(tasks, "full-feature")


def scenario_parallel_refactor(orchestrator: WorkflowOrchestrator) -> WorkflowResult:
    """Demonstrate parallel refactoring across multiple modules.

    Args:
        orchestrator: Workflow orchestrator instance

    Returns:
        Workflow execution results
    """
    tasks = [
        Task(
            id="refactor-001",
            description="Refactor storage module",
            prompt="Refactor storage layer for better performance",
            complexity=TaskComplexity.MODERATE,
            assigned_agent=orchestrator.assigner.assign_agent(
                TaskComplexity.MODERATE, "refactoring"
            ),
            estimated_tokens=5000,
        ),
        Task(
            id="refactor-002",
            description="Refactor clients module",
            prompt="Refactor API clients for consistency",
            complexity=TaskComplexity.MODERATE,
            assigned_agent=orchestrator.assigner.assign_agent(
                TaskComplexity.MODERATE, "refactoring"
            ),
            estimated_tokens=5000,
        ),
        Task(
            id="refactor-003",
            description="Refactor logging module",
            prompt="Refactor logging for better structure",
            complexity=TaskComplexity.SIMPLE,
            assigned_agent=orchestrator.assigner.assign_agent(TaskComplexity.SIMPLE, "refactoring"),
            estimated_tokens=3000,
        ),
    ]

    return orchestrator.execute_workflow(tasks, "parallel-refactor")


def scenario_doc_generation(orchestrator: WorkflowOrchestrator) -> WorkflowResult:
    """Demonstrate cost-optimized documentation generation.

    Args:
        orchestrator: Workflow orchestrator instance

    Returns:
        Workflow execution results
    """
    tasks = [
        Task(
            id="docs-api",
            description="Generate API documentation",
            prompt="Create API docs from docstrings",
            complexity=TaskComplexity.SIMPLE,
            assigned_agent=AgentType.OPENCODE,  # Free tier
            estimated_tokens=2000,
        ),
        Task(
            id="docs-guide",
            description="Generate user guide",
            prompt="Create user guide from README",
            complexity=TaskComplexity.SIMPLE,
            assigned_agent=AgentType.OPENCODE,  # Free tier
            estimated_tokens=2000,
        ),
        Task(
            id="docs-arch",
            description="Generate architecture docs",
            prompt="Document system architecture",
            complexity=TaskComplexity.MODERATE,
            assigned_agent=AgentType.SONNET,  # Needs understanding
            estimated_tokens=4000,
        ),
    ]

    return orchestrator.execute_workflow(tasks, "doc-generation")


def main() -> int:
    """Main entry point for the demonstration script.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    parser = argparse.ArgumentParser(
        description="Demonstrate GSD multi-agent workflow capabilities",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--scenario",
        choices=["full-feature", "parallel-refactor", "doc-generation"],
        help="Scenario to demonstrate",
    )

    parser.add_argument(
        "--list-scenarios",
        action="store_true",
        help="List available scenarios and exit",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Output file for results (JSON format)",
    )

    args = parser.parse_args()

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logger = setup_logger("gsd-demo", level=log_level)

    # List scenarios if requested
    if args.list_scenarios:
        print("\nAvailable Scenarios:")
        print("  full-feature       - Complete feature development workflow")
        print("  parallel-refactor  - Parallel refactoring across modules")
        print("  doc-generation     - Cost-optimized documentation generation")
        print("\nUsage:")
        print("  uv run python scripts/demo_gsd_workflow.py --scenario full-feature")
        return 0

    # Require scenario selection
    if not args.scenario:
        parser.error("--scenario is required (or use --list-scenarios)")

    try:
        # Initialize orchestrator
        orchestrator = WorkflowOrchestrator(logger)

        # Execute selected scenario
        scenario_map = {
            "full-feature": scenario_full_feature,
            "parallel-refactor": scenario_parallel_refactor,
            "doc-generation": scenario_doc_generation,
        }

        result = scenario_map[args.scenario](orchestrator)

        # Display summary
        logger.info("\n" + "=" * 80)
        logger.info("WORKFLOW SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Scenario: {result.scenario}")
        logger.info(f"Total tasks: {result.total_tasks}")
        logger.info(f"Completed: {result.completed_tasks}")
        logger.info(f"Failed: {result.failed_tasks}")
        logger.info(f"Estimated tokens: {result.total_tokens_estimated}")

        # Agent distribution
        agent_counts: dict[str, int] = {}
        for task in result.tasks:
            agent = task.assigned_agent.value
            agent_counts[agent] = agent_counts.get(agent, 0) + 1

        logger.info("\nAgent Distribution:")
        for agent, count in sorted(agent_counts.items()):
            logger.info(f"  {agent}: {count} tasks")

        # Save results if output file specified
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with open(args.output, "w") as f:
                json.dump(result.to_dict(), f, indent=2)
            logger.info(f"\nResults saved to: {args.output}")

        return 0

    except Exception as e:
        logger.error(f"Error executing workflow: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
