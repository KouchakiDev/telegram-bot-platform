# Contributing

Thanks for contributing to Telegram Bot Platform.

## Development

Use Python 3.12 or 3.13 and install the development dependencies:

```bash
python -m pip install -e ".[dev]"
```

Copy `.env.example` to `.env`, use a development database, and never place real secrets in source control.

## Checks

Run the same checks used by CI before opening a pull request:

```bash
python -m compileall -q app scripts tests
ruff format --check .
ruff check .
mypy app
pip-audit
pytest
```

## Architecture rules

Keep Telegram and HTTP code in adapters. Put use-case orchestration in application services, stable business concepts in the domain layer, and external I/O in infrastructure adapters. Prefer composition, explicit dependencies, bounded resources, and database-backed state.

## Pull requests

Explain the problem, the design, compatibility impact, and validation. Database changes require an Alembic migration. Changes that affect Telegram permissions or external API behavior must document those constraints.
