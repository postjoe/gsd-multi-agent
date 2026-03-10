# Task Tool Capability Reference

The `Task` tool can be used to delegate work to additional agents inside Claude Code.

## Basic Pattern

```python
Task(
    description="Short task description",
    prompt="Detailed instructions",
    subagent_type="general-purpose",
)
```

## Parallel Pattern

Parallel work is achieved by issuing multiple `Task(...)` calls in the same message when the tasks are independent.

## Recommended Uses

- implementation slices with clear boundaries
- test writing
- documentation
- verification passes on isolated areas

## Avoid

- hiding unresolved architecture decisions inside subagent prompts
- granting broad command permissions without review
- assuming every task benefits from parallelization
