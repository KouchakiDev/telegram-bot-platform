# Changelog

## 2.2.0

- Added a shared bilingual English/Persian localization control plane with stable English keys.
- Added editable platform settings, translation pairs, bot profiles, and module registry to the Mini App.
- Added server-side bot-bound Mini App sessions and per-bot module-aware navigation.
- Added `/app` Mini App access to the preserved admin, client, and staff compatibility runners.
- Added a compatibility localization catalog and `LocalizedTeleBot` wrapper for centralized legacy text/button overrides.
- Added platform validation for locale parity, placeholders, frontend keys, compatibility catalog integrity, and settings descriptors.
- Added Docker Compose profiles for compatibility bots and auto-responder alongside the modern core services.


## 2.1.2 - 2026-10-04

- Replaced the placeholder Mini App with a complete responsive operations console.
- Added authenticated dashboard, content lifecycle management, scheduling, auto-reply management, chat module controls, team/role management, audit activity, and safe settings views.
- Added server-side API coverage for the Mini App without exposing secrets.
- Fixed the Mini App static-file path in the FastAPI application.
- Added consistent admin authorization for configured admins, database admins, and `admin`/`owner` roles.
- Added scheduled-job cancellation and repository listing support.
- Added security response headers and API no-store caching.
- Updated Telegram Mini App integration to use the current hosted Web App script and theme/safe-area behavior.


## 2.1.1 - 2026-10-03

- Globalized all remaining user-facing content for commerce, services, and general channel workflows.
- Removed legacy restricted wording and sensitive visual labels from compatibility UI text.
- Standardized all Python comments and docstrings to English.
- Preserved legacy field keys and callable behavior while moving their presentation to neutral configurable labels.

## 2.0.0 - 2026-10-03

- Added parity-first migration of the original production feature set.
- Preserved all 67 original Python modules in a neutral compatibility namespace.
- Decomposed large database, workflow, request, and runner classes into focused mixins without reducing the original callable inventory.
- Added a machine-checkable logic parity manifest and verification script.
- Kept secrets and private production data out of the public repository while retaining environment compatibility aliases.
- Added stable resource paths, GitHub CI metadata, Docker support, Mini App authentication, structured logging, and modern application boundaries.

## 1.1.0 - 2026-10-03

- Prepared the project for public GitHub distribution under `KouchakiDev`.
- Added reusable user roles and GitHub repository automation.

## 1.0.0

- Initial modular platform release.
