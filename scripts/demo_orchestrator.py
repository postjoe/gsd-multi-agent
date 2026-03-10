#!/usr/bin/env python3
"""Demonstration of GSD Orchestrator capabilities.

This script showcases the GSDOrchestrator class with real examples of:
- Cost-optimized task distribution
- Parallel execution wave identification
- Token cost calculation
- Agent assignment strategies
- Workflow reporting

Usage:
    uv run python scripts/demo_orchestrator.py
    uv run python scripts/demo_orchestrator.py --feature "API Integration"
    uv run python scripts/demo_orchestrator.py --compare-costs

License: MIT
"""

import argparse
import sys
from pathlib import Path

# Add src to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from gsd_orchestrator import (  # noqa: E402
    AgentType,
    GSDOrchestrator,
    Task,
    TaskComplexity,
)


def demo_basic_workflow() -> None:
    """Demonstrate basic workflow creation and optimization."""
    print("\n" + "=" * 80)
    print("DEMO: Basic Workflow with Cost Optimization")
    print("=" * 80)

    orchestrator = GSDOrchestrator()

    # Create tasks with suboptimal assignments
    tasks = [
        Task(
            id="doc-001",
            description="Write API documentation",
            prompt="Generate comprehensive API documentation",
            complexity=TaskComplexity.SIMPLE,
            assigned_agent=AgentType.SONNET,  # Suboptimal - costs money
            estimated_tokens=3000,
        ),
        Task(
            id="impl-001",
            description="Implement authentication",
            prompt="Build JWT authentication system",
            complexity=TaskComplexity.COMPLEX,
            assigned_agent=AgentType.HAIKU,  # Suboptimal - too simple
            estimated_tokens=8000,
        ),
        Task(
            id="test-001",
            description="Write unit tests",
            prompt="Create comprehensive test suite",
            complexity=TaskComplexity.MODERATE,
            assigned_agent=AgentType.OPUS,  # Suboptimal - too expensive
            dependencies=["impl-001"],
            estimated_tokens=5000,
        ),
    ]

    # Add tasks
    for task in tasks:
        orchestrator.add_task(task)

    print(f"\nCreated {len(tasks)} tasks")
    print("\nBEFORE OPTIMIZATION:")
    print(f"  Total cost: ${orchestrator.calculate_token_costs():.4f}")

    # Show agent distribution before
    before_agents = {}
    for task in orchestrator.tasks:
        agent = task.assigned_agent.value
        before_agents[agent] = before_agents.get(agent, 0) + 1
    print("  Agent distribution:")
    for agent, count in before_agents.items():
        print(f"    {agent}: {count}")

    # Optimize
    print("\n>>> Running optimization...")
    orchestrator.optimize_task_distribution()

    print("\nAFTER OPTIMIZATION:")
    print(f"  Total cost: ${orchestrator.calculate_token_costs():.4f}")

    # Show agent distribution after
    after_agents = {}
    for task in orchestrator.tasks:
        agent = task.assigned_agent.value
        after_agents[agent] = after_agents.get(agent, 0) + 1
    print("  Agent distribution:")
    for agent, count in after_agents.items():
        is_free = " (FREE!)" if orchestrator.costs.is_free(AgentType(agent)) else ""
        print(f"    {agent}: {count}{is_free}")


def demo_parallel_execution() -> None:
    """Demonstrate parallel execution wave identification."""
    print("\n" + "=" * 80)
    print("DEMO: Parallel Execution Wave Identification")
    print("=" * 80)

    orchestrator = GSDOrchestrator()

    # Create tasks with dependencies
    tasks = [
        Task(
            id="setup-1",
            description="Setup database",
            prompt="Initialize database schema",
            complexity=TaskComplexity.MODERATE,
            assigned_agent=AgentType.CODEX,
            estimated_tokens=3000,
        ),
        Task(
            id="setup-2",
            description="Setup cache",
            prompt="Configure Redis cache",
            complexity=TaskComplexity.SIMPLE,
            assigned_agent=AgentType.HAIKU,
            estimated_tokens=2000,
        ),
        Task(
            id="impl-1",
            description="Implement users module",
            prompt="Build user management",
            complexity=TaskComplexity.COMPLEX,
            assigned_agent=AgentType.CODEX,
            dependencies=["setup-1"],
            estimated_tokens=5000,
        ),
        Task(
            id="impl-2",
            description="Implement auth module",
            prompt="Build authentication",
            complexity=TaskComplexity.COMPLEX,
            assigned_agent=AgentType.CODEX,
            dependencies=["setup-1"],
            estimated_tokens=5000,
        ),
        Task(
            id="impl-3",
            description="Implement API endpoints",
            prompt="Build REST API",
            complexity=TaskComplexity.MODERATE,
            assigned_agent=AgentType.CODEX,
            dependencies=["impl-1", "impl-2"],
            estimated_tokens=4000,
        ),
        Task(
            id="docs-1",
            description="Write documentation",
            prompt="Document the API",
            complexity=TaskComplexity.SIMPLE,
            assigned_agent=AgentType.OPENCODE,
            dependencies=["impl-3"],
            estimated_tokens=3000,
        ),
    ]

    for task in tasks:
        orchestrator.add_task(task)

    # Identify parallel waves
    print(f"\nAnalyzing {len(tasks)} tasks for parallel execution...")
    waves = orchestrator.identify_parallel_tasks()

    print(f"\nIdentified {len(waves)} execution waves:")
    for i, wave in enumerate(waves, 1):
        print(f"\n  Wave {i}: {len(wave)} parallel tasks")
        for task in wave:
            print(f"    - {task.id}: {task.description}")

    print("\n>>> Parallel execution strategy:")
    print("  Call multiple Task tools in ONE message for parallel execution")
    print("  Example:")
    print('    Task(description="Task 1", prompt="...", subagent_type="general-purpose")')
    print('    Task(description="Task 2", prompt="...", subagent_type="general-purpose")')
    print('    Task(description="Task 3", prompt="...", subagent_type="general-purpose")')


