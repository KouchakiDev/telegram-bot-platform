(() => {
  "use strict";

  const tg = window.Telegram?.WebApp ?? null;
  const $ = (id) => document.getElementById(id);
  const state = {
    user: null, isAdmin: false, botKey: "core", locale: "en", translations: {}, botModules: {},
    view: "dashboard", dashboard: null, content: [], schedules: [], replies: [], chats: [], users: [], audit: [], settings: [], translationsRows: [], bots: [], modules: [], loaded: false,
    editingContentId: null, editingReplyId: null, translationFilter: ""
  };

  const navKeys = [
    ["dashboard", "nav.dashboard"], ["content", "nav.content"], ["scheduling", "nav.scheduling"],
    ["automation", "nav.automation"], ["chats", "nav.chats"], ["team", "nav.team"], ["activity", "nav.activity"],
    ["settings", "nav.settings"], ["translations", "nav.translations"], ["bots", "nav.bots"], ["modules", "nav.modules"]
  ];
  const icons = { dashboard: "⌂", content: "◫", scheduling: "◷", automation: "⌁", chats: "◌", team: "♟", activity: "↯", settings: "⚙", translations: "文", bots: "◈", modules: "◉" };
  const statusKey = { draft: "common.draft", published: "common.published", archived: "common.archived", pending: "common.pending", processing: "common.processing", completed: "common.completed", failed: "common.failed", cancelled: "common.cancelled", exact: "common.exact", contains: "common.contains", prefix: "common.prefix", regex: "common.regex" };

  function t(key, vars = {}) {
    let value = state.translations[key] ?? key;
    for (const [name, replacement] of Object.entries(vars)) value = value.replaceAll(`{${name}}`, String(replacement));
    return value;
  }
  function esc(value) { const el = document.createElement("span"); el.textContent = value == null ? "" : String(value); return el.innerHTML; }
  function formatDate(value) { if (!value) return t("common.not_available"); const d = new Date(value); return Number.isNaN(d.getTime()) ? String(value) : new Intl.DateTimeFormat(state.locale === "fa" ? "fa-IR" : "en-US", { dateStyle: "medium", timeStyle: "short" }).format(d); }
  function formatNumber(value) { return new Intl.NumberFormat(state.locale === "fa" ? "fa-IR" : "en-US").format(Number(value || 0)); }
  function keyForStatus(value) { return statusKey[value] ?? null; }
  function moduleLabel(key) { const item = state.modules.find(x => x.key === key); return item ? t(item.title_key) : t(`nav.${key}`); }
  function displayStatus(value) { const key = keyForStatus(value); return key ? t(key) : String(value ?? ""); }
  function toast(message, kind = "success") { const node = document.createElement("div"); node.className = `toast ${kind}`; node.textContent = message; $("toast-region").append(node); window.setTimeout(() => node.remove(), 3500); }
  function setLoading(active, messageKey = "common.loading") { $("loading-overlay").classList.toggle("hidden", !active); $("loading-overlay").setAttribute("aria-hidden", String(!active)); $("loading-text").textContent = t(messageKey); }

  async function api(url, options = {}) {
    const headers = { Accept: "application/json", ...(options.headers || {}) };
    if (options.body && !headers["Content-Type"]) headers["Content-Type"] = "application/json";
    const response = await fetch(url, { credentials: "same-origin", ...options, headers });
    let payload = null;
    try { payload = await response.json(); } catch (_) {}
    if (response.status === 401) { await logout(false); throw new Error(t("errors.session_expired")); }
    if (!response.ok) { const detail = payload?.detail; const message = state.translations[detail] ? t(detail) : (detail || t("errors.request_failed")); throw new Error(message); }
    return payload;
  }

  function refreshTelegramTheme() {
    if (!tg) return;
    tg.expand?.();
    tg.ready?.();
    const theme = tg.themeParams || {};
    for (const [name, value] of Object.entries(theme)) if (typeof value === "string") document.documentElement.style.setProperty(`--tg-${name.replaceAll("_", "-")}`, value);
  }

  function renderStaticLabels() {
    document.title = t("app.brand");
    $("brand-title").textContent = t("app.brand");
    $("page-subtitle").textContent = t("app.subtitle");
    $("connection-pill").textContent = t("common.connected");
    $("close-button").textContent = t("common.close");
    $("logout-button").textContent = t("common.sign_out");
    $("identity-role").textContent = state.isAdmin ? t("common.administrator") : t("common.member");
    $("sidebar").setAttribute("aria-label", t("nav.dashboard"));
    $("menu-button").setAttribute("aria-label", t("nav.dashboard"));
    document.querySelectorAll("[data-i18n]").forEach((node) => { node.textContent = t(node.dataset.i18n); });
    $("content-dialog-close").setAttribute("aria-label", t("common.close"));
    $("schedule-close").setAttribute("aria-label", t("common.close"));
    $("reply-close").setAttribute("aria-label", t("common.close"));
  }

  function renderLocaleSelect() {
    const select = $("locale-select"); select.replaceChildren();
    [["en", "common.english"], ["fa", "common.persian"]].forEach(([value, key]) => { const option = document.createElement("option"); option.value = value; option.textContent = t(key); select.append(option); });
    select.value = state.locale;
  }

  function renderNavigation() {
    const allowed = navKeys.filter(([view]) => {
      if (!state.isAdmin && !["dashboard", "content"].includes(view)) return false;
      const moduleKey = view === "chats" ? "chat_settings" : view === "team" ? "roles" : view === "activity" ? "audit" : view === "bots" ? "bot_profiles" : view === "modules" ? "module_registry" : view;
      return state.isAdmin ? state.botModules[moduleKey] !== false : ["dashboard", "content"].includes(view);
    });
    const nav = $("nav-list"); nav.replaceChildren();
    for (const [view, key] of allowed) {
      const button = document.createElement("button"); button.type = "button"; button.className = `nav-item${state.view === view ? " active" : ""}`; button.dataset.view = view;
      button.innerHTML = `<span class="nav-icon" aria-hidden="true">${icons[view]}</span><span class="nav-label">${esc(t(key))}</span>`;
      button.addEventListener("click", () => navigate(view)); nav.append(button);
    }
  }

  async function navigate(view) { state.view = view; $("sidebar").classList.remove("open"); renderNavigation(); await renderView(); }

  async function bootstrap() {
    refreshTelegramTheme(); setLoading(true, "common.authenticating");
    try {
      state.translations = (await api("/api/public/i18n?locale=en")).translations || {};
      let auth = null;
      if (tg?.initData) auth = await api("/api/auth/telegram", { method: "POST", body: JSON.stringify({ init_data: tg.initData }) });
      if (!auth) {
        state.locale = "en";
        throw new Error(t("auth.invalid"));
      }
      state.user = auth.user; state.isAdmin = await resolveAdmin(auth.user?.id); state.botKey = auth.bot_key || "core"; state.locale = auth.locale || "en"; state.translations = auth.translations || {}; state.botModules = auth.modules || {}; state.modules = (await api("/api/catalog")).modules || [];
      renderStaticLabels(); renderLocaleSelect(); renderNavigation(); updateIdentity();
      state.loaded = true; $("connection-pill").textContent = t("common.connected"); await renderView();
    } catch (error) {
      renderStaticLabels(); $("view-root").innerHTML = `<section class="card auth-card"><div class="eyebrow">${esc(t("auth.invalid"))}</div><h1>${esc(error.message)}</h1><p class="muted">${esc(t("errors.session_expired"))}</p></section>`; $("connection-pill").textContent = t("common.unavailable"); toast(error.message, "error");
    } finally { setLoading(false); }
  }

  async function resolveAdmin(id) { try { const me = await api("/api/me"); return Boolean(me.is_admin || id && me.id === id && (me.roles || []).includes("administrator")); } catch (_) { return false; } }
  function updateIdentity() { const name = [state.user?.first_name, state.user?.last_name].filter(Boolean).join(" ") || state.user?.username || ""; $("identity-name").textContent = name; $("avatar").textContent = (name[0] || "•").toUpperCase(); $("identity-role").textContent = state.isAdmin ? t("common.administrator") : t("common.member"); }

  async function renderView() {
    if (!state.loaded) return;
    renderNavigation();
    const renderers = { dashboard: renderDashboard, content: renderContent, scheduling: renderScheduling, automation: renderAutomation, chats: renderChats, team: renderTeam, activity: renderActivity, settings: renderSettings, translations: renderTranslations, bots: renderBots, modules: renderModules };
    await (renderers[state.view] || renderDashboard)();
    window.requestAnimationFrame(() => $("main-content").focus({ preventScroll: true }));
  }

  function pageHead(eyebrowKey, titleKey, descriptionKey) { return `<header class="page-head"><p class="eyebrow">${esc(t(eyebrowKey))}</p><h1>${esc(t(titleKey))}</h1>${descriptionKey ? `<p class="page-description">${esc(t(descriptionKey))}</p>` : ""}</header>`; }
  function section(titleKey, descriptionKey, actions = "", body = "") { return `<section class="card section"><div class="section-header"><div><h2>${esc(t(titleKey))}</h2>${descriptionKey ? `<p class="muted">${esc(t(descriptionKey))}</p>` : ""}</div><div class="actions">${actions}</div></div>${body}</section>`; }
  function stat(labelKey, value) { return `<article class="card stat-card"><div class="stat-label">${esc(t(labelKey))}</div><div class="stat-value">${esc(formatNumber(value))}</div></article>`; }
  function empty(key = "common.no_data") { return `<div class="empty-state">${esc(t(key))}</div>`; }

  async function renderDashboard() {
    setLoading(true); try {
      state.dashboard = await api("/api/dashboard"); const d = state.dashboard; const stats = d.stats || {};
      $("view-root").innerHTML = pageHead("dashboard.eyebrow", "dashboard.title", "dashboard.description") + `<div class="grid stats">${state.isAdmin ? stat("dashboard.users", stats.users) + stat("dashboard.chats", stats.chats) + stat("dashboard.content", stats.content) + stat("dashboard.audit_events", stats.audit_events) : stat("dashboard.content", stats.content)}</div>` +
        section("dashboard.published_content", "dashboard.latest_public_content", `<button class="secondary-button" data-nav="content">${esc(t("dashboard.open_content"))}</button>`, `<div class="list">${(d.recent_content || []).map(item => `<article class="list-item"><div class="item-top"><div><h3>${esc(item.title)}</h3><div class="meta-line"><span class="pill ${statusClass(item.status)}">${esc(displayStatus(item.status))}</span><span>${esc(formatDate(item.published_at || item.updated_at))}</span></div></div></div><div class="item-body">${esc(item.body)}</div></article>`).join("") || empty("content.empty")}</div>`) +
        `<div class="grid cards sectionless"><div>${section("dashboard.system_status", "dashboard.system_status_description", "", `<div class="list"><div class="list-item status-row"><span>${esc(t("dashboard.api"))}</span><span class="pill pill-success">${esc(t("common.ready"))}</span></div><div class="list-item status-row"><span>${esc(t("dashboard.database"))}</span><span class="pill ${d.ready ? "pill-success" : "pill-danger"}">${esc(d.ready ? t("common.ready") : t("common.unavailable"))}</span></div>${state.isAdmin ? `<div class="list-item status-row"><span>${esc(t("dashboard.scheduler"))}</span><span class="pill ${d.scheduler_enabled ? "pill-success" : "pill-warning"}">${esc(d.scheduler_enabled ? t("common.enabled") : t("common.disabled"))}</span></div>` : ""}</div>` )}</div><div>${section("dashboard.quick_actions", "dashboard.quick_actions_description", "", `<div class="actions vertical"><button class="primary-button" data-action="create-content">${esc(t("dashboard.create_content"))}</button>${state.isAdmin ? `<button class="secondary-button" data-action="schedule-message">${esc(t("dashboard.schedule_message"))}</button><button class="secondary-button" data-nav="automation">${esc(t("dashboard.manage_replies"))}</button>` : ""}</div>`)}</div></div>`;
      bindGlobalActions();
    } finally { setLoading(false); }
  }

  async function renderContent() { setLoading(true); try { state.content = (await api(state.isAdmin ? "/api/admin/content?limit=200" : "/api/content?limit=100")).items || []; $("view-root").innerHTML = pageHead("content.eyebrow", "content.title", state.isAdmin ? "content.admin_description" : "content.user_description") + section("content.library", "", state.isAdmin ? `<button class="primary-button" data-action="create-content">${esc(t("content.create_button"))}</button>` : "", `<div class="list">${state.content.map(renderContentItem).join("") || empty("content.empty")}</div>`); bindGlobalActions(); } finally { setLoading(false); } }
  function renderContentItem(item) { const adminActions = state.isAdmin ? `<div class="row-actions">${item.status !== "published" ? `<button class="secondary-button" data-edit-content="${item.id}">${esc(t("content.edit_button"))}</button><button class="secondary-button" data-publish-content="${item.id}">${esc(t("content.publish_button"))}</button>` : `<button class="secondary-button" data-archive-content="${item.id}">${esc(t("content.archive_button"))}</button>`}<button class="secondary-button" data-schedule-content="${item.id}">${esc(t("content.schedule_button"))}</button></div>` : ""; return `<article class="list-item"><div class="item-top"><div><h3>${esc(item.title)}</h3><div class="meta-line"><span class="pill ${statusClass(item.status)}">${esc(displayStatus(item.status))}</span><span>${esc(t("content.created"))} ${esc(formatDate(item.created_at))}</span><span>${esc(t("content.updated"))} ${esc(formatDate(item.updated_at))}</span></div></div>${adminActions}</div><div class="item-body">${esc(item.body)}</div></article>`; }

  async function renderScheduling() { setLoading(true); try { state.schedules = (await api("/api/admin/schedules?limit=200")).items || []; const list = state.schedules.map(item => { const p = item.payload || {}; const summary = item.kind === "send_message" ? `${p.chat_id}: ${p.text}` : `${t("scheduling.content_id")}: ${p.content_id}`; return `<article class="schedule-row"><div class="schedule-main"><strong>${esc(summary)}</strong><div class="meta-line"><span class="pill ${statusClass(item.status)}">${esc(displayStatus(item.status))}</span><span>${esc(item.kind)}</span><span>${esc(formatDate(item.run_at))}</span><span>${esc(formatNumber(item.attempts))}</span></div>${item.last_error ? `<div class="error-text">${esc(item.last_error)}</div>` : ""}</div><div class="row-actions">${["pending", "processing"].includes(item.status) ? `<button class="danger-button" data-cancel-job="${item.id}">${esc(t("scheduling.cancel_button"))}</button>` : ""}</div></article>`; }).join(""); $("view-root").innerHTML = pageHead("scheduling.eyebrow", "scheduling.title", "scheduling.description") + section("scheduling.jobs", "", `<button class="primary-button" data-action="schedule-message">${esc(t("scheduling.schedule_message"))}</button>`, `<div class="schedule-list">${list || empty("scheduling.empty")}</div>`); bindGlobalActions(); } finally { setLoading(false); } }

  async function renderAutomation() { setLoading(true); try { state.replies = (await api("/api/admin/auto-replies?limit=200")).items || []; const list = state.replies.map(item => `<article class="list-item"><div class="item-top"><div><h3>${esc(item.trigger)}</h3><div class="meta-line"><span class="pill ${item.enabled ? "pill-success" : "pill-muted"}">${esc(item.enabled ? t("common.enabled") : t("common.disabled"))}</span><span>${esc(displayStatus(item.match_mode))}</span><span>${esc(t("automation.priority"))}: ${esc(item.priority)}</span><span>${esc(t("automation.uses"))}: ${esc(formatNumber(item.usage_count))}</span></div></div><div class="row-actions"><button class="secondary-button" data-edit-reply="${item.id}">${esc(t("automation.edit_rule"))}</button><button class="secondary-button" data-toggle-reply="${item.id}">${esc(item.enabled ? t("common.disable") : t("common.enable"))}</button><button class="danger-button" data-delete-reply="${item.id}">${esc(t("automation.delete_rule"))}</button></div></div><div class="item-body">${esc(item.response)}</div></article>`).join(""); $("view-root").innerHTML = pageHead("automation.eyebrow", "automation.title", "automation.description") + section("automation.title", "", `<button class="primary-button" data-action="create-reply">${esc(t("automation.create_rule"))}</button>`, `<div class="list">${list || empty("automation.empty")}</div>`); bindGlobalActions(); } finally { setLoading(false); } }

  async function renderChats() { setLoading(true); try { state.chats = (await api("/api/admin/chats?limit=200")).items || []; $("view-root").innerHTML = pageHead("chats.eyebrow", "chats.title", "chats.description") + `<div class="list">${state.chats.map(chat => `<article class="list-item"><div class="item-top"><div><h3>${esc(chat.title || chat.username || chat.telegram_id)}</h3><div class="meta-line"><span>${esc(chat.chat_type)}</span><span>${esc(chat.telegram_id)}</span><span>${esc(chat.locale)}</span><span>${esc(chat.is_active ? t("common.enabled") : t("common.disabled"))}</span></div></div></div><div class="module-grid">${Object.entries(chat.modules || {}).map(([module, enabled]) => `<button class="module-chip ${enabled ? "enabled" : ""}" data-toggle-module="${chat.telegram_id}" data-module="${esc(module)}"><span>${esc(moduleLabel(module))}</span><span>${esc(enabled ? t("common.enabled") : t("common.disabled"))}</span></button>`).join("")}</div></article>`).join("") || empty("chats.empty")}</div>`; bindGlobalActions(); } finally { setLoading(false); } }

  async function renderTeam() { setLoading(true); try { state.users = (await api("/api/admin/users?limit=200")).items || []; $("view-root").innerHTML = pageHead("team.eyebrow", "team.title", "team.description") + `<div class="list">${state.users.map(user => `<article class="list-item"><div class="item-top"><div><h3>${esc([user.first_name, user.last_name].filter(Boolean).join(" ") || user.username || user.telegram_id)}</h3><div class="meta-line"><span>${esc(user.username ? `@${user.username}` : String(user.telegram_id))}</span><span>${esc(user.language_code || "")}</span><span>${esc(user.is_blocked ? t("common.disabled") : t("common.enabled"))}</span></div></div><div class="row-actions"><button class="secondary-button" data-edit-roles="${user.telegram_id}">${esc(t("team.roles"))}</button></div></div><div class="role-list">${(user.roles || []).map(r => `<span class="tag">${esc(r)}</span>`).join("") || empty()}</div></article>`).join("") || empty("team.empty")}</div>`; bindGlobalActions(); } finally { setLoading(false); } }

  async function renderActivity() { setLoading(true); try { state.audit = (await api("/api/admin/audit?limit=200")).items || []; $("view-root").innerHTML = pageHead("activity.eyebrow", "activity.title", "activity.description") + `<div class="table-wrap"><table><thead><tr><th>${esc(t("activity.actor"))}</th><th>${esc(t("activity.action"))}</th><th>${esc(t("activity.target"))}</th><th>${esc(t("activity.time"))}</th></tr></thead><tbody>${state.audit.map(row => `<tr><td>${esc(row.actor_telegram_id || t("common.not_available"))}</td><td>${esc(row.action)}</td><td>${esc(row.target || t("common.not_available"))}</td><td>${esc(formatDate(row.created_at))}</td></tr>`).join("") || `<tr><td colspan="4">${esc(t("activity.empty"))}</td></tr>`}</tbody></table></div>`; } finally { setLoading(false); } }

  async function renderSettings() { setLoading(true); try { state.settings = (await api("/api/admin/settings")).items || []; const grouped = {}; state.settings.forEach(item => (grouped[item.category] ||= []).push(item)); $("view-root").innerHTML = pageHead("settings.eyebrow", "settings.title", "settings.description") + Object.entries(grouped).map(([cat, items]) => `<section class="card section"><div class="section-header"><div><h2>${esc(t(`settings.category.${cat}`))}</h2></div></div><div class="settings-grid">${items.map(renderSetting).join("")}</div></section>`).join("") || empty("settings.empty"); bindGlobalActions(); } finally { setLoading(false); } }
  function renderSetting(item) {
    const value = item.value;
    let control = "";
    if (item.type === "bool") {
      control = `<label class="checkbox-label"><input type="checkbox" data-setting-key="${esc(item.key)}" data-setting-type="bool" data-secret="false" ${value ? "checked" : ""} ${item.editable ? "" : "disabled"}><span>${esc(t("settings.value"))}</span></label>`;
    } else {
      const type = item.secret ? "password" : (item.type === "int" || item.type === "float" ? "number" : "text");
      const step = item.type === "float" ? ' step="any"' : "";
      const inputValue = item.secret ? "" : Array.isArray(value) ? value.join(", ") : value ?? "";
      control = `<label><span>${esc(t("settings.value"))}</span><input type="${type}" data-setting-key="${esc(item.key)}" data-setting-type="${esc(item.type)}" data-secret="${item.secret}" value="${esc(inputValue)}"${step} ${item.editable ? "" : "disabled"} autocomplete="off"></label>`;
    }
    return `<article class="setting-card"><div class="setting-heading"><div><strong>${esc(item.key)}</strong><span class="setting-env">${esc(item.env_name)}</span></div>${item.secret ? `<span class="pill pill-warning">${esc(t("settings.secret"))}</span>` : ""}</div><p class="muted">${esc(item.description_key ? t(item.description_key) : "")}</p>${control}<div class="setting-footer"><span>${esc(item.restart_required ? t("settings.restart_required") : t("settings.live"))}</span><div class="actions"><button class="secondary-button" data-save-setting="${esc(item.key)}">${esc(t("common.save"))}</button>${item.overridden ? `<button class="ghost-button" data-reset-setting="${esc(item.key)}">${esc(t("settings.reset_to_default"))}</button>` : ""}</div></div></article>`;
  }

  async function renderTranslations() { setLoading(true); try { state.translationsRows = (await api("/api/admin/translations")).items || []; const q = state.translationFilter.toLowerCase(); const rows = state.translationsRows.filter(row => !q || `${row.key} ${row.en} ${row.fa}`.toLowerCase().includes(q)); $("view-root").innerHTML = pageHead("translations.eyebrow", "translations.title", "translations.description") + `<section class="card section"><div class="translation-toolbar"><input id="translation-search" placeholder="${esc(t("translations.search_placeholder"))}" value="${esc(state.translationFilter)}"><span class="muted">${esc(formatNumber(rows.length))}</span></div><div class="translation-list">${rows.map(row => `<article class="translation-row"><div class="translation-key">${esc(row.key)}<span>${esc(row.category)}</span></div><textarea data-en-key="${esc(row.key)}" rows="3">${esc(row.en)}</textarea><textarea data-fa-key="${esc(row.key)}" rows="3" dir="rtl">${esc(row.fa)}</textarea><div class="row-actions"><button class="primary-button" data-save-translation="${esc(row.key)}">${esc(t("common.save"))}</button><button class="ghost-button" data-reset-translation="${esc(row.key)}">${esc(t("translations.reset"))}</button></div></article>`).join("") || empty("translations.empty")}</div></section>`; bindGlobalActions(); $("translation-search").addEventListener("input", event => { state.translationFilter = event.target.value; renderTranslations(); }); } finally { setLoading(false); } }

  function moduleLabel(key) { const item = state.modules.find(x => x.key === key); return item ? t(item.title_key) : t(`nav.${key}`); }

  async function renderBots() { setLoading(true); try { state.bots = (await api("/api/admin/bots")).items || []; $("view-root").innerHTML = pageHead("bots.eyebrow", "bots.title", "bots.description") + `<div class="grid cards">${state.bots.map(renderBot).join("") || empty("bots.empty")}</div>`; bindGlobalActions(); } finally { setLoading(false); } }
  function renderBot(bot) { const moduleInputs = Object.entries(bot.modules || {}).map(([key, enabled]) => `<label class="checkbox-label"><input type="checkbox" data-bot-module="${esc(bot.bot_key)}" data-module-key="${esc(key)}" ${enabled ? "checked" : ""}><span>${esc(key)}</span></label>`).join(""); return `<article class="card bot-card"><div class="section-header"><div><p class="eyebrow">${esc(bot.bot_key)}</p><h2>${esc(t(bot.name_key))}</h2></div><span class="pill ${bot.configured ? "pill-success" : "pill-warning"}">${esc(bot.configured ? t("common.ready") : t("common.unavailable"))}</span></div><label><span>${esc(t("bots.username"))}</span><input data-bot-username="${esc(bot.bot_key)}" value="${esc(bot.username || "")}"></label><label><span>${esc(t("bots.default_locale"))}</span><select data-bot-locale="${esc(bot.bot_key)}"><option value="en">${esc(t("common.english"))}</option><option value="fa">${esc(t("common.persian"))}</option></select></label><label class="checkbox-label"><input type="checkbox" data-bot-enabled="${esc(bot.bot_key)}" ${bot.enabled ? "checked" : ""}><span>${esc(t("bots.enabled"))}</span></label><div class="module-grid">${moduleInputs}</div><div class="setting-footer"><button class="primary-button" data-save-bot="${esc(bot.bot_key)}">${esc(t("bots.save"))}</button>${bot.username ? `<button class="ghost-button" data-open-bot="${esc(bot.username)}">${esc(t("bots.open"))}</button>` : ""}</div></article>`; }

  async function renderModules() { setLoading(true); try { state.modules = (await api("/api/catalog")).modules || []; $("view-root").innerHTML = pageHead("modules.eyebrow", "modules.title", "modules.description") + `<div class="grid cards">${state.modules.map(item => `<article class="card module-card"><div class="section-header"><div><h2>${esc(t(item.title_key))}</h2><p class="muted">${esc(t(item.description_key))}</p></div><span class="pill ${item.source === "modern" ? "pill-success" : "pill-muted"}">${esc(item.source === "modern" ? t("modules.modern") : t("modules.compatibility"))}</span></div><div class="meta-line"><span>${esc(item.scope)}</span><span>${esc(item.key)}</span></div></article>`).join("")}</div>`; } finally { setLoading(false); } }

  function bindGlobalActions() {
    document.querySelectorAll("[data-nav]").forEach(node => node.onclick = () => navigate(node.dataset.nav));
    document.querySelectorAll("[data-action='create-content']").forEach(node => node.onclick = () => openContentDialog());
    document.querySelectorAll("[data-action='schedule-message']").forEach(node => node.onclick = () => openScheduleDialog());
    document.querySelectorAll("[data-action='create-reply']").forEach(node => node.onclick = () => openReplyDialog());
    document.querySelectorAll("[data-edit-content]").forEach(node => node.onclick = () => { const item = state.content.find(x => x.id == node.dataset.editContent); if (item) openContentDialog(item); });
    document.querySelectorAll("[data-publish-content]").forEach(node => node.onclick = () => mutate(`/api/content/${node.dataset.publishContent}/publish`, "POST", null, "common.publish"));
    document.querySelectorAll("[data-archive-content]").forEach(node => node.onclick = () => mutate(`/api/admin/content/${node.dataset.archiveContent}/archive`, "POST", null, "common.archive"));
    document.querySelectorAll("[data-schedule-content]").forEach(node => node.onclick = () => openScheduleDialog(Number(node.dataset.scheduleContent)));
    document.querySelectorAll("[data-cancel-job]").forEach(node => node.onclick = () => mutate(`/api/admin/schedules/${node.dataset.cancelJob}/cancel`, "POST", null, "common.cancel"));
    document.querySelectorAll("[data-edit-reply]").forEach(node => node.onclick = () => { const item = state.replies.find(x => x.id == node.dataset.editReply); if (item) openReplyDialog(item); });
    document.querySelectorAll("[data-toggle-reply]").forEach(node => node.onclick = () => mutate(`/api/admin/auto-replies/${node.dataset.toggleReply}/toggle`, "POST", null, "common.save"));
    document.querySelectorAll("[data-delete-reply]").forEach(node => node.onclick = () => mutate(`/api/admin/auto-replies/${node.dataset.deleteReply}`, "DELETE", null, "common.delete"));
    document.querySelectorAll("[data-toggle-module]").forEach(node => node.onclick = () => mutate(`/api/admin/chats/${node.dataset.toggleModule}/modules/${encodeURIComponent(node.dataset.module)}/toggle`, "POST", null, "common.save"));
    document.querySelectorAll("[data-edit-roles]").forEach(node => node.onclick = () => editRoles(Number(node.dataset.editRoles)));
    document.querySelectorAll("[data-save-setting]").forEach(node => node.onclick = () => saveSetting(node.dataset.saveSetting));
    document.querySelectorAll("[data-reset-setting]").forEach(node => node.onclick = () => resetSetting(node.dataset.resetSetting));
    document.querySelectorAll("[data-save-translation]").forEach(node => node.onclick = () => saveTranslation(node.dataset.saveTranslation));
    document.querySelectorAll("[data-reset-translation]").forEach(node => node.onclick = () => resetTranslation(node.dataset.resetTranslation));
    document.querySelectorAll("[data-save-bot]").forEach(node => node.onclick = () => saveBot(node.dataset.saveBot));
    document.querySelectorAll("[data-open-bot]").forEach(node => node.onclick = () => { const value = node.dataset.openBot; window.open(`https://t.me/${value.replace(/^@/, "")}`, "_blank", "noopener"); });
  }

  async function mutate(url, method, body, successKey) { try { await api(url, { method, ...(body == null ? {} : { body: JSON.stringify(body) }) }); toast(t(successKey)); await renderView(); } catch (e) { toast(e.message, "error"); } }

  function openContentDialog(item = null) { state.editingContentId = item?.id || null; $("content-dialog-title").textContent = t(item ? "content.edit_title" : "content.create_title"); $("content-dialog-eyebrow").textContent = t("content.eyebrow"); $("content-title").value = item?.title || ""; $("content-body").value = item?.body || ""; $("content-submit").textContent = t(item ? "content.save_button" : "content.create_button"); $("content-cancel").textContent = t("common.cancel"); $("content-dialog").showModal(); }
  function closeDialog(id) { $(id).close(); }
  async function submitContent(event) { event.preventDefault(); const body = { title: $("content-title").value.trim(), body: $("content-body").value.trim() }; try { if (state.editingContentId) await api(`/api/admin/content/${state.editingContentId}`, { method: "PUT", body: JSON.stringify(body) }); else await api("/api/content", { method: "POST", body: JSON.stringify(body) }); closeDialog("content-dialog"); toast(t("common.saved")); await renderContent(); } catch (e) { toast(e.message, "error"); } }

  function openScheduleDialog(contentId = null) { $("schedule-dialog-title").textContent = t(contentId ? "scheduling.schedule_content" : "scheduling.schedule_message"); $("schedule-submit").textContent = t("common.save"); $("schedule-cancel").textContent = t("common.cancel"); $("schedule-content-id").value = contentId || ""; $("schedule-content-input").value = contentId || ""; $("schedule-text").value = ""; $("schedule-chat-id").value = ""; $("schedule-target-chat-id").value = ""; $("schedule-parse-mode").value = ""; const now = new Date(Date.now() + 10 * 60 * 1000); now.setSeconds(0, 0); $("schedule-run-at").value = new Date(now.getTime() - now.getTimezoneOffset() * 60000).toISOString().slice(0, 16); $("schedule-dialog").showModal(); }
  async function submitSchedule(event) { event.preventDefault(); try { const run_at = new Date($("schedule-run-at").value).toISOString(); const contentId = Number($("schedule-content-input").value || 0); if (contentId) await api("/api/admin/schedule-content", { method: "POST", body: JSON.stringify({ content_id: contentId, run_at, target_chat_id: $("schedule-target-chat-id").value ? Number($("schedule-target-chat-id").value) : null }) }); else await api("/api/admin/schedule-message", { method: "POST", body: JSON.stringify({ chat_id: Number($("schedule-chat-id").value), text: $("schedule-text").value.trim(), run_at, parse_mode: $("schedule-parse-mode").value.trim() || null }) }); closeDialog("schedule-dialog"); toast(t("common.saved")); await renderScheduling(); } catch (e) { toast(e.message, "error"); } }

  function openReplyDialog(item = null) { state.editingReplyId = item?.id || null; $("reply-dialog-title").textContent = t(item ? "automation.edit_rule" : "automation.create_rule"); $("reply-trigger").value = item?.trigger || ""; $("reply-response").value = item?.response || ""; $("reply-priority").value = item?.priority ?? 100; $("reply-enabled").checked = item ? Boolean(item.enabled) : true; const select = $("reply-match-mode"); select.replaceChildren(); ["contains", "exact", "prefix", "regex"].forEach(v => { const option = document.createElement("option"); option.value = v; option.textContent = statusKey[v] ? t(statusKey[v]) : v; if (v === item?.match_mode) option.selected = true; select.append(option); }); $("reply-submit").textContent = t("common.save"); $("reply-cancel").textContent = t("common.cancel"); $("reply-dialog").showModal(); }
  async function submitReply(event) { event.preventDefault(); const payload = { trigger: $("reply-trigger").value.trim(), response: $("reply-response").value.trim(), match_mode: $("reply-match-mode").value, priority: Number($("reply-priority").value), enabled: $("reply-enabled").checked }; try { await api(state.editingReplyId ? `/api/admin/auto-replies/${state.editingReplyId}` : "/api/admin/auto-replies", { method: state.editingReplyId ? "PUT" : "POST", body: JSON.stringify(payload) }); closeDialog("reply-dialog"); toast(t("common.saved")); await renderAutomation(); } catch (e) { toast(e.message, "error"); } }

  async function editRoles(id) { const user = state.users.find(x => x.telegram_id === id); if (!user) return; const raw = window.prompt(t("team.role_help"), (user.roles || []).join(", ")); if (raw == null) return; const roles = raw.split(",").map(x => x.trim()).filter(Boolean); try { await api(`/api/admin/users/${id}/roles`, { method: "PUT", body: JSON.stringify({ roles }) }); toast(t("common.saved")); await renderTeam(); } catch (e) { toast(e.message, "error"); } }

  async function saveSetting(key) { const input = document.querySelector(`[data-setting-key="${CSS.escape(key)}"]`); if (!input) return; if (input.dataset.secret === "true" && !input.value) return toast(t("common.no_data"), "error"); let value = input.dataset.settingType === "bool" ? input.checked : input.value; try { await api(`/api/admin/settings/${encodeURIComponent(key)}`, { method: "PUT", body: JSON.stringify({ value }) }); toast(t("common.saved")); await renderSettings(); } catch (e) { toast(e.message, "error"); } }
  async function resetSetting(key) { try { await api(`/api/admin/settings/${encodeURIComponent(key)}`, { method: "DELETE" }); toast(t("common.reset")); await renderSettings(); } catch (e) { toast(e.message, "error"); } }
  async function saveTranslation(key) { const en = document.querySelector(`[data-en-key="${CSS.escape(key)}"]`)?.value; const fa = document.querySelector(`[data-fa-key="${CSS.escape(key)}"]`)?.value; if (!en || !fa) return; try { await api(`/api/admin/translations/${encodeURIComponent(key)}`, { method: "PUT", body: JSON.stringify({ en, fa }) }); toast(t("common.saved")); state.translationsRows = (await api("/api/admin/translations")).items || []; await renderTranslations(); } catch (e) { toast(e.message, "error"); } }
  async function resetTranslation(key) { try { await api(`/api/admin/translations/${encodeURIComponent(key)}`, { method: "DELETE" }); toast(t("common.reset")); state.translationsRows = (await api("/api/admin/translations")).items || []; await renderTranslations(); } catch (e) { toast(e.message, "error"); } }
  async function saveBot(botKey) { const bot = state.bots.find(x => x.bot_key === botKey); if (!bot) return; const username = document.querySelector(`[data-bot-username="${CSS.escape(botKey)}"]`).value.trim() || null; const locale = document.querySelector(`[data-bot-locale="${CSS.escape(botKey)}"]`).value; const enabled = document.querySelector(`[data-bot-enabled="${CSS.escape(botKey)}"]`).checked; const modules = {}; document.querySelectorAll(`[data-bot-module="${CSS.escape(botKey)}"]`).forEach(node => modules[node.dataset.moduleKey] = node.checked); try { await api(`/api/admin/bots/${encodeURIComponent(botKey)}`, { method: "PUT", body: JSON.stringify({ username, default_locale: locale, enabled, modules }) }); toast(t("common.saved")); await renderBots(); } catch (e) { toast(e.message, "error"); } }

  async function logout(notify = true) { try { await api("/api/auth/logout", { method: "POST" }); } catch (_) {} document.cookie = ""; if (notify) toast(t("common.sign_out")); window.setTimeout(() => window.location.reload(), 150); }
  function statusClass(value) { return { published: "pill-success", completed: "pill-success", enabled: "pill-success", draft: "pill-muted", pending: "pill-warning", processing: "pill-warning", archived: "pill-muted", failed: "pill-danger", cancelled: "pill-muted" }[value] || "pill-muted"; }

  $("menu-button").addEventListener("click", () => $("sidebar").classList.toggle("open"));
  $("close-button").addEventListener("click", () => tg?.close?.());
  $("logout-button").addEventListener("click", () => logout(true));
  $("locale-select").addEventListener("change", async (event) => { state.locale = event.target.value; const bundle = await api(`/api/i18n?locale=${encodeURIComponent(state.locale)}`); state.translations = bundle.translations || {}; document.documentElement.lang = state.locale; document.documentElement.dir = state.locale === "fa" ? "rtl" : "ltr"; renderStaticLabels(); renderLocaleSelect(); updateIdentity(); await renderView(); });
  $("content-form").addEventListener("submit", submitContent); $("content-cancel").addEventListener("click", () => closeDialog("content-dialog")); $("content-dialog-close").addEventListener("click", () => closeDialog("content-dialog"));
  $("schedule-form").addEventListener("submit", submitSchedule); $("schedule-cancel").addEventListener("click", () => closeDialog("schedule-dialog")); $("schedule-close").addEventListener("click", () => closeDialog("schedule-dialog"));
  $("reply-form").addEventListener("submit", submitReply); $("reply-cancel").addEventListener("click", () => closeDialog("reply-dialog")); $("reply-close").addEventListener("click", () => closeDialog("reply-dialog"));
  tg?.onEvent?.("themeChanged", refreshTelegramTheme); tg?.onEvent?.("viewportChanged", () => tg.expand?.());
  bootstrap();
})();
