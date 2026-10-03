# Feature Catalog

The base platform is deliberately reusable. Common capabilities are grouped below so a deployment can enable/extend the pieces it needs.

| Capability | Base status | Extension point |
| --- | --- | --- |
| User registry | Included | `UserService` / user repository |
| Customer/member roles | Included | `RoleService` |
| Staff/admin roles | Included | `RoleService` + admin policy |
| Chat registry | Included | chat repository/settings |
| Content lifecycle | Included | `ContentService` |
| Auto replies | Included | `AutomationService` |
| Scheduling | Included | scheduled jobs |
| Notification outbox | Included | outbox worker |
| Audit trail | Included | `AuditRepository` |
| REST API | Included | FastAPI routes |
| Telegram Mini App | Included | `frontend/` + API |
| Telegram authentication | Included | `telegram_auth.py` |
| Docker deployment | Included | `Dockerfile` / Compose |
| Role vocabulary | Included | persistent user roles |
| Payments | Adapter-ready, not domain-specific | add provider module |
| CRM/business workflows | Adapter-ready, not domain-specific | application modules |
| AI/LLM features | Adapter-ready, not domain-specific | external service adapter |
| Broadcast campaigns | Adapter-ready, not domain-specific | campaign module + worker |
| Multi-bot control plane | Not included by default | separate orchestration layer |

The goal is to avoid shipping every possible business feature into the core. A clean platform should make those features easy to add without forcing them onto every bot.
