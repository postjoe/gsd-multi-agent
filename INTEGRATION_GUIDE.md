# Integration Guide

This package is designed to be copied into another repository as `gsd_setup/`.

## Install

1. Copy this repository into the target project as `gsd_setup/`.
2. From the target project root, run:

```bash
python gsd_setup/install.py --project-name "Example Project" --dry-run
python gsd_setup/install.py --project-name "Example Project"
python gsd_setup/verify.py
```

## What Gets Installed

- `.claude/settings.local.json`
- `antigravity/agent_policy.yaml`
- `skills-lock.json`
- `CLAUDE.md`
- `TASK_TOOL_CAPABILITY.md`
- orchestrator examples, tests, and docs

## Customization

- update `CLAUDE.md` with project-specific conventions
- review `.claude/settings.local.json` before approving agent permissions
- adjust `antigravity/agent_policy.yaml` to fit your model and cost preferences

## Troubleshooting

- If imports fail, verify the target project has a valid Python package under `src/`.
- If verification fails, rerun `python gsd_setup/verify.py --verbose`.
- If you do not want automatic dependency install, run the installer with `--skip-deps`.
