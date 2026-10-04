## Summary

Describe what changed and why.

## Validation

- [ ] `pytest`
- [ ] `ruff check .`
- [ ] `mypy src/telegram_bot_platform`
- [ ] `pip-audit`
- [ ] Docker build (when infrastructure changed)

## Migration / Compatibility

Describe database, environment-variable, API, Telegram, or deployment impact. Use `None` when not applicable.

## Security

- [ ] No secrets or credentials were added.
- [ ] Untrusted input is validated.
- [ ] Authorization behavior was reviewed.
