# Control Plane

The platform has one shared control plane for the modern bot, compatibility bots, Mini App, worker, and administrative APIs.

## Localization

Core strings live in `resources/i18n/en.json` and `resources/i18n/fa.json`. Compatibility strings are indexed in `resources/i18n/compat_catalog.json`. Administrators can update both locale values in the Mini App. The backend writes overrides to `data/i18n_overrides.json`, and the Telegram compatibility adapter reloads the same values.

## Settings

Every supported runtime setting has a stable English key in `core/settings_catalog.py`. The Mini App displays the key, type, category, override status, secret status, and restart requirement. The database stores administrative overrides; settings marked `restart_required` become effective when the relevant process is restarted, which keeps the runtime configuration deterministic.

## Bot profiles

Bot profiles identify the core, admin, client, staff, and auto-responder tokens, usernames, default locale, enabled state, and module flags. Tokens are sourced from environment/secret configuration; the Mini App never exposes plaintext tokens.

## Mini App

All compatible bots expose `/app` and use the same Mini App URL. Authentication is server-side and the resulting session records the bot key that validated Telegram `initData`. The frontend uses the bot profile module map to render only enabled navigation areas, while administrative endpoints continue to enforce server-side authorization.

## Docker

Use `docker compose up --build` for the modern core. Add `--profile bots` to run the admin/client/staff compatibility bots and `--profile automation` for the auto-responder. All application containers share the `platform_data` volume for localization/runtime overrides.
