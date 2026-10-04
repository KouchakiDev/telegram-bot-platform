# Validation

The parity edition is validated from the repository root.

## Local checks

```bash
python scripts/verify_parity.py
PYTHONPATH=src pytest -q
python -m compileall -q src scripts tests
```

`verify_parity.py` compares the original source inventory captured during the audit with the compatibility tree. The current invariant is:

- 67 original Python modules represented
- 88 original classes represented
- 1,511 original functions/methods represented
- no reduction in the audited callable inventory

The test suite covers configuration, role policy, content services, Mini App authentication, rate limiting, Telegram application construction, and parity invariants.

## CI-only checks

The GitHub Actions workflow additionally runs formatting/linting, static type checking, dependency auditing, package build validation, tests, and Docker build validation. These checks require the development toolchain and network-enabled dependency installation and therefore are not all available in every local sandbox.

## Integration validation before production

Run the following against staging credentials and services:

1. Telegram bot startup and update handling.
2. Database migration from a copy of the production schema.
3. Legacy compatibility runner workflows.
4. Mini App authentication through Telegram.
5. External API integrations.
6. Graceful shutdown under worker load.

Do not treat passing unit tests as proof of Telegram or broker-side behavior.