def demo_feature_decomposition(feature_name: str) -> None:
    """Demonstrate feature decomposition into tasks."""
    print("\n" + "=" * 80)
    print(f"DEMO: Feature Decomposition - {feature_name}")
    print("=" * 80)

    orchestrator = GSDOrchestrator()
    tasks = orchestrator.decompose_feature(feature_name)

    print(f"\nDecomposed '{feature_name}' into {len(tasks)} tasks:")
    for task in tasks:
        print(f"\n  Task: {task.id}")
        print(f"    Description: {task.description}")
        print(f"    Complexity: {task.complexity.value}")
        print(f"    Agent: {task.assigned_agent.value}")
        print(f"    Estimated tokens: {task.estimated_tokens}")
        if task.dependencies:
            print(f"    Dependencies: {', '.join(task.dependencies)}")

    # Generate report
    report = orchestrator.generate_workflow_report(feature_name)
    print(f"\n{'-' * 80}")
    print("WORKFLOW REPORT")
    print(f"{'-' * 80}")
    print(f"Feature: {report.workflow_name}")
    print(f"Total tasks: {report.total_tasks}")
    print(f"Total tokens: {report.total_tokens}")
    print(f"Total cost: ${report.total_cost:.4f}")
    print(f"Cost savings vs. baseline: ${report.cost_savings:.4f}")
    print("\nAgent distribution:")
    for agent, count in sorted(report.agent_distribution.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / report.total_tasks) * 100
        is_free = " (FREE!)" if orchestrator.costs.is_free(agent) else ""
        print(f"  {agent.value}: {count} ({percentage:.1f}%){is_free}")


def demo_cost_comparison() -> None:
    """Demonstrate cost comparison between different strategies."""
    print("\n" + "=" * 80)
    print("DEMO: Cost Comparison - FREE vs PAID Strategies")
    print("=" * 80)

    # Strategy 1: All Sonnet (expensive)
    print("\nStrategy 1: All Sonnet (EXPENSIVE)")
    orchestrator1 = GSDOrchestrator()
    for i in range(10):
        orchestrator1.add_task(
            Task(
                id=f"task-{i}",
                description=f"Documentation task {i}",
                prompt=f"Write docs {i}",
                complexity=TaskComplexity.SIMPLE,
                assigned_agent=AgentType.SONNET,
                estimated_tokens=2000,
            )
        )
    cost1 = orchestrator1.calculate_token_costs()
    print(f"  Total cost: ${cost1:.4f}")

    # Strategy 2: Optimized (FREE)
    print("\nStrategy 2: Optimized with OpenCode (FREE)")
    orchestrator2 = GSDOrchestrator()
    for i in range(10):
        orchestrator2.add_task(
            Task(
                id=f"task-{i}",
                description=f"Documentation task {i}",
                prompt=f"Write docs {i}",
                complexity=TaskComplexity.SIMPLE,
                assigned_agent=AgentType.SONNET,  # Will be optimized
                estimated_tokens=2000,
            )
        )
    orchestrator2.optimize_task_distribution()
    cost2 = orchestrator2.calculate_token_costs()
    print(f"  Total cost: ${cost2:.4f}")

    # Comparison
    savings = cost1 - cost2
    savings_pct = (savings / cost1 * 100) if cost1 > 0 else 0
    print(f"\n{'=' * 80}")
    print("COST COMPARISON RESULTS")
    print(f"{'=' * 80}")
    print(f"Expensive strategy: ${cost1:.4f}")
    print(f"Optimized strategy: ${cost2:.4f}")
    print(f"Savings: ${savings:.4f} ({savings_pct:.1f}%)")
    print("\n>>> KEY INSIGHT: OpenCode (MiniMax M2.5) is FREE!")
    print("    Use it for documentation, simple refactoring, and basic tasks")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Demonstrate GSD Orchestrator capabilities",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--feature",
        help="Feature name for decomposition demo",
        default="User Authentication",
    )

    parser.add_argument(
        "--compare-costs",
        action="store_true",
        help="Show cost comparison demo",
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all demos",
    )

    args = parser.parse_args()

    try:
        if args.all:
            demo_basic_workflow()
            demo_parallel_execution()
            demo_feature_decomposition(args.feature)
            demo_cost_comparison()
        elif args.compare_costs:
            demo_cost_comparison()
        else:
            demo_basic_workflow()
            demo_parallel_execution()
            demo_feature_decomposition(args.feature)

        print("\n" + "=" * 80)
        print("DEMO COMPLETE")
        print("=" * 80)
        print("\nKey Takeaways:")
        print("  1. OpenCode (MiniMax M2.5) is FREE - maximize its use!")
        print("  2. Parallel execution = multiple Task tools in one message")
        print("  3. Optimization can save significant costs (often 100%!)")
        print("  4. Agent assignment should match task complexity")
        print("\n")

        return 0

    except Exception as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
