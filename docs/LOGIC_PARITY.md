# Logic Parity and Migration Strategy

This release treats the original implementation as the behavior source of truth.

## What is preserved

All 67 original Python modules are represented in the compatibility tree. Large classes have been decomposed into smaller mixins where the extraction can be done without deleting methods or changing their callable contract.

The repository records the inventory in `docs/logic_parity_manifest.json`. The verification script aggregates all mapped destination modules and checks that every original class and function/method remains represented.

## Runtime architecture

```text
Legacy-compatible modules
        │
        ├── preserved feature logic
        ├── compatibility aliases
        └── existing workflows
                │
                ▼
Modern application/domain layer
                │
        ┌───────┼────────┐
        ▼       ▼        ▼
Telegram      Web     Workers
adapter       API     / jobs
        \       |       /
         \      |      /
          ▼     ▼     ▼
           Infrastructure
                 │
                 ▼
            Persistence
```

New development should target typed application services and repositories. Existing workflows should be migrated one bounded context at a time and removed from compatibility only after behavior-level tests demonstrate parity.

## Neutralization

The public distribution is domain-neutral. Product-specific branding and legacy domain terminology are not part of the public API. Existing behavior is preserved while labels and integration boundaries are generalized where technically safe.

## Non-destructive rule

A legacy implementation is retired only when its replacement has:

1. Equivalent behavior for the supported contract.
2. Database migration coverage where needed.
3. Integration tests for external side effects.
4. A documented migration path for active deployments.
