"""GSD (Get Shit Done) Multi-Agent Orchestrator.

This module provides a comprehensive orchestrator for managing multi-agent task
distribution with aggressive cost optimization. Key features:

1. COST OPTIMIZATION - OpenCode (MiniMax M2.5) is FREE and prioritized
2. PARALLEL EXECUTION - Multiple Task tools in one message = parallel agents
3. INTELLIGENT ASSIGNMENT - Tasks routed to optimal agents by complexity/type
4. TOKEN TRACKING - Full cost calculation and reporting
5. WORKFLOW ANALYTICS - Detailed reports on agent usage and savings

Cost Tiers (per 1000 tokens):
- FREE: OpenCode (MiniMax M2.5) = $0.00 - MAXIMIZE THIS!
- Fast: Haiku = $0.001
- Implementation: Codex = $0.002
- QA: Gemini = $0.0025
- Standard: Sonnet = $0.003
- Premium: Opus = $0.015

Architecture:
- Tasks are decomposed into parallelizable units
- Agent assignment optimizes for FREE tier first
- Dependencies create execution waves
- Each wave runs in parallel via multiple Task tool calls

Example Usage:
    >>> orchestrator = GSDOrchestrator()
    >>> tasks = orchestrator.decompose_feature("User Auth")
    >>> orchestrator.optimize_task_distribution()
    >>> report = orchestrator.generate_workflow_report("auth-feature")
    >>> print(f"Cost: ${report.total_cost:.4f}")

License: MIT
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Create a simple console logger without project-specific dependencies."""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(levelname)s %(name)s: %(message)s"))
        logger.addHandler(handler)

    logger.propagate = False
    return logger


class AgentType(Enum):
    """Agent types with their model identifiers.

    Each agent has a specific cost tier and use case:
    - OPENCODE: FREE tier - documentation, simple tasks (MAXIMIZE!)
    - HAIKU: Fast tier - quick operations, simple validation
    - CODEX: Implementation tier - feature development, tests
    - GEMINI: QA tier - adversarial testing, edge cases
    - SONNET: Standard tier - coordination, review
    - OPUS: Premium tier - architecture, critical decisions
    """

    OPUS = "claude-opus"
    SONNET = "claude-sonnet"
    HAIKU = "claude-haiku"
    CODEX = "openai-codex"
    OPENCODE = "minimax-opencode"  # FREE!
    GEMINI = "google-gemini"


class TaskComplexity(Enum):
    """Task complexity levels for agent assignment.

    Complexity drives cost optimization:
    - TRIVIAL/SIMPLE: Use FREE tier (OpenCode) when possible
    - MODERATE: Balance between cost and capability
    - COMPLEX: Use specialized agents (Codex, Gemini)
    - CRITICAL: Use premium agents (Opus) for high-stakes work
    """

    TRIVIAL = "trivial"
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    CRITICAL = "critical"


