# Telegram Bot Platform

[![CI](https://github.com/KouchakiDev/telegram-bot-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/KouchakiDev/telegram-bot-platform/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.12%20%7C%203.13-3776AB.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A modular, secure, configurable foundation for building production-grade Telegram bots and Mini Apps, with a complete responsive operations console and the original application feature set preserved under a compatibility layer for non-destructive modernization.

This repository is intentionally **domain-neutral**. User-facing defaults are designed for lawful commerce, service delivery, support, community, automation, and content channels and are reviewed to avoid legacy sensitive positioning. See `docs/CONTENT_POLICY.md`. It is not tied to one business, channel, workflow, or bot concept. Use the same platform as a starting point for community bots, client-service bots, internal operations bots, content publishing systems, notification bots, automation bots, or custom business workflows. The core provides reusable platform primitives, while the preserved compatibility layer keeps the original production workflows available during migration. Domain-specific behavior should be expressed through focused feature modules rather than hard-coded into transport handlers.

## What is included

### Bot and Telegram capabilities

- Async Telegram bot foundation using `python-telegram-bot`.
- Commands, callback queries, inline keyboards, reply keyboards, and Mini App launch flows.
- Chat-aware behavior for private chats, groups, supergroups, and channels.
- Explicit Telegram permission boundaries instead of assuming capabilities the Bot API does not provide.
- Thin Telegram adapters that delegate business behavior to application services.

### Users, clients, staff, and administration

- Persistent Telegram user and chat registry.
- Reusable roles: `owner`, `admin`, `manager`, `staff`, `support`, `moderator`, `analyst`, `client`, and `member`.
- Bootstrap administrators from environment configuration.
- Audit trail for important administrative/application actions.
- Blocked-user state and language preference tracking.
- A foundation for client-support, staff, moderation, and internal-operation workflows without coupling them to Telegram handlers.

### Content and automation

- Draft → review → publish → archive content lifecycle.
- Scheduled messages and scheduled content publishing.
- Notification outbox with retries and at-least-once delivery semantics.
- Configurable auto-reply rules with exact, contains, and regex matching.
- Bounded in-process caches with TTLs.
- Persistent jobs instead of fragile in-memory background state.

### Mini App and API

- FastAPI backend with explicit API boundaries.
- Telegram Mini App authentication using server-side `initData` verification.
- Signed, time-limited sessions.
- Admin-aware API routes.
- Complete responsive Mini App console with dashboard, content lifecycle, scheduling, auto-reply management, chat module controls, role management, audit activity, settings, loading states, error handling, and Telegram theme integration.
- Liveness and database readiness endpoints.


### Mini App console

The bundled Mini App is a real operations console rather than a placeholder. It authenticates the Telegram user server-side, creates a signed HTTP session, adapts to Telegram theme/safe-area values, and exposes only actions allowed by the authenticated role. Telegram recommends mobile-first responsive interfaces, dynamic theme handling, and safe-area support for Mini Apps. citeturn229984search0turn229984search1

For administrators, the console provides:

- Dashboard and runtime status
- Content creation, editing, publishing, archiving, and scheduling
- Scheduled-job inspection and cancellation
- Auto-reply CRUD, priority, match mode, enable/disable, and usage counts
- Registered chat inspection and module toggles
- User registry and persistent role management
- Read-only audit activity
- Full settings control plane with typed values, secret masking, reset-to-default, and restart semantics
- Full bilingual translation catalog editor for English/Persian strings

The backend endpoints are under `/api/` and require the signed session cookie. Telegram `initData` is verified on the server before that session is issued.

### Infrastructure and operations

- SQLAlchemy 2 async database layer.
- SQLite for local development/tests; MySQL and PostgreSQL for production.
- Alembic migrations with non-destructive schema evolution.
- Structured logging and request IDs.
- Bounded rate limiting.
- Background worker with cancellation and graceful shutdown.
- Docker image with non-root execution.
- Docker Compose stack with database, migration, web, bot, and worker services.
- GitHub Actions CI, Dependabot, CODEOWNERS, issue templates, and security policy.

## Architecture

```text
                   ┌─────────────────────────┐
                   │      Telegram Bot       │
                   │  commands / callbacks   │
                   └────────────┬────────────┘
                                │
                   ┌────────────▼────────────┐
                   │    Telegram adapters    │
                   └────────────┬────────────┘
                                │
┌─────────────────┐   ┌─────────▼─────────┐   ┌─────────────────┐
│ Telegram Mini   │──▶│ Application layer │◀──│ HTTP / FastAPI  │
│ App / Frontend  │   │     use cases     │   │      API        │
└─────────────────┘   └─────────┬─────────┘   └─────────────────┘
                                │
                       ┌────────▼────────┐
                       │ Domain concepts │
                       │ + policies      │
                       └────────┬────────┘
                                │
                    ┌───────────▼───────────┐
                    │ Infrastructure / DB   │
                    │ repositories / I/O    │
                    └───────────┬───────────┘
                                │
                         ┌──────▼──────┐
                         │ SQL database │
                         └─────────────┘

                   ┌────────────────────────┐
                   │ Persistent jobs/outbox │
                   └───────────┬────────────┘
                               ▼
                        Background worker
                               │
                               ▼
                         Telegram gateway
```

The key rule is simple: **Telegram and HTTP transport code should translate inputs/outputs; it should not become the business layer.**

## Project structure

```text
telegram-bot-platform/
├── src/telegram_bot_platform/
│   ├── application/          # use cases, orchestration, feature services
│   ├── core/                 # settings, errors, logging, limits, DI container
│   ├── domain/               # stable platform concepts and policies
│   ├── infrastructure/       # DB models, sessions, repositories, external I/O
│   ├── telegram/             # modern Telegram adapters/modules
│   ├── web/                  # FastAPI + Mini App authentication/session
│   ├── workers/              # background processing
│   └── compat/              # preserved and decomposed original logic
├── frontend/                 # Telegram Mini App frontend
├── migrations/               # Alembic migrations
├── scripts/                  # operational/maintenance commands
├── tests/                    # behavior-focused tests
├── docs/                     # architecture, operations, security, roles
├── .github/                  # CI, issue templates, Dependabot, CODEOWNERS
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── .env.example
├── LICENSE
└── README.md
```

## Quick start

### 1. Create a bot

Create a bot with `@BotFather` and copy the token into `.env`. Keep the token out of git and secret logs.

### 2. Configure the environment

```bash
cp .env.example .env
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

At minimum set:

```env
TELEGRAM_BOT_TOKEN=...
TELEGRAM_BOT_USERNAME=...
APP_SECRET_KEY=<long-random-secret>
ADMIN_USER_IDS=<telegram-id>,<telegram-id>
```

For production, also set an HTTPS `WEB_APP_URL` and production database credentials.

### 3. Run locally

```bash
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Install runtime + development dependencies:

```bash
python -m pip install -e ".[dev]"
```

Run migrations:

```bash
platform-migrate
```

Run the API:

```bash
platform-web
```

Run the bot in another terminal:

```bash
platform-bot
```

Run the worker when you use scheduled work/outbox processing:

```bash
platform-worker
```

### 4. Run with Docker

```bash
docker compose up --build
```

The default web endpoint is `http://localhost:8000`.

## Multi-bot runtime

The platform uses one shared database, localization catalog, settings registry, audit trail, and Mini App. The modern core bot and the preserved admin/client/staff compatibility bots can run together without creating separate configuration silos. The compatibility runner is explicit so each token remains an independent Telegram update consumer:

```bash
platform-run-compat admin
platform-run-compat client
platform-run-compat staff
platform-run-compat auto-responder
```

Use the compatibility runners for the preserved admin/client/staff workflows. Each of those bots also exposes `/app`, which opens the same authenticated Mini App control plane according to the user role and bot module profile.

## Original feature parity

This release is based on the uploaded production code rather than a clean-room replacement. All **67 original Python modules** are represented under `src/telegram_bot_platform/compat`, with the original AST inventory of **88 classes** and **1,511 functions/methods** preserved. The largest classes were decomposed into focused mixins where that could be done without removing callable behavior.

Run the parity check at any time:

```bash
python scripts/verify_parity.py
```

The detailed inventory lives in [`docs/logic_parity_manifest.json`](docs/logic_parity_manifest.json) and the capability map in [`docs/FEATURE_PARITY.md`](docs/FEATURE_PARITY.md).

For the preserved runner topology, install the compatibility dependencies and use:

```bash
pip install -e ".[legacy,legacy-db]"
platform-run-compat admin
platform-run-compat client
platform-run-compat staff
platform-run-compat auto-responder
```

## Global bilingual control plane

All modern user-facing text is referenced by stable English localization keys. English and Persian values are kept as a pair, placeholders are validated for parity, and the administrator can edit every catalog entry from the Mini App under `Translations`. Compatibility strings are represented by the generated `legacy.text.*` catalog and are passed through `LocalizedTeleBot`, so the legacy bots use the same centralized localization/override mechanism instead of maintaining a second translation system.

Settings use stable English dot-keys such as `telegram.core.token`, `database.url`, `bots.client.token`, and `security.rate_limit_requests`. The Settings screen shows type, category, override state, secret masking, and whether a restart is required. Secrets are never returned in clear text by the settings API.

The Mini App session is authenticated from Telegram `initData`, signed server-side, and bound to the bot token that verified the request. The `/api/me` response also carries the effective bot module map, so the navigation reflects the capabilities configured for that bot.

## Environment configuration

Configuration is loaded through `pydantic-settings`. The application supports:

- `development`
- `testing`
- `staging`
- `production`

Use `.env` for local secrets. In CI/CD or production, prefer the platform's secret manager instead of committing secret files.

### Main variables

| Area | Variables |
| --- | --- |
| Application | `ENVIRONMENT`, `APP_NAME`, `APP_SECRET_KEY` |
| Telegram | `TELEGRAM_BOT_TOKEN`, `TELEGRAM_BOT_USERNAME`, `DEFAULT_CHANNEL_ID`, `ADMIN_USER_IDS` |
| Telegram limits | `TELEGRAM_CONCURRENT_UPDATES`, `TELEGRAM_CONNECTION_POOL_SIZE`, `TELEGRAM_*RATE*`, `TELEGRAM_TIMEOUT_SECONDS` |
| Access | `ADMIN_USER_IDS`, `RATE_LIMIT_REQUESTS`, `RATE_LIMIT_WINDOW_SECONDS` |
| Database | `DATABASE_URL`, `DB_POOL_SIZE`, `DB_MAX_OVERFLOW`, `DB_POOL_RECYCLE` |
| Mini App | `WEB_APP_URL`, `SESSION_*`, `CORS_ALLOWED_ORIGINS` |
| Compatibility bots | `BOT_ADMIN_TOKEN`, `BOT_CLIENT_TOKEN`, `BOT_STAFF_TOKEN`, `BOT_AUTO_RESPONDER_TOKEN` |
| Worker | `SCHEDULER_ENABLED`, `WORKER_*`, `OUTBOX_MAX_ATTEMPTS`, `AUTO_REPLY_*` |
| Logging | `LOG_LEVEL`, `LOG_JSON` |

See `.env.example` for the complete list.

## Roles and authorization

The platform provides a neutral role vocabulary for common bot deployments:

```text
owner
admin
manager
staff
support
moderator
analyst
client
member
```

The built-in `ADMIN_USER_IDS` configuration remains useful for first-time bootstrap/emergency administration. Persistent role assignments can then be managed by application services and repositories.

Authorization should use stable Telegram IDs and explicit permissions. Never infer authorization from a username or display name.

See [`docs/ROLES.md`](docs/ROLES.md).

## Mini App

The Mini App is served by the FastAPI application. The client sends Telegram's `initData` to `/api/auth/telegram` and receives a signed session cookie after server-side validation.

The backend:

1. Parses Telegram Web App initialization data.
2. Rejects malformed/duplicate fields.
3. Verifies the Telegram HMAC signature.
4. Validates `auth_date` freshness.
5. Creates/updates the corresponding user record.
6. Issues a time-limited signed session.

Do not use `initDataUnsafe` as an authentication source.

## Database and migrations

Alembic is the source of truth for schema evolution:

```bash
platform-migrate
```

The project intentionally avoids startup-time table destruction or implicit schema resets. Existing installations should move through explicit migrations.

To import neutral exported data:

```bash
platform-import export.json
```

See [`docs/DATA_IMPORT.md`](docs/DATA_IMPORT.md).

## Testing and quality

The same checks are run in GitHub Actions:

```bash
python -m compileall -q src scripts tests
ruff format --check .
ruff check .
mypy src/telegram_bot_platform
pip-audit
pytest
```

## Security

See [`docs/SECURITY.md`](docs/SECURITY.md) for the operational checklist and [`SECURITY.md`](.github/SECURITY.md) for vulnerability reporting guidance.

Never commit:

- Telegram bot tokens
- database passwords
- session/app secrets
- private API credentials
- personal data exports

## Extending the platform

New features should normally follow this path:

```text
Telegram/HTTP adapter
        ↓
Application service/use case
        ↓
Domain policy/value object
        ↓
Repository or external adapter
        ↓
Database / external service
```

Keep cross-cutting concerns such as configuration, logging, authentication, rate limiting, and resource lifecycle centralized.

For new Telegram functionality, use the official Telegram Bot API documentation as the behavioral source of truth.

## Production deployment notes

For a real deployment:

1. Provision a production database.
2. Generate unique production secrets.
3. Configure an HTTPS Mini App URL when using the Web App.
4. Run migrations before starting application processes.
5. Run exactly one polling bot consumer per bot token unless the update architecture has been deliberately redesigned for another strategy.
6. Keep the bot's Telegram permissions to the minimum required for the installed modules.
7. Back up the database using the database vendor's normal backup tools.
8. Monitor liveness/readiness endpoints and structured logs.

For detailed operational guidance, see [`docs/OPERATIONS.md`](docs/OPERATIONS.md).

## Telegram platform constraints

This project does not bypass Telegram permissions or protected-content restrictions. A bot can only perform operations the Bot API permits in the current chat/context and with the permissions granted to it.

## License

Released under the [MIT License](LICENSE).

## Maintainer

Maintained by [KouchakiDev](https://github.com/KouchakiDev).
