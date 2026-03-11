# GSD Workflow Guide

## Goal

Use this package to make multi-agent work repeatable inside a local repository.

## Suggested Flow

1. Define the feature or maintenance task.
2. Break the work into independent slices.
3. Assign stronger agents only where complexity justifies it.
4. Run tests and verification after each wave.
5. Document any new permissions or trust assumptions.

## Good Candidates for Parallel Work

- documentation plus tests
- isolated refactors in separate modules
- validation and review passes

## Poor Candidates for Parallel Work

- schema changes with shared migration state
- unresolved architecture work
- tasks that all mutate the same files

## CLI Invocation Notes

When dispatching to agents non-interactively, be aware of these tested patterns:

**Codex (OpenAI)**
```bash
codex exec --full-auto "your prompt here"
```
- Default sandbox is **read-only** — Codex will generate code but cannot write files without `--full-auto` or `--sandbox workspace-write`.
- Non-interactive mode is `codex exec`, not the base `codex` command.

**OpenCode (MiniMax M2.5 free tier)**
```bash
opencode run -m opencode/minimax-m2.5-free "your prompt here"
```
- Use `opencode models` to list available models on your setup.
- The free tier model string may vary by OpenCode version.

> These patterns were validated on 2026-03-11. Your CLI versions and configuration may differ — run `codex exec --help` and `opencode run --help` to confirm available flags.
