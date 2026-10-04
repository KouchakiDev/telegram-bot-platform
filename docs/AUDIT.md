# Baseline Audit and Preservation Record

The original uploaded project was audited before modernization. The source archive contained **67 Python modules**, approximately **49,318 Python lines**, **88 classes**, and **1,511 functions/methods** when counted with the Python AST.

The baseline also contained multiple Telegram bot runners, more than one Telegram framework, two independent database-manager implementations, large handler/manager classes, legacy runner copies, process/thread based state management, mixed synchronous and asynchronous I/O, hard-coded deployment values, and several broad exception handlers.

## Preservation policy

This release is **parity-first**. The original executable logic was transformed into a neutral compatibility namespace under `telegram_bot_platform.compat` and then decomposed into smaller mixins where the class boundary allowed a behavior-preserving extraction.

The migration does **not** use a small replacement application as a substitute for the original feature set. The compatibility tree contains the migrated production logic, while the modern typed application/domain/infrastructure layers provide the preferred foundation for new work.

## Major modernization actions

- Centralized configuration with environment-driven values and compatibility aliases.
- Removed real secrets and private production credentials from the distribution.
- Replaced product-specific branding and sensitive domain terminology with neutral platform terminology.
- Added explicit application, domain, infrastructure, Telegram, web, and worker boundaries.
- Added structured logging, rate limiting, signed Mini App sessions, and input validation.
- Added Alembic migrations, repository boundaries, Docker, health checks, and CI scaffolding.
- Decomposed the largest reusable classes into lifecycle, schema, data, settings, transaction, execution, navigation, and other focused mixins without reducing the original function/method inventory.

## Current parity measurement

The release inventory covers all 67 original Python modules. The destination tree contains the same **1,511 functions/methods** and at least the original **88 classes**; extra classes are decomposition mixins and modern platform components.

See `docs/logic_parity_manifest.json` and `scripts/verify_parity.py`.

## Runtime verification limits

The sandbox used for this migration did not contain every optional legacy dependency and could not perform a live Telegram or broker integration. Syntax validation, local import-target resolution, parity inventory verification, and the available automated test suite were executed locally. The networked GitHub CI workflow remains the final dependency-installation and integration-validation environment.
