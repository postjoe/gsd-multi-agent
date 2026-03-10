# GSD Orchestrator

`src/gsd_orchestrator.py` provides a small orchestration layer for:

- task definition
- agent assignment by complexity
- simple dependency-wave planning
- token cost estimation
- workflow reporting

## Core Types

- `Task`
- `TaskComplexity`
- `AgentType`
- `WorkflowReport`
- `GSDOrchestrator`

## Typical Usage

```python
from gsd_orchestrator import GSDOrchestrator

orchestrator = GSDOrchestrator()
tasks = orchestrator.decompose_feature("Example Feature")
orchestrator.optimize_task_distribution()
waves = orchestrator.identify_parallel_tasks()
report = orchestrator.generate_workflow_report("example-feature")
```

## Notes

- lower-cost agents are preferred for simple work
- complex and security-sensitive work is assigned to stronger lanes
- execution is simulated in this repository; downstream tooling decides how to run real agents
