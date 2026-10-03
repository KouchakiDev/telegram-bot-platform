# Architecture Notes

## Boundary rules

### Presentation

Telegram handlers and FastAPI routes are adapters. They validate transport input, resolve dependencies, call application services, and map service results into transport responses.

### Application

Application services own use cases and orchestration. They are independent of Telegram update classes and HTTP request objects.

### Domain

Domain types describe stable platform concepts such as users, roles, chats, content, automation rules, scheduled work, and audit events. Business-specific concepts should be added here only when a deployment actually needs them.

### Infrastructure

Infrastructure contains SQLAlchemy models, repositories, transaction/session creation, Telegram gateways, and other external integrations.

## Authorization

The platform supports both bootstrap administrator IDs and persistent user roles. Role vocabulary is deliberately generic (`owner`, `admin`, `manager`, `staff`, `support`, `moderator`, `analyst`, `customer`, `member`). Usernames and display names are never authorization keys.

## Concurrency model

- Telegram update processing is asynchronous.
- Database operations use SQLAlchemy async sessions.
- The worker owns background outbox delivery and scheduled tasks.
- Long-running or blocking integrations should be moved behind `asyncio.to_thread()` or a dedicated process, depending on workload.
- No request creates unbounded tasks.

## State model

Persistent state belongs in the database. Process-local state is limited to bounded caches such as auto-reply rule caching. This prevents user state from disappearing on restart and makes horizontal API scaling practical.

## Extensibility

New workflows should generally be implemented as focused application services plus domain policies and infrastructure adapters. Telegram/HTTP modules remain thin so the same use case can be called from another interface such as a Mini App, scheduled task, CLI, or future integration.

## Data compatibility

The modernization intentionally avoids destructive schema operations. Existing application-specific storage is not coupled directly to the generic domain model. Data can be imported through explicit mapping/export tooling rather than by silently guessing field semantics.
