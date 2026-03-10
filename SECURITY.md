# Security Policy

## Scope

`gsd-multi-agent` is a local bootstrap package. Its primary security boundary is the machine and repository where `install.py` and `verify.py` are executed.

## Trust Model

- `install.py` writes files into a target project and can install Python dependencies.
- Generated `.claude/settings.local.json` files grant local command permissions to the agent runtime.
- `skills-lock.json` references third-party skill sources; users should review those sources before enabling them in sensitive repositories.

## Safe Usage

1. Review generated config files before committing them to a production repository.
2. Run `python gsd_setup/install.py --dry-run` first when integrating into a new project.
3. Treat dependency installation as a trusted-network step and review pinned versions in `requirements.txt`.
4. Do not run the installer against untrusted repositories with symlink-heavy layouts unless you have reviewed the tree.

## Reporting

Open a private security report through GitHub Security Advisories or contact the maintainer directly before filing a public issue for exploitable problems.
