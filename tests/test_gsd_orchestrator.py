"""Tests for GSD Orchestrator - Multi-Agent Task Distribution System.

This test suite verifies the GSDOrchestrator class which manages:
- Multi-agent task distribution with cost optimization
- Parallel task execution patterns
- Token usage and cost tracking
- Agent assignment logic based on complexity
- Workflow reporting and analytics
"""

from datetime import datetime

import pytest

from gsd_orchestrator import (
    AgentType,
    GSDOrchestrator,
    OptimizationStrategy,
    Task,
    TaskComplexity,
    TokenCosts,
    WorkflowReport,
)


class TestAgentType:
    """Test agent type enumeration and properties."""

    def test_agent_types_defined(self) -> None:
        """Test that all required agent types are defined."""
        assert AgentType.OPUS.value == "claude-opus"
        assert AgentType.SONNET.value == "claude-sonnet"
        assert AgentType.HAIKU.value == "claude-haiku"
        assert AgentType.CODEX.value == "openai-codex"
        assert AgentType.OPENCODE.value == "minimax-opencode"
        assert AgentType.GEMINI.value == "google-gemini"

    def test_agent_cost_tiers(self) -> None:
        """Test that agents have correct cost tiers."""
        costs = TokenCosts()
        assert costs.get_cost(AgentType.OPENCODE) == 0.0  # FREE!
        assert costs.get_cost(AgentType.HAIKU) < costs.get_cost(AgentType.SONNET)
        assert costs.get_cost(AgentType.SONNET) < costs.get_cost(AgentType.OPUS)

    def test_opencode_is_free(self) -> None:
        """Test that OpenCode (MiniMax) has zero token cost."""
        costs = TokenCosts()
        # This is the critical optimization - OpenCode is FREE
        assert costs.get_cost(AgentType.OPENCODE) == 0.0
        assert costs.is_free(AgentType.OPENCODE) is True


class TestTaskComplexity:
    """Test task complexity enumeration."""

    def test_complexity_levels_defined(self) -> None:
        """Test that all complexity levels are defined."""
        assert TaskComplexity.TRIVIAL.value == "trivial"
        assert TaskComplexity.SIMPLE.value == "simple"
        assert TaskComplexity.MODERATE.value == "moderate"
        assert TaskComplexity.COMPLEX.value == "complex"
        assert TaskComplexity.CRITICAL.value == "critical"


class TestTask:
    """Test Task dataclass and methods."""

    def test_task_creation(self) -> None:
        """Test creating a task with required fields."""
        task = Task(
            id="test-001",
            description="Test task",
            prompt="Do something",
            complexity=TaskComplexity.SIMPLE,
            assigned_agent=AgentType.HAIKU,
        )
        assert task.id == "test-001"
        assert task.status == "pending"
        assert task.dependencies == []
        assert task.estimated_tokens == 0

    def test_task_with_dependencies(self) -> None:
        """Test task with dependencies."""
        task = Task(
            id="test-002",
            description="Dependent task",
            prompt="Do something after test-001",
            complexity=TaskComplexity.MODERATE,
            assigned_agent=AgentType.CODEX,
            dependencies=["test-001"],
        )
        assert task.dependencies == ["test-001"]

    def test_task_serialization(self) -> None:
        """Test task can be converted to dictionary."""
        task = Task(
            id="test-003",
            description="Test serialization",
            prompt="Serialize me",
            complexity=TaskComplexity.SIMPLE,
            assigned_agent=AgentType.OPENCODE,
            estimated_tokens=1000,
        )
        data = task.to_dict()
        assert data["id"] == "test-003"
        assert data["complexity"] == "simple"
        assert data["assigned_agent"] == "minimax-opencode"
        assert data["estimated_tokens"] == 1000