@dataclass
class Task:
    """Represents a single task in the workflow.

    Attributes:
        id: Unique task identifier
        description: Human-readable task description
        prompt: Detailed instructions for the agent
        complexity: Task complexity level
        assigned_agent: Agent assigned to execute this task
        dependencies: List of task IDs that must complete first
        estimated_tokens: Estimated token usage
        status: Current status (pending, in_progress, completed, failed)
        result: Task execution results
        metadata: Additional task metadata
    """

    id: str
    description: str
    prompt: str
    complexity: TaskComplexity
    assigned_agent: AgentType
    dependencies: list[str] = field(default_factory=list)
    estimated_tokens: int = 0
    status: str = "pending"
    result: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert task to dictionary for serialization.

        Returns:
            Dictionary representation of the task
        """
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
            "metadata": self.metadata,
        }


@dataclass
class WorkflowReport:
    """Report on workflow execution and costs.

    Provides comprehensive analytics on:
    - Task completion rates
    - Agent distribution
    - Token usage and costs
    - Cost savings from optimization

    Attributes:
        workflow_name: Name of the workflow
        total_tasks: Total number of tasks
        completed_count: Number of completed tasks
        failed_count: Number of failed tasks
        total_cost: Total cost in dollars
        total_tokens: Total tokens used
        agent_distribution: Count of tasks per agent
        execution_start: Workflow start time
        execution_end: Workflow end time
        cost_savings: Savings from using free tier
    """

    workflow_name: str
    total_tasks: int
    completed_count: int
    failed_count: int
    total_cost: float
    total_tokens: int
    agent_distribution: dict[AgentType, int]
    execution_start: datetime
    execution_end: datetime | None = None
    cost_savings: float = 0.0

    @property
    def success_rate(self) -> float:
        """Calculate task success rate.

        Returns:
            Success rate as a decimal (0.0 to 1.0)
        """
        if self.total_tasks == 0:
            return 0.0
        return self.completed_count / self.total_tasks

    @property
    def pending_count(self) -> int:
        """Calculate number of pending tasks.

        Returns:
            Number of pending tasks
        """
        return self.total_tasks - self.completed_count - self.failed_count

    def to_dict(self) -> dict[str, Any]:
        """Convert report to dictionary for serialization.

        Returns:
            Dictionary representation of the report
        """
        return {
            "workflow_name": self.workflow_name,
            "total_tasks": self.total_tasks,
            "completed_count": self.completed_count,
            "failed_count": self.failed_count,
            "pending_count": self.pending_count,
            "success_rate": self.success_rate,
            "total_cost": self.total_cost,
            "total_tokens": self.total_tokens,
            "cost_savings": self.cost_savings,
            "agent_distribution": {
                agent.value: count for agent, count in self.agent_distribution.items()
            },
            "execution_start": self.execution_start.isoformat(),
            "execution_end": self.execution_end.isoformat() if self.execution_end else None,
        }


class TokenCosts:
    """Token cost calculator for different agent types.

    Cost per 1000 tokens (USD):
    - OpenCode (MiniMax M2.5): $0.00 - FREE!
    - Haiku: $0.001 - Fast tier
    - Codex: $0.002 - Implementation tier
    - Gemini: $0.0025 - QA tier
    - Sonnet: $0.003 - Standard tier
    - Opus: $0.015 - Premium tier

    The orchestrator prioritizes OpenCode to minimize costs.
    """

    # Cost per 1000 tokens in USD
    COST_TABLE: dict[AgentType, float] = {
        AgentType.OPENCODE: 0.0,  # FREE - This is the key optimization!
        AgentType.HAIKU: 0.001,  # Fast tier
        AgentType.CODEX: 0.002,  # Implementation tier
        AgentType.GEMINI: 0.0025,  # QA tier
        AgentType.SONNET: 0.003,  # Standard tier
        AgentType.OPUS: 0.015,  # Premium tier
    }

    def get_cost(self, agent: AgentType) -> float:
        """Get cost per 1000 tokens for an agent.

        Args:
            agent: Agent type to get cost for

        Returns:
            Cost per 1000 tokens in USD
        """
        return self.COST_TABLE.get(agent, 0.0)

    def is_free(self, agent: AgentType) -> bool:
        """Check if an agent is free tier.

        Args:
            agent: Agent type to check

        Returns:
            True if agent has zero cost
        """
        return self.get_cost(agent) == 0.0

    def calculate_task_cost(self, task: Task) -> float:
        """Calculate cost for a single task.

        Args:
            task: Task to calculate cost for

        Returns:
            Cost in USD
        """
        cost_per_1k = self.get_cost(task.assigned_agent)
        return (task.estimated_tokens / 1000) * cost_per_1k

    def calculate_workflow_cost(self, tasks: list[Task]) -> float:
        """Calculate total cost for a list of tasks.

        Args:
            tasks: List of tasks to calculate cost for

        Returns:
            Total cost in USD
        """
        return sum(self.calculate_task_cost(task) for task in tasks)

    def calculate_savings(self, original_tasks: list[Task], optimized_tasks: list[Task]) -> float:
        """Calculate cost savings from optimization.

        Args:
            original_tasks: Tasks before optimization
            optimized_tasks: Tasks after optimization

        Returns:
            Cost savings in USD
        """
        original_cost = self.calculate_workflow_cost(original_tasks)
        optimized_cost = self.calculate_workflow_cost(optimized_tasks)
        return original_cost - optimized_cost


class OptimizationStrategy:
    """Strategy for optimizing agent assignment.

    Core principles:
    1. FREE FIRST - Use OpenCode for all compatible tasks
    2. COMPLEXITY MATCH - Match agent capability to task complexity
    3. SPECIALIZATION - Use specialized agents for specific task types
    4. COST AWARENESS - Minimize total cost while maintaining quality

    The strategy prioritizes cost savings while ensuring tasks are
    assigned to agents with appropriate capabilities.
    """

    def get_optimal_agent(self, complexity: TaskComplexity, task_type: str) -> AgentType:
        """Get optimal agent for a task based on complexity and type.

        Strategy decision tree:
        1. Check for specialization requirements (docs, qa, security)
        2. Check complexity level
        3. Default to cost-optimized agent for complexity tier

        Args:
            complexity: Task complexity level
            task_type: Type of task (implementation, documentation, qa, etc.)

        Returns:
            Optimal agent type for the task
        """
        task_type_lower = task_type.lower()

        # FREE TIER FIRST - Documentation and simple tasks
        if task_type_lower in ["documentation", "readme", "docs"]:
            return AgentType.OPENCODE  # FREE!

        # CRITICAL COMPLEXITY - Always use Opus
        if complexity == TaskComplexity.CRITICAL:
            return AgentType.OPUS

        # SPECIALIZATION - Architecture, security, debugging
        if task_type_lower in ["architecture", "arch"]:
            return AgentType.OPUS
        if task_type_lower in ["security", "sec"]:
            return AgentType.OPUS
        if task_type_lower in ["debugging", "debug"]:
            return AgentType.OPUS

        # QA SPECIALIZATION
        if task_type_lower in ["qa", "testing", "adversarial"]:
            if complexity == TaskComplexity.SIMPLE:
                return AgentType.GEMINI
            return AgentType.GEMINI

        # COMPLEX TASKS
        if complexity == TaskComplexity.COMPLEX:
            if task_type_lower in ["implementation", "impl", "feature"]:
                return AgentType.CODEX
            if task_type_lower in ["refactoring", "refactor"]:
                return AgentType.CODEX
            return AgentType.CODEX

        # MODERATE TASKS
        if complexity == TaskComplexity.MODERATE:
            if task_type_lower in ["implementation", "impl", "feature", "tests"]:
                return AgentType.CODEX
            if task_type_lower in ["refactoring", "refactor"]:
                return AgentType.CODEX
            if task_type_lower in ["simple_refactoring", "basic_implementation"]:
                return AgentType.OPENCODE  # FREE for simple moderate tasks
            return AgentType.SONNET

        # SIMPLE TASKS - Optimize for FREE tier
        if complexity == TaskComplexity.SIMPLE:
            if task_type_lower in [
                "documentation",
                "simple_refactoring",
                "basic_implementation",
                "basic_tests",
            ]:
                return AgentType.OPENCODE  # FREE!
            if task_type_lower in ["validation", "check"]:
                return AgentType.HAIKU
            return AgentType.HAIKU

        # TRIVIAL TASKS - Fastest agent
        if complexity == TaskComplexity.TRIVIAL:
            return AgentType.HAIKU

        # DEFAULT - Cost-optimized based on complexity
        return AgentType.HAIKU


class GSDOrchestrator:
    """Main orchestrator for multi-agent GSD workflows.

    This orchestrator manages the complete lifecycle of multi-agent workflows:
    1. Task decomposition and assignment
    2. Cost optimization (prioritizing FREE tier)
    3. Parallel execution planning
    4. Token usage tracking
    5. Workflow reporting

    Key Features:
    - Aggressive cost optimization via OpenCode (FREE tier)
    - Parallel execution via Task tool batching
    - Intelligent agent assignment
    - Comprehensive analytics and reporting

    Example Usage:
        >>> orchestrator = GSDOrchestrator()
        >>> tasks = orchestrator.decompose_feature("User Authentication")
        >>> orchestrator.optimize_task_distribution()
        >>> waves = orchestrator.identify_parallel_tasks()
        >>> report = orchestrator.generate_workflow_report("auth-feature")

    Attributes:
        tasks: All tasks in the workflow
        completed_tasks: Successfully completed tasks
        failed_tasks: Failed tasks
        costs: Token cost calculator
        strategy: Optimization strategy
        logger: Logger instance
    """

    def __init__(self, logger: logging.Logger | None = None) -> None:
        """Initialize the orchestrator.

        Args:
            logger: Optional logger instance. If not provided, creates a new one.
        """
        self.tasks: list[Task] = []
        self.completed_tasks: list[Task] = []
        self.failed_tasks: list[Task] = []
        self.costs = TokenCosts()
        self.strategy = OptimizationStrategy()
        self.logger = logger or setup_logger("gsd-orchestrator", level=logging.INFO)

    def add_task(self, task: Task) -> None:
        """Add a task to the workflow.

        Args:
            task: Task to add
        """
        self.tasks.append(task)
        self.logger.debug(f"Added task: {task.id} - {task.description}")

    def assign_agent_by_complexity(self, complexity: TaskComplexity, task_type: str) -> AgentType:
        """Assign optimal agent based on task complexity and type.

        This method uses the optimization strategy to select the best agent
        for a given task, prioritizing cost savings while maintaining quality.

        Args:
            complexity: Task complexity level
            task_type: Type of task (implementation, documentation, etc.)

        Returns:
            Optimal agent type for the task
        """
        return self.strategy.get_optimal_agent(complexity, task_type)

    def optimize_task_distribution(self) -> None:
        """Optimize task distribution for cost savings.

        This method reassigns tasks to more cost-effective agents while
        maintaining appropriate capability levels. It prioritizes:
        1. OpenCode (FREE) for all compatible tasks
        2. Haiku for simple operations
        3. Specialized agents only when necessary

        The optimization can result in significant cost savings, especially
        for documentation-heavy workflows.
        """
        self.logger.info("Optimizing task distribution for cost savings...")

        original_cost = self.costs.calculate_workflow_cost(self.tasks)

        for task in self.tasks:
            # Infer task type from description
            task_type = self._infer_task_type(task.description)

            # Get optimal agent
            optimal_agent = self.strategy.get_optimal_agent(task.complexity, task_type)

            # Reassign if different
            if optimal_agent != task.assigned_agent:
                old_agent = task.assigned_agent
                task.assigned_agent = optimal_agent
                self.logger.debug(
                    f"Reassigned {task.id}: {old_agent.value} -> {optimal_agent.value}"
                )

        optimized_cost = self.costs.calculate_workflow_cost(self.tasks)
        savings = original_cost - optimized_cost

        self.logger.info(f"Original cost: ${original_cost:.4f}")
        self.logger.info(f"Optimized cost: ${optimized_cost:.4f}")
        self.logger.info(f"Savings: ${savings:.4f} ({savings / original_cost * 100:.1f}%)")

    def _infer_task_type(self, description: str) -> str:
        """Infer task type from description.

        Args:
            description: Task description

        Returns:
            Inferred task type
        """
        desc_lower = description.lower()

        # Documentation
        if any(kw in desc_lower for kw in ["document", "docs", "readme", "api doc"]):
            return "documentation"

        # QA and testing
        if any(kw in desc_lower for kw in ["qa", "test", "edge case", "adversarial"]):
            return "qa"

        # Architecture
        if any(kw in desc_lower for kw in ["architecture", "design", "model"]):
            return "architecture"

        # Security
        if any(kw in desc_lower for kw in ["security", "auth", "credential"]):
            return "security"

        # Debugging
        if any(kw in desc_lower for kw in ["debug", "fix", "bug"]):
            return "debugging"

        # Implementation
        if any(kw in desc_lower for kw in ["implement", "build", "create", "develop"]):
            return "implementation"

        # Refactoring
        if any(kw in desc_lower for kw in ["refactor", "cleanup", "reorganize"]):
            return "refactoring"

        # Default
        return "implementation"

    def identify_parallel_tasks(self) -> list[list[Task]]:
        """Identify tasks that can run in parallel.

        This method analyzes task dependencies to create execution "waves"
        where all tasks in a wave can run in parallel. This enables:
        1. Maximum throughput via parallel agent execution
        2. Efficient resource utilization
        3. Reduced total execution time

        Parallel execution is achieved by calling multiple Task tools
        in a single message.

        Returns:
            List of task waves, where each wave contains tasks that can
            run in parallel
        """
        self.logger.info("Identifying parallel execution waves...")

        # Build dependency map
        dep_map: dict[str, set[str]] = {}
        for task in self.tasks:
            dep_map[task.id] = set(task.dependencies)

        waves: list[list[Task]] = []
        remaining = set(task.id for task in self.tasks)

        while remaining:
            # Find tasks with no remaining dependencies
            wave_ids = {
                task_id for task_id in remaining if not dep_map[task_id].intersection(remaining)
            }

            if not wave_ids:
                self.logger.error("Circular dependency detected!")
                break

            # Create wave
            wave = [task for task in self.tasks if task.id in wave_ids]
            waves.append(wave)

            self.logger.info(
                f"Wave {len(waves)}: {len(wave)} parallel tasks - {[t.id for t in wave]}"
            )

            # Remove wave tasks from remaining
            remaining -= wave_ids

        self.logger.info(f"Total waves: {len(waves)}")
        return waves

    def execute_parallel_tasks(self, tasks: list[Task], dry_run: bool = True) -> list[Task]:
        """Execute tasks in parallel.

        In production, this would spawn multiple Task agents by calling
        the Task tool multiple times in a single message. For example:

            Task(description="Task 1", prompt="...", subagent_type="general-purpose")
            Task(description="Task 2", prompt="...", subagent_type="general-purpose")
            Task(description="Task 3", prompt="...", subagent_type="general-purpose")

        Args:
            tasks: List of tasks to execute in parallel
            dry_run: If True, simulate execution without running agents

        Returns:
            List of executed tasks with results
        """
        self.logger.info(f"Executing {len(tasks)} tasks in parallel...")

        if dry_run:
            # Simulate execution
            for task in tasks:
                task.status = "completed"
                task.result = {
                    "simulated": True,
                    "agent": task.assigned_agent.value,
                    "tokens_used": task.estimated_tokens,
                    "cost": self.costs.calculate_task_cost(task),
                }
                self.completed_tasks.append(task)
                self.logger.debug(f"Simulated execution: {task.id}")
        else:
            # In real execution, this would use the Task tool
            self.logger.warning(
                "Real parallel execution requires calling Task tool multiple times. "
                "This is a placeholder for the actual implementation."
            )

        return tasks

    def calculate_token_costs(self) -> float:
        """Calculate total token costs for all tasks.

        Returns:
            Total cost in USD
        """
        total_cost = self.costs.calculate_workflow_cost(self.tasks)
        self.logger.info(f"Total estimated cost: ${total_cost:.4f}")
        return total_cost

    def generate_workflow_report(self, workflow_name: str) -> WorkflowReport:
        """Generate comprehensive workflow report.

        This report provides detailed analytics on:
        - Task completion rates
        - Agent distribution
        - Token usage and costs
        - Cost savings from optimization

        Args:
            workflow_name: Name of the workflow

        Returns:
            Workflow report with full analytics
        """
        self.logger.info(f"Generating workflow report: {workflow_name}")

        # Count agent distribution
        agent_distribution: dict[AgentType, int] = {}
        for task in self.tasks:
            agent = task.assigned_agent
            agent_distribution[agent] = agent_distribution.get(agent, 0) + 1

        # Calculate totals
        total_tokens = sum(task.estimated_tokens for task in self.tasks)
        total_cost = self.costs.calculate_workflow_cost(self.tasks)

        # Calculate potential savings (if everything used Sonnet)
        baseline_cost = (total_tokens / 1000) * TokenCosts.COST_TABLE[AgentType.SONNET]
        cost_savings = baseline_cost - total_cost

        report = WorkflowReport(
            workflow_name=workflow_name,
            total_tasks=len(self.tasks),
            completed_count=len(self.completed_tasks),
            failed_count=len(self.failed_tasks),
            total_cost=total_cost,
            total_tokens=total_tokens,
            agent_distribution=agent_distribution,
            execution_start=datetime.now(),
            cost_savings=cost_savings,
        )

        # Log report summary
        self.logger.info(f"Report: {workflow_name}")
        self.logger.info(f"  Total tasks: {report.total_tasks}")
        self.logger.info(f"  Completed: {report.completed_count}")
        self.logger.info(f"  Failed: {report.failed_count}")
        self.logger.info(f"  Success rate: {report.success_rate:.1%}")
        self.logger.info(f"  Total tokens: {report.total_tokens}")
        self.logger.info(f"  Total cost: ${report.total_cost:.4f}")
        self.logger.info(f"  Cost savings: ${report.cost_savings:.4f}")
        self.logger.info("  Agent distribution:")
        for agent, count in sorted(agent_distribution.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / report.total_tasks) * 100
            is_free = " (FREE!)" if self.costs.is_free(agent) else ""
            self.logger.info(f"    {agent.value}: {count} ({percentage:.1f}%){is_free}")

        return report

    def decompose_feature(self, feature_name: str) -> list[Task]:
        """Decompose a feature into optimized tasks.

        This method creates a standard feature development workflow:
        1. Architecture (Opus - critical)
        2. Implementation (Codex - complex)
        3. Tests (Codex - moderate)
        4. QA (Gemini - simple)
        5. Documentation (OpenCode - FREE!)

        Args:
            feature_name: Name of the feature to decompose

        Returns:
            List of tasks with proper dependencies and agent assignments
        """
        self.logger.info(f"Decomposing feature: {feature_name}")

        tasks = [
            Task(
                id=f"{feature_name.lower().replace(' ', '-')}-arch",
                description=f"Define architecture and data models for {feature_name}",
                prompt=f"Design the architecture for {feature_name} feature. "
                f"Include data models, API interfaces, and component interactions.",
                complexity=TaskComplexity.CRITICAL,
                assigned_agent=AgentType.OPUS,
                estimated_tokens=5000,
            ),
            Task(
                id=f"{feature_name.lower().replace(' ', '-')}-impl",
                description=f"Implement core {feature_name} logic",
                prompt=f"Implement the {feature_name} feature based on the architecture. "
                f"Follow TDD principles and coding standards.",
                complexity=TaskComplexity.COMPLEX,
                assigned_agent=AgentType.CODEX,
                dependencies=[f"{feature_name.lower().replace(' ', '-')}-arch"],
                estimated_tokens=8000,
            ),
            Task(
                id=f"{feature_name.lower().replace(' ', '-')}-tests",
                description=f"Write comprehensive test suite for {feature_name}",
                prompt=f"Create tests for {feature_name} with >80% coverage. "
                f"Include unit tests, integration tests, and edge cases.",
                complexity=TaskComplexity.MODERATE,
                assigned_agent=AgentType.CODEX,
                dependencies=[f"{feature_name.lower().replace(' ', '-')}-impl"],
                estimated_tokens=6000,
            ),
            Task(
                id=f"{feature_name.lower().replace(' ', '-')}-qa",
                description=f"Adversarial QA for {feature_name}",
                prompt=f"Test {feature_name} for edge cases and failure modes. "
                f"Try to break assumptions and find bugs.",
                complexity=TaskComplexity.SIMPLE,
                assigned_agent=AgentType.GEMINI,
                dependencies=[f"{feature_name.lower().replace(' ', '-')}-tests"],
                estimated_tokens=3000,
            ),
            Task(
                id=f"{feature_name.lower().replace(' ', '-')}-docs",
                description=f"Generate documentation for {feature_name}",
                prompt=f"Create comprehensive documentation for {feature_name}. "
                f"Include usage examples, API reference, and architecture notes.",
                complexity=TaskComplexity.SIMPLE,
                assigned_agent=AgentType.OPENCODE,  # FREE!
                dependencies=[f"{feature_name.lower().replace(' ', '-')}-impl"],
                estimated_tokens=2000,
            ),
        ]

        # Add tasks to orchestrator
        for task in tasks:
            self.add_task(task)

        self.logger.info(f"Created {len(tasks)} tasks for {feature_name}")
        return tasks
