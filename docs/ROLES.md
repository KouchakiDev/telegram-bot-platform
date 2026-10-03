# Roles and Access Model

The platform includes a reusable role vocabulary so deployments can model common Telegram operations without hard-coding business-specific roles.

| Role | Typical use |
| --- | --- |
| `owner` | Full deployment ownership |
| `admin` | Administrative control |
| `manager` | Operational management |
| `staff` | Internal operational work |
| `support` | User/customer support |
| `moderator` | Content and community moderation |
| `analyst` | Reporting and read-oriented operations |
| `customer` | End-user/customer workflow |
| `member` | General participant |

Roles are stored in the database and are intentionally separate from Telegram usernames. Authorization should always use stable Telegram IDs and explicit role/permission checks.

The built-in configured-admin mechanism remains available for bootstrap and emergency access. Role-based authorization can be layered into application services as a deployment grows.