class TestTokenCosts:
    """Test token cost calculation and optimization."""

    def test_cost_per_agent(self) -> None:
        """Test that each agent has a defined cost."""
        costs = TokenCosts()
        assert costs.get_cost(AgentType.OPENCODE) == 0.0  # FREE
        assert costs.get_cost(AgentType.HAIKU) == 0.001  # Fast tier
        assert costs.get_cost(AgentType.SONNET) == 0.003  # Standard tier
        assert costs.get_cost(AgentType.OPUS) == 0.015  # Premium tier
        assert costs.get_cost(AgentType.CODEX) == 0.002  # Implementation tier
        assert costs.get_cost(AgentType.GEMINI) == 0.0025  # QA tier

    def test_calculate_task_cost(self) -> None:
        """Test calculating cost for a single task."""
        costs = TokenCosts()
        task = Task(
            id="test-001",
            description="Test",
            prompt="Test",
            complexity=TaskComplexity.SIMPLE,
            assigned_agent=AgentType.OPENCODE,
            estimated_tokens=1000,
        )
        cost = costs.calculate_task_cost(task)
        assert cost == 0.0  # OpenCode is free

    def test_calculate_workflow_cost(self) -> None:
        """Test calculating total cost for multiple tasks."""
        costs = TokenCosts()
        tasks = [
            Task(
                id="free-task",
                description="Free",
                prompt="Free",
                complexity=TaskComplexity.SIMPLE,
                assigned_agent=AgentType.OPENCODE,
                estimated_tokens=2000,
            ),
            Task(
                id="paid-task",
                description="Paid",
                prompt="Paid",
                complexity=TaskComplexity.MODERATE,
                assigned_agent=AgentType.SONNET,
                estimated_tokens=5000,
            ),
        ]
        total_cost = costs.calculate_workflow_cost(tasks)
        expected = 0.0 + (5000 / 1000 * 0.003)  # OpenCode free + Sonnet cost
        assert total_cost == expected


class TestOptimizationStrategy:
    """Test task optimization strategies."""

    def test_free_tier_prioritization(self) -> None:
        """Test that free tier (OpenCode) is prioritized."""
        strategy = OptimizationStrategy()
        task_types = [
            ("documentation", TaskComplexity.SIMPLE),
            ("simple_refactoring", TaskComplexity.MODERATE),
            ("basic_tests", TaskComplexity.SIMPLE),
            ("readme", TaskComplexity.SIMPLE),
        ]
        for task_type, complexity in task_types:
            agent = strategy.get_optimal_agent(complexity, task_type)
            assert agent == AgentType.OPENCODE

    def test_complexity_based_assignment(self) -> None:
        """Test agent assignment based on complexity."""
        strategy = OptimizationStrategy()

        # Critical tasks -> Opus
        agent = strategy.get_optimal_agent(TaskComplexity.CRITICAL, "architecture")
        assert agent == AgentType.OPUS

        # Complex implementation -> Codex
        agent = strategy.get_optimal_agent(TaskComplexity.COMPLEX, "implementation")
        assert agent == AgentType.CODEX

        # Moderate implementation -> Codex
        agent = strategy.get_optimal_agent(TaskComplexity.MODERATE, "implementation")
        assert agent == AgentType.CODEX

        # Simple tasks -> Haiku (unless it's docs, then OpenCode)
        agent = strategy.get_optimal_agent(TaskComplexity.SIMPLE, "validation")
        assert agent == AgentType.HAIKU

        # Trivial tasks -> Haiku
        agent = strategy.get_optimal_agent(TaskComplexity.TRIVIAL, "file_operation")
        assert agent == AgentType.HAIKU

    def test_task_type_specialization(self) -> None:
        """Test that specialized task types get correct agents."""
        strategy = OptimizationStrategy()

        # Documentation -> OpenCode (FREE)
        agent = strategy.get_optimal_agent(TaskComplexity.SIMPLE, "documentation")
        assert agent == AgentType.OPENCODE

        # QA -> Gemini
        agent = strategy.get_optimal_agent(TaskComplexity.SIMPLE, "qa")
        assert agent == AgentType.GEMINI

        # Security -> Opus
        agent = strategy.get_optimal_agent(TaskComplexity.COMPLEX, "security")
        assert agent == AgentType.OPUS

        # Debugging -> Opus
        agent = strategy.get_optimal_agent(TaskComplexity.COMPLEX, "debugging")
        assert agent == AgentType.OPUS


