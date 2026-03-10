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
