# GSD Multi-Agent

Portable bootstrap package for adding structured multi-agent workflows to a local Claude Code project.

[![Version](https://img.shields.io/badge/version-1.0.1-blue.svg)](#)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)

## What It Does

- installs a reusable workflow scaffold into a target project
- adds orchestrator examples, validation scripts, and templates
- prioritizes lower-cost model lanes for simple tasks
- provides testable, documented patterns for parallel agent execution

## Quick Start

```bash
git clone https://github.com/postjoe/gsd-multi-agent.git
cd gsd-multi-agent
```

Copy the package into the target repository as `gsd_setup/`, then from the target repository run:

```bash
python gsd_setup/install.py --project-name "Example Project" --dry-run
python gsd_setup/install.py --project-name "Example Project"
python gsd_setup/verify.py
```

## Included Files

```text
gsd_setup/
├── install.py
├── verify.py
├── requirements.txt
├── templates/
├── scripts/
├── docs/
├── src/
└── tests/
```

## Security Notes

- Review [SECURITY.md](SECURITY.md) before using this in a sensitive repository.
- The installer blocks writes that resolve outside the selected project root.
- Generated `.claude/settings.local.json` files should be reviewed before commit.
- Dependency versions are pinned in [requirements.txt](requirements.txt).

## Development

```bash
uv run --extra dev pytest
uv run --extra dev ruff check .
```

`uv.lock` is committed and should stay in sync with `pyproject.toml` and `requirements.txt`.

## Documentation

- [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)
- [docs/GSD_WORKFLOW_GUIDE.md](docs/GSD_WORKFLOW_GUIDE.md)
- [docs/GSD_ORCHESTRATOR.md](docs/GSD_ORCHESTRATOR.md)

## License

MIT