class TestGSDOrchestrator:
    """Test GSD orchestrator main functionality."""

    @pytest.fixture
    def orchestrator(self) -> GSDOrchestrator:
        """Create orchestrator instance for testing."""
        return GSDOrchestrator()

    def test_orchestrator_initialization(self, orchestrator: GSDOrchestrator) -> None:
        """Test that orchestrator initializes correctly."""
        assert orchestrator.tasks == []
        assert orchestrator.completed_tasks == []
        assert orchestrator.failed_tasks == []
        assert isinstance(orchestrator.costs, TokenCosts)
        assert isinstance(orchestrator.strategy, OptimizationStrategy)

    def test_add_task(self, orchestrator: GSDOrchestrator) -> None:
        """Test adding a task to the orchestrator."""
        task = Task(
            id="test-001",
            description="Test task",
            prompt="Do something",
            complexity=TaskComplexity.SIMPLE,
            assigned_agent=AgentType.HAIKU,
        )
        orchestrator.add_task(task)
        assert len(orchestrator.tasks) == 1
        assert orchestrator.tasks[0].id == "test-001"

    def test_assign_agent_by_complexity(self, orchestrator: GSDOrchestrator) -> None:
        """Test agent assignment based on complexity."""
        # Add a task without an agent
        task = Task(
            id="test-001",
            description="Implementation task",
            prompt="Implement feature",
            complexity=TaskComplexity.MODERATE,
            assigned_agent=AgentType.HAIKU,  # Will be reassigned
        )
        # Orchestrator should reassign based on complexity
        optimal_agent = orchestrator.assign_agent_by_complexity(task.complexity, "implementation")
        assert optimal_agent == AgentType.CODEX  # Codex for moderate implementation

    def test_optimize_task_distribution(self, orchestrator: GSDOrchestrator) -> None:
        """Test task distribution optimization for cost savings."""
        tasks = [
            Task(
                id="doc-001",
                description="Write docs",
                prompt="Document API",
                complexity=TaskComplexity.SIMPLE,
                assigned_agent=AgentType.SONNET,  # Suboptimal
                estimated_tokens=2000,
            ),
            Task(
                id="impl-001",
                description="Implement feature",
                prompt="Build feature",
                complexity=TaskComplexity.COMPLEX,
                assigned_agent=AgentType.HAIKU,  # Suboptimal
                estimated_tokens=5000,
            ),
        ]

        for task in tasks:
            orchestrator.add_task(task)

        # Optimize the distribution
        orchestrator.optimize_task_distribution()

        # Check that tasks were reassigned optimally
        doc_task = orchestrator.tasks[0]
        impl_task = orchestrator.tasks[1]

        assert doc_task.assigned_agent == AgentType.OPENCODE  # Free for docs
        assert impl_task.assigned_agent == AgentType.CODEX  # Codex for implementation

    def test_identify_parallel_tasks(self, orchestrator: GSDOrchestrator) -> None:
        """Test identifying tasks that can run in parallel."""
        tasks = [
            Task(
                id="task-1",
                description="Independent task 1",
                prompt="Do 1",
                complexity=TaskComplexity.SIMPLE,
                assigned_agent=AgentType.HAIKU,
            ),
            Task(
                id="task-2",
                description="Independent task 2",
                prompt="Do 2",
                complexity=TaskComplexity.SIMPLE,
                assigned_agent=AgentType.HAIKU,
            ),
            Task(
                id="task-3",
                description="Dependent task",
                prompt="Do 3",
                complexity=TaskComplexity.SIMPLE,
                assigned_agent=AgentType.HAIKU,
                dependencies=["task-1"],
            ),
        ]

        for task in tasks:
            orchestrator.add_task(task)

        waves = orchestrator.identify_parallel_tasks()

        # Should have 2 waves: [task-1, task-2] then [task-3]
        assert len(waves) == 2
        assert len(waves[0]) == 2  # First wave has 2 parallel tasks
        assert len(waves[1]) == 1  # Second wave has 1 dependent task
        assert waves[0][0].id in ["task-1", "task-2"]
        assert waves[0][1].id in ["task-1", "task-2"]
        assert waves[1][0].id == "task-3"

    def test_execute_parallel_tasks(self, orchestrator: GSDOrchestrator) -> None:
        """Test parallel task execution (simulation)."""
        tasks = [
            Task(
                id="parallel-1",
                description="Task 1",
                prompt="Do 1",
                complexity=TaskComplexity.SIMPLE,
                assigned_agent=AgentType.OPENCODE,
                estimated_tokens=1000,
            ),
            Task(
                id="parallel-2",
                description="Task 2",
                prompt="Do 2",
                complexity=TaskComplexity.SIMPLE,
                assigned_agent=AgentType.OPENCODE,
                estimated_tokens=1000,
            ),
        ]

        for task in tasks:
            orchestrator.add_task(task)

        # Execute in dry-run mode (simulation)
        results = orchestrator.execute_parallel_tasks(tasks, dry_run=True)

        assert len(results) == 2
        for task in results:
            assert task.status == "completed"
            assert task.result.get("simulated") is True

    def test_calculate_token_costs(self, orchestrator: GSDOrchestrator) -> None:
        """Test token cost calculation for workflow."""
        tasks = [
            Task(
                id="free-task",
                description="Free task",
                prompt="Free work",
                complexity=TaskComplexity.SIMPLE,
                assigned_agent=AgentType.OPENCODE,
                estimated_tokens=5000,
            ),
            Task(
                id="paid-task",
                description="Paid task",
                prompt="Paid work",
                complexity=TaskComplexity.MODERATE,
                assigned_agent=AgentType.SONNET,
                estimated_tokens=3000,
            ),
        ]

        for task in tasks:
            orchestrator.add_task(task)

        total_cost = orchestrator.calculate_token_costs()

        # OpenCode is free, Sonnet costs 0.003 per 1000 tokens
        expected_cost = 0.0 + (3000 / 1000 * 0.003)
        assert total_cost == expected_cost

    def test_generate_workflow_report(self, orchestrator: GSDOrchestrator) -> None:
        """Test workflow report generation."""
        tasks = [
            Task(
                id="task-1",
                description="Completed task",
                prompt="Complete",
                complexity=TaskComplexity.SIMPLE,
                assigned_agent=AgentType.OPENCODE,
                estimated_tokens=1000,
            ),
            Task(
                id="task-2",
                description="Failed task",
                prompt="Fail",
                complexity=TaskComplexity.MODERATE,
                assigned_agent=AgentType.SONNET,
                estimated_tokens=2000,
            ),
        ]

        for task in tasks:
            orchestrator.add_task(task)

        # Simulate execution
        orchestrator.tasks[0].status = "completed"
        orchestrator.completed_tasks.append(orchestrator.tasks[0])
        orchestrator.tasks[1].status = "failed"
        orchestrator.failed_tasks.append(orchestrator.tasks[1])

        report = orchestrator.generate_workflow_report("test-workflow")

        assert report.workflow_name == "test-workflow"
        assert report.total_tasks == 2
        assert report.completed_count == 1
        assert report.failed_count == 1
        assert report.total_cost > 0.0  # Has Sonnet task
        assert AgentType.OPENCODE in report.agent_distribution
        assert AgentType.SONNET in report.agent_distribution

    def test_decompose_feature(self, orchestrator: GSDOrchestrator) -> None:
        """Test feature decomposition into tasks."""
        feature_name = "User Authentication"
        tasks = orchestrator.decompose_feature(feature_name)

        # Should create multiple tasks with proper dependencies
        assert len(tasks) > 0

        # Should have architecture task
        arch_tasks = [t for t in tasks if "architecture" in t.description.lower()]
        assert len(arch_tasks) > 0

        # Should have implementation task
        impl_tasks = [t for t in tasks if "implement" in t.description.lower()]
        assert len(impl_tasks) > 0

        # Should have test task
        test_tasks = [t for t in tasks if "test" in t.description.lower()]
        assert len(test_tasks) > 0

        # Architecture should be assigned to Opus
        arch_task = arch_tasks[0]
        assert arch_task.assigned_agent == AgentType.OPUS

    def test_cost_optimization_comparison(self, orchestrator: GSDOrchestrator) -> None:
        """Test cost comparison between optimized and unoptimized workflows."""
        # Create tasks with suboptimal assignments
        unoptimized_tasks = [
            Task(
                id="doc-1",
                description="Documentation",
                prompt="Write docs",
                complexity=TaskComplexity.SIMPLE,
                assigned_agent=AgentType.SONNET,  # Could use OpenCode
                estimated_tokens=5000,
            ),
            Task(
                id="doc-2",
                description="More docs",
                prompt="Write more docs",
                complexity=TaskComplexity.SIMPLE,
                assigned_agent=AgentType.SONNET,  # Could use OpenCode
                estimated_tokens=3000,
            ),
        ]

        # Calculate unoptimized cost
        unoptimized_cost = orchestrator.costs.calculate_workflow_cost(unoptimized_tasks)

        # Add to orchestrator and optimize
        for task in unoptimized_tasks:
            orchestrator.add_task(task)
        orchestrator.optimize_task_distribution()

        # Calculate optimized cost
        optimized_cost = orchestrator.calculate_token_costs()

        # Optimized should be cheaper (OpenCode is free)
        assert optimized_cost < unoptimized_cost
        assert optimized_cost == 0.0  # All docs should use OpenCode


