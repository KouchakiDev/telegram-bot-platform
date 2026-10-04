from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True, slots=True)
class ModuleDescriptor:
    key: str
    title_key: str
    description_key: str
    scope: str
    source: str
    default_enabled: bool = True


MODULES: tuple[ModuleDescriptor, ...] = (
    ModuleDescriptor("dashboard", "nav.dashboard", "dashboard.description", "platform", "modern"),
    ModuleDescriptor("content", "nav.content", "content.admin_description", "platform/chat", "modern"),
    ModuleDescriptor("scheduling", "nav.scheduling", "scheduling.description", "platform", "modern"),
    ModuleDescriptor("automation", "nav.automation", "automation.description", "platform/chat", "modern"),
    ModuleDescriptor("chat_settings", "nav.chats", "chats.description", "chat", "modern"),
    ModuleDescriptor("roles", "nav.team", "team.description", "platform", "modern"),
    ModuleDescriptor("audit", "nav.activity", "activity.description", "platform", "modern"),
    ModuleDescriptor("settings", "nav.settings", "settings.description", "platform", "modern"),
    ModuleDescriptor("translations", "nav.translations", "translations.description", "platform", "modern"),
    ModuleDescriptor("bot_profiles", "nav.bots", "bots.description", "platform", "modern"),
    ModuleDescriptor("module_registry", "nav.modules", "modules.description", "platform", "modern"),
    ModuleDescriptor("legacy_admin", "bots.admin", "bots.description", "bot", "compatibility"),
    ModuleDescriptor("legacy_client", "bots.client", "bots.description", "bot", "compatibility"),
    ModuleDescriptor("legacy_staff", "bots.staff", "bots.description", "bot", "compatibility"),
    ModuleDescriptor("legacy_auto_responder", "bots.auto_responder", "bots.description", "bot", "compatibility"),
)


def catalog_dict() -> list[dict[str, object]]:
    return [asdict(item) for item in MODULES]
