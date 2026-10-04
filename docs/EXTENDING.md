# Extending the Platform

The project is a foundation rather than a collection of business-specific features. Add new capabilities as modules so one deployment can stay small while another can grow into a larger Telegram application.

## Recommended flow

```text
Telegram handler / API route
        ↓
Application service
        ↓
Domain policy / value object
        ↓
Repository or external adapter
        ↓
Database / external system
```

## Adding a Telegram feature

Keep transport concerns inside `src/telegram_bot_platform/telegram/modules/`. A handler should parse Telegram input, call an application service, and format the result. It should not open database connections or encode business rules.

## Adding a business capability

Create a focused application service under `src/telegram_bot_platform/application/services/` and keep stable rules in `src/telegram_bot_platform/domain/`. Add persistence only when state must survive a restart or be shared across processes.

## Adding an external integration

Place client/adaptor code in `src/telegram_bot_platform/infrastructure/`. Define a small interface at the application boundary when the business logic should be independent of the provider. Add timeouts, retries only where safe, and explicit failure handling.

## Adding a scheduled workflow

Prefer a durable `ScheduledJob` or outbox record over an in-memory task. Make the payload versionable and make the external action idempotent where practical.

## Adding a Mini App screen

Serve the static frontend through the existing FastAPI boundary and add a dedicated API endpoint. Authenticate with the server-created session after valisocial_service Telegram `initData`; do not trust browser-provided identity fields.

## Adding permissions

Use stable Telegram IDs and explicit roles/permissions. Do not use usernames as authorization keys. For chat-scoped operations, validate both application authorization and Telegram's actual permissions for that chat.
