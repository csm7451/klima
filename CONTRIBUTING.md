# Contributing to klima

Thanks for your interest. This document is the entry point for issues, pull requests, and local development.

## Code of conduct

Participation is governed by our [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By contributing, you agree to uphold it.

## Before you start

- **Bugs**: use the [bug report](.github/ISSUE_TEMPLATE/bug_report.yml) template and include `klima --version`, OS, terminal, and Python version.
- **Features**: open an issue (or use the feature request template) to describe the problem and proposed behavior so maintainers can align before you invest in a large change.

## Development setup

Prerequisites: **Python 3.12+** and **[uv](https://docs.astral.sh/uv/)**.

```bash
git clone https://github.com/YOUR_GITHUB_USER/klima.git
cd klima
uv sync --all-groups
```

Run the app from the repo:

```bash
uv run klima --help
uv run klima Berlin
```

## Checks (match CI)

From the repository root:

```bash
uv run ruff format --check .
uv run ruff check .
uv run mypy src/klima
uv run pytest tests/
uv build
```

When Textual UI output changes **intentionally**, update snapshots:

```bash
uv run pytest tests/ --snapshot-update
```

Review diffs under `tests/__snapshots__/` before committing.

## Pull requests

- Keep changes focused and described in complete sentences (see the [PR template](.github/pull_request_template.md)).
- Add or extend tests for behavior you change.
- Do not commit secrets or personal API keys (this project does not require keys for Open-Meteo).

## Versioning

This project follows [Semantic Versioning](https://semver.org/) (MAJOR.MINOR.PATCH). The released version is defined in `src/klima/__init__.py` as `__version__` (Hatch reads it for package metadata). Notable changes are summarized in [CHANGELOG.md](CHANGELOG.md).

## Repository metadata after you fork

Replace the placeholder `YOUR_GITHUB_USER` in:

- [README.md](README.md) (CI badge URL)
- [pyproject.toml](pyproject.toml) (`[project.urls]`)

so links and badges point at your fork or canonical remote.
