# Repository Setup

## Publish

```bash
git remote add origin https://github.com/<your-account>/gsd-multi-agent.git
git push -u origin main
```

## Recommended Repository Metadata

- topics: `claude-code`, `multi-agent`, `automation`, `developer-tools`
- short description: `Portable multi-agent workflow bootstrap for Claude Code projects`

## Release Checklist

1. Run `uv run --extra dev pytest`
2. Run `uv run --extra dev ruff check .`
3. Review `README.md` and `SECURITY.md`
4. Tag a release
