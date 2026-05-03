## Summary

Briefly explain what changed and why.

## How to verify

Steps you took (manual or automated):

- …

## Checklist

- [ ] I have read and agree to follow the [Code of Conduct](../CODE_OF_CONDUCT.md)
- [ ] `uv run ruff format --check .` and `uv run ruff check .`
- [ ] `uv run mypy src/klima`
- [ ] `uv run pytest tests/`
- [ ] If UI snapshots changed on purpose: `uv run pytest tests/ --snapshot-update` and the diff was reviewed