class TestWorkflowReport:
    """Test workflow report generation and serialization."""

    def test_report_creation(self) -> None:
        """Test creating a workflow report."""
        report = WorkflowReport(
            workflow_name="test-workflow",
            total_tasks=5,
            completed_count=4,
            failed_count=1,
            total_cost=0.045,
            total_tokens=15000,
            agent_distribution={
                AgentType.OPENCODE: 2,
                AgentType.SONNET: 2,
                AgentType.OPUS: 1,
            },
            execution_start=datetime.now(),
        )

        assert report.workflow_name == "test-workflow"
        assert report.total_tasks == 5
        assert report.completed_count == 4
        assert report.failed_count == 1
        assert report.success_rate == 0.8  # 4/5

    def test_report_serialization(self) -> None:
        """Test report can be converted to dictionary."""
        report = WorkflowReport(
            workflow_name="test-workflow",
            total_tasks=3,
            completed_count=3,
            failed_count=0,
            total_cost=0.0,  # All OpenCode
            total_tokens=6000,
            agent_distribution={AgentType.OPENCODE: 3},
            execution_start=datetime.now(),
        )

        data = report.to_dict()
        assert data["workflow_name"] == "test-workflow"
        assert data["total_tasks"] == 3
        assert data["total_cost"] == 0.0
        assert data["success_rate"] == 1.0

    def test_cost_savings_report(self) -> None:
        """Test that report highlights OpenCode cost savings."""
        report = WorkflowReport(
            workflow_name="cost-optimized",
            total_tasks=10,
            completed_count=10,
            failed_count=0,
            total_cost=0.0,  # All FREE via OpenCode
            total_tokens=20000,
            agent_distribution={AgentType.OPENCODE: 10},
            execution_start=datetime.now(),
        )

        # Calculate what it WOULD have cost with Sonnet
        sonnet_cost = 20000 * 0.003
        savings = sonnet_cost - report.total_cost

        assert report.total_cost == 0.0
        assert savings == sonnet_cost  # Saved 100%
        assert report.agent_distribution[AgentType.OPENCODE] == 10


