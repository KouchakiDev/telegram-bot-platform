# GitHub Release Setup

Recommended repository name:

```text
telegram-bot-platform
```

Recommended description:

> A modular, secure, configurable foundation for production-grade Telegram bots and Telegram Mini Apps.

Recommended topics:

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
```

## First push

Create an empty public repository at:

`https://github.com/KouchakiDev/telegram-bot-platform`

Then from the project root:

```bash
git init
git branch -M main
git add .
git commit -m "chore: initial public release"
git remote add origin https://github.com/KouchakiDev/telegram-bot-platform.git
git push -u origin main
```

Do not commit `.env`, local databases, log files, virtual environments, exports, bot tokens, or other credentials. The repository `.gitignore` and `.dockerignore` already exclude the common cases.

## Release checklist

Before publishing a production instance:

```bash
python -m compileall -q app scripts tests
ruff format --check .
ruff check .
mypy app
pip-audit
pytest
```

Also run the Docker build and a controlled staging test with a non-production bot/database.
