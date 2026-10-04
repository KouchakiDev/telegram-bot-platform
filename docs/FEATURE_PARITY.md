# Feature Parity Map

The original application was not reduced to a small generic bot. Its functional areas remain represented in the compatibility layer.

| Capability area | Preserved module family | Modern extension point |
| --- | --- | --- |
| Administrative operations | `compat.handlers.admin.*` | `application.services.admin_service` |
| Accounting and reporting | `compat.handlers.admin.accounting_handler`, `report_manager` | application reporting services |
| Content and advertisement workflows | `compat.handlers.admin.ad_manager`, `compat.handlers.client.ads_handler`, staff content handlers | `content_service` / repository layer |
| User/customer lifecycle | `compat.handlers.admin.client_manager`, client handlers | `user_service` / domain policies |
| Staff lifecycle | `compat.handlers.admin.staff_manager`, staff handlers | role and authorization services |
| Requests and workflow state | `compat.handlers.admin.request_manager_*`, client booking/request modules | application workflow services |
| Premium/extended features | `compat.handlers.client.premium.*` | feature modules / configurable plugins |
| Identity/verification workflows | `compat.handlers.client.verification`, staff verification handlers | authentication/verification services |
| Location services | `compat.utils.locations`, `location_utils` | infrastructure adapters |
| Media recovery/sending/watermarking | `compat.utils.media_recovery`, `media_sender`, `watermark` | media infrastructure adapters |
| Scheduling and notifications | `compat.utils.listing_publish_scheduler`, `notification_manager`, worker modules | worker/outbox services |
| Stateful workflow engine | `compat.utils.workflow_engine_*`, `workflow_steps` | application workflow engine |
| Persistent database operations | `compat.database.database_manager_*`, `compat.utils.database_manager` | SQLAlchemy repositories |
| Legacy runner topology | `compat.runners.*` | unified Telegram application / worker topology |

The table is intentionally capability-oriented rather than business-oriented. It describes what the source code can do without carrying the original product identity into the public platform.