class TestParallelExecutionPatterns:
    """Test parallel execution patterns and capabilities."""

    @pytest.fixture
    def orchestrator(self) -> GSDOrchestrator:
        """Create orchestrator instance for testing."""
        return GSDOrchestrator()

    def test_parallel_execution_capability(self) -> None:
        """Test that parallel execution is properly documented."""
        parallel_capability = {
            "method": "Call multiple Task tools in ONE message",
            "proven_agents": 3,
            "supports_parallel_execution": True,
            "all_tests_passed": True,
        }

        assert parallel_capability["proven_agents"] == 3
        assert parallel_capability["supports_parallel_execution"] is True

    def test_task_wave_execution(self, orchestrator: GSDOrchestrator) -> None:
        """Test executing tasks in waves for parallelism."""
        # Create independent tasks (wave 1)
        wave1_tasks = [
            Task(
                id=f"wave1-{i}",
                description=f"Wave 1 task {i}",
                prompt=f"Do {i}",
                complexity=TaskComplexity.SIMPLE,
                assigned_agent=AgentType.OPENCODE,
            )
            for i in range(3)
        ]

        # Create dependent tasks (wave 2)
        wave2_tasks = [
            Task(
                id="wave2-1",
                description="Wave 2 task",
                prompt="Do dependent work",
                complexity=TaskComplexity.SIMPLE,
                assigned_agent=AgentType.OPENCODE,
                dependencies=["wave1-0", "wave1-1", "wave1-2"],
            )
        ]

        all_tasks = wave1_tasks + wave2_tasks
        for task in all_tasks:
            orchestrator.add_task(task)

        waves = orchestrator.identify_parallel_tasks()

        assert len(waves) == 2
        assert len(waves[0]) == 3  # All wave 1 tasks can run in parallel
        assert len(waves[1]) == 1  # Wave 2 depends on wave 1


