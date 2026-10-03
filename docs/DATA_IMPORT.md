# Data Import Contract

The migration is intentionally non-destructive. Existing production data should be exported into a neutral JSON document and mapped explicitly instead of guessing the meaning of legacy columns.

Supported top-level keys are `users` and `content`. Example:

```json
{
  "users": [
    {"telegram_id": 123, "username": "example", "first_name": "Example", "language_code": "en"}
  ],
  "content": [
    {"title": "Announcement", "body": "Hello", "created_by": 123}
  ]
}
```

Run:

```bash
platform-import export.json
```

The importer uses the normal application services, so validation and transaction behavior stay in one place.
