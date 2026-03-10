# {{PROJECT_NAME}} - Developer Instructions

## Project Defaults

- Source lives under `src/`
- Tests live under `tests/`
- Tool configuration lives in `pyproject.toml`

## Working Rules

1. Write tests with changes.
2. Keep commits scoped to one logical change.
3. Prefer `uv run` for local commands.
4. Run tests and lint before finishing substantial work.
5. Keep templates and automation generic unless the target project requires otherwise.

## Multi-Agent Guidance

- Use the `Task` tool for parallel work when tasks are independent.
- Keep architecture and security decisions with the coordinating agent.
- Use lower-cost lanes for documentation and simple maintenance tasks.
- Review generated command permissions before approving them in a target repo.

## Suggested Commands

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

## Project Layout

```text
src/
tests/
scripts/
docs/
antigravity/
.claude/
```
