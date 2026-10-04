# GitHub Release Setup

Repository:

`https://github.com/KouchakiDev/telegram-bot-platform`

## Recommended repository description

> Production-ready, modular Telegram bot platform for building scalable bots, Mini Apps, automation, admin panels, and custom workflows.

## Topics

```text
telegram
telegram-bot
python
fastapi
telegram-mini-app
automation
asyncio
sqlalchemy
alembic
docker
modular-architecture
```

## Release checks

```bash
python scripts/verify_parity.py
python -m compileall -q src scripts tests
pytest
ruff format --check .
ruff check .
mypy src/telegram_bot_platform
pip-audit
```

The optional compatibility runtime must also be exercised in staging when it is enabled:

```bash
pip install -e ".[legacy,legacy-db]"
platform-run-compat admin
platform-run-compat client
platform-run-compat staff
platform-run-compat auto-responder
```

Do not commit `.env`, production databases, generated exports, tokens, passwords, private keys, or user data.