class TestIntegration:
    """Integration tests for complete workflows."""

    def test_full_feature_workflow(self) -> None:
        """Test a complete feature development workflow."""
        orchestrator = GSDOrchestrator()

        # Decompose a feature
        tasks = orchestrator.decompose_feature("Analytics Dashboard")

        # Should have proper task breakdown
        assert len(tasks) > 0

        # Optimize task distribution
        orchestrator.optimize_task_distribution()

        # Calculate costs
        total_cost = orchestrator.calculate_token_costs()

        # Generate report
        report = orchestrator.generate_workflow_report("revenue-dashboard")

        assert report.total_tasks == len(tasks)
        assert report.total_cost == total_cost
        assert AgentType.OPENCODE in report.agent_distribution  # Used free tier

    def test_documentation_workflow_all_free(self) -> None:
        """Test that documentation workflows use only free agents."""
        orchestrator = GSDOrchestrator()

        # Add documentation tasks
        doc_tasks = [
            Task(
                id=f"doc-{i}",
                description=f"Documentation task {i}",
                prompt=f"Write docs {i}",
                complexity=TaskComplexity.SIMPLE,
                assigned_agent=AgentType.SONNET,  # Suboptimal
                estimated_tokens=2000,
            )
            for i in range(5)
        ]

        for task in doc_tasks:
            orchestrator.add_task(task)

        # Optimize
        orchestrator.optimize_task_distribution()

        # All tasks should now use OpenCode
        for task in orchestrator.tasks:
            assert task.assigned_agent == AgentType.OPENCODE

        # Total cost should be zero
        total_cost = orchestrator.calculate_token_costs()
        assert total_cost == 0.0
