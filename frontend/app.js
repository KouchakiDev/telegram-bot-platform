(() => {
  "use strict";

  const tg = window.Telegram?.WebApp ?? null;
  const state = {
    user: null,
    isAdmin: false,
    view: "dashboard",
    dashboard: null,
    content: [],
    replies: [],
    schedules: [],
    chats: [],
    users: [],
    audit: [],
  };

  const $ = (id) => document.getElementById(id);
  const viewRoot = $("view-root");
  const navList = $("nav-list");
  const sidebar = $("sidebar");

  const icons = {
    dashboard: "⌂",
    content: "▤",
    schedule: "◷",
    automation: "↯",
    chats: "◈",
    team: "◎",
    activity: "◌",
    settings: "⚙",
  };

  function escapeHtml(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function formatDate(value) {
    if (!value) return "—";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return "—";
    return new Intl.DateTimeFormat(undefined, {
      dateStyle: "medium",
      timeStyle: "short",
    }).format(date);
  }

  function formatNumber(value) {
    return new Intl.NumberFormat().format(Number(value ?? 0));
  }

  function roleLabel(roles = []) {
    if (!roles.length) return "Member";
    return roles.map((role) => role.charAt(0).toUpperCase() + role.slice(1)).join(" · ");
  }

  function statusClass(status) {
    const map = {
      published: "pill-success",
      draft: "pill-muted",
      pending_review: "pill-warning",
      archived: "pill-danger",
      pending: "pill-info",
      processing: "pill-warning",
      completed: "pill-success",
      failed: "pill-danger",
      cancelled: "pill-muted",
      enabled: "pill-success",
      disabled: "pill-muted",
    };
    return map[status] || "pill-muted";
  }

  function toast(message, kind = "info") {
    const node = document.createElement("div");
    node.className = `toast${kind === "error" ? " error" : ""}`;
    node.textContent = message;
    $("toast-region").append(node);
    window.setTimeout(() => node.remove(), 3400);
  }

  function setLoading(loading, message = "Loading…") {
    const overlay = $("loading-overlay");
    $("loading-text").textContent = message;
    overlay.classList.toggle("hidden", !loading);
    overlay.setAttribute("aria-hidden", String(!loading));
  }

  async function api(path, options = {}) {
    const response = await fetch(path, {
      credentials: "include",
      headers: { "Content-Type": "application/json", ...(options.headers || {}) },
      ...options,
    });
    if (!response.ok) {
      let detail = `Request failed (${response.status})`;
      try {
        const payload = await response.json();
        detail = payload.detail || detail;
      } catch (_) {}
      const error = new Error(detail);
      error.status = response.status;
      throw error;
    }
    if (response.status === 204) return null;
    return response.json();
  }

  function initTelegram() {
    if (!tg) throw new Error("Open this Mini App inside Telegram.");
    tg.ready();
    tg.expand?.();
    tg.enableVerticalSwipes?.();
    tg.setHeaderColor?.(tg.themeParams?.bg_color || "bg_color");
    tg.setBackgroundColor?.(tg.themeParams?.bg_color || "bg_color");
  }

  function refreshTheme() {
    if (!tg) return;
    const theme = tg.themeParams || {};
    const root = document.documentElement;
    for (const [key, value] of Object.entries(theme)) {
      if (typeof value === "string") root.style.setProperty(`--tg-theme-${key.replaceAll("_", "-")}`, value);
    }
  }

  function buildNavigation() {
    const entries = [
      ["dashboard", "Dashboard"],
      ["content", "Content"],
    ];
    if (state.isAdmin) {
      entries.push(["schedule", "Scheduling"]);
      entries.push(["automation", "Auto replies"]);
      entries.push(["chats", "Chats"]);
      entries.push(["team", "Team"]);
      entries.push(["activity", "Activity"]);
      entries.push(["settings", "Settings"]);
    }
    navList.replaceChildren();
    for (const [key, label] of entries) {
      const button = document.createElement("button");
      button.className = "nav-item";
      button.dataset.view = key;
      button.type = "button";
      button.innerHTML = `<span class="nav-icon" aria-hidden="true">${icons[key]}</span><span class="nav-label">${label}</span>`;
      button.addEventListener("click", () => navigate(key));
      navList.append(button);
    }
  }

  function navigate(view) {
    state.view = view;
    sidebar.classList.remove("open");
    updateNavState();
    renderView().catch((error) => handleError(error));
  }

  function updateNavState() {
    document.querySelectorAll(".nav-item").forEach((node) => {
      node.classList.toggle("active", node.dataset.view === state.view);
    });
  }

  function pageHead(eyebrow, title, description = "") {
    return `<div class="page-head"><p class="eyebrow">${escapeHtml(eyebrow)}</p><h1>${escapeHtml(title)}</h1>${description ? `<p class="page-description">${escapeHtml(description)}</p>` : ""}</div>`;
  }

  function sectionHeader(title, description = "", actions = "") {
    return `<div class="section-header"><div><h2>${escapeHtml(title)}</h2>${description ? `<p class="muted">${escapeHtml(description)}</p>` : ""}</div><div class="actions">${actions}</div></div>`;
  }

  function statCard(label, value, hint = "") {
    return `<article class="card stat-card"><div class="stat-label">${escapeHtml(label)}</div><div class="stat-value">${escapeHtml(value)}</div><div class="stat-hint">${escapeHtml(hint)}</div></article>`;
  }

  function renderEmpty(message) {
    return `<div class="empty-state">${escapeHtml(message)}</div>`;
  }

  async function renderView() {
    updateNavState();
    const renderers = {
      dashboard: renderDashboard,
      content: renderContent,
      schedule: renderSchedule,
      automation: renderAutomation,
      chats: renderChats,
      team: renderTeam,
      activity: renderActivity,
      settings: renderSettings,
    };
    const renderer = renderers[state.view] || renderDashboard;
    await renderer();
    window.requestAnimationFrame(() => $("main-content").focus({ preventScroll: true }));
  }

  async function loadDashboard() {
    state.dashboard = await api("/api/dashboard");
  }

  async function renderDashboard() {
    viewRoot.innerHTML = pageHead("Overview", `Welcome, ${state.user?.first_name || "there"}`, "Control your Telegram platform from one place.");
    try {
      if (!state.dashboard) await loadDashboard();
      const d = state.dashboard;
      const adminStats = state.isAdmin ? `
        <div class="grid stats section">
          ${statCard("Users", formatNumber(d.stats.users))}
          ${statCard("Chats", formatNumber(d.stats.chats))}
          ${statCard("Content", formatNumber(d.stats.content))}
          ${statCard("Audit events", formatNumber(d.stats.audit_events))}
        </div>` : "";
      const contentRows = (d.recent_content || []).map((item) => `
        <article class="list-item">
          <div class="item-top"><div><h3>${escapeHtml(item.title)}</h3><div class="meta-line"><span class="pill ${statusClass(item.status)}">${escapeHtml(item.status)}</span><span>${formatDate(item.published_at || item.updated_at || item.created_at)}</span></div></div></div>
          <div class="item-body">${escapeHtml(item.body)}</div>
        </article>`).join("");
      viewRoot.innerHTML += `
        ${adminStats}
        <div class="grid cards section">
          <article class="card">
            ${sectionHeader("Published content", "Your latest public content.", `<button class="secondary-button" data-action="navigate-content">Open content</button>`)}
            <div class="list">${contentRows || renderEmpty("No published content yet.")}</div>
          </article>
          <article class="card">
            ${sectionHeader("System status", "Runtime and automation state.")}
            <div class="list">
              <div class="list-item"><div class="stat-row" style="justify-content:space-between"><span>API</span><span class="pill pill-success">Online</span></div></div>
              <div class="list-item"><div class="stat-row" style="justify-content:space-between"><span>Database</span><span class="pill ${d.ready ? "pill-success" : "pill-danger"}">${d.ready ? "Ready" : "Unavailable"}</span></div></div>
              ${state.isAdmin ? `<div class="list-item"><div class="stat-row" style="justify-content:space-between"><span>Scheduler</span><span class="pill ${d.scheduler_enabled ? "pill-success" : "pill-warning"}">${d.scheduler_enabled ? "Enabled" : "Disabled"}</span></div></div>` : ""}
            </div>
          </article>
          <article class="card">
            ${sectionHeader("Quick actions", "Common operations for admins.")}
            <div class="actions">
              <button class="primary-button" data-action="quick-create-content">Create content</button>
              ${state.isAdmin ? `<button class="secondary-button" data-action="quick-schedule">Schedule message</button><button class="secondary-button" data-action="quick-replies">Manage auto replies</button>` : ""}
            </div>
          </article>
        </div>`;
      bindDataActions();
    } catch (error) {
      viewRoot.innerHTML += `<div class="card section">${renderEmpty(error.message)}</div>`;
      handleError(error, false);
    }
  }

  async function renderContent() {
    setLoading(true, "Loading content…");
    try {
      state.content = (await api(state.isAdmin ? "/api/admin/content" : "/api/content?limit=50")).items || [];
      viewRoot.innerHTML = pageHead("Content", "Content library", state.isAdmin ? "Create, edit, publish, archive and schedule content." : "Browse published content.");
      const actions = state.isAdmin ? `<button class="primary-button" data-action="create-content">Create content</button>` : "";
      const list = state.content.map((item) => `
        <article class="list-item">
          <div class="item-top">
            <div>
              <h3>${escapeHtml(item.title)}</h3>
              <div class="meta-line"><span class="pill ${statusClass(item.status)}">${escapeHtml(item.status)}</span><span>Created ${formatDate(item.created_at)}</span><span>Updated ${formatDate(item.updated_at)}</span></div>
            </div>
            ${state.isAdmin ? `<div class="row-actions"><button class="secondary-button" data-content-edit="${item.id}" ${item.status === "published" ? "disabled" : ""}>Edit</button>${item.status !== "published" ? `<button class="secondary-button" data-content-publish="${item.id}">Publish</button>` : `<button class="secondary-button" data-content-archive="${item.id}">Archive</button>`}<button class="secondary-button" data-content-schedule="${item.id}">Schedule</button></div>` : ""}
          </div>
          <div class="item-body">${escapeHtml(item.body)}</div>
        </article>`).join("");
      viewRoot.innerHTML += `<section class="card section">${sectionHeader("Library", `${state.content.length} item(s)`, actions)}<div class="list">${list || renderEmpty("No content is available.")}</div></section>`;
      bindDataActions();
    } finally {
      setLoading(false);
    }
  }

  async function renderSchedule() {
    setLoading(true, "Loading schedule…");
    try {
      state.schedules = (await api("/api/admin/schedules?limit=100")).items || [];
      viewRoot.innerHTML = pageHead("Scheduling", "Delivery queue", "Schedule messages and content publications for later delivery.");
      const list = state.schedules.map((item) => {
        const payload = item.payload || {};
        const summary = item.kind === "send_message" ? `${payload.chat_id}: ${payload.text}` : `Content #${payload.content_id}`;
        const canCancel = ["pending", "processing"].includes(item.status);
        return `<div class="schedule-row"><div class="schedule-main"><strong>${escapeHtml(summary)}</strong><div class="schedule-meta"><span class="pill ${statusClass(item.status)}">${escapeHtml(item.status)}</span><span>${escapeHtml(item.kind)}</span><span>Run at ${formatDate(item.run_at)}</span><span>Attempts ${formatNumber(item.attempts)}</span></div>${item.last_error ? `<div class="meta-line">${escapeHtml(item.last_error)}</div>` : ""}</div><div class="row-actions">${canCancel ? `<button class="danger-button" data-schedule-cancel="${item.id}">Cancel</button>` : ""}</div></div>`;
      }).join("");
      viewRoot.innerHTML += `<section class="card section">${sectionHeader("Scheduled jobs", `${state.schedules.length} job(s)`, `<button class="primary-button" data-action="schedule-message">Schedule message</button>`)}<div class="schedule-list">${list || renderEmpty("No scheduled jobs.")}</div></section>`;
      bindDataActions();
    } finally {
      setLoading(false);
    }
  }

  async function renderAutomation() {
    setLoading(true, "Loading automation…");
    try {
      state.replies = (await api("/api/admin/auto-replies?limit=100")).items || [];
      viewRoot.innerHTML = pageHead("Automation", "Auto reply rules", "Control deterministic reply rules used by the bot.");
      const rows = state.replies.map((item) => `
        <div class="list-item">
          <div class="item-top">
            <div><h3>${escapeHtml(item.trigger)}</h3><div class="meta-line"><span class="pill ${item.enabled ? "pill-success" : "pill-muted"}">${item.enabled ? "Enabled" : "Disabled"}</span><span>${escapeHtml(item.match_mode)}</span><span>Priority ${item.priority}</span><span>${formatNumber(item.usage_count)} uses</span></div></div>
            <div class="row-actions"><button class="secondary-button" data-reply-edit="${item.id}">Edit</button><button class="secondary-button" data-reply-toggle="${item.id}">${item.enabled ? "Disable" : "Enable"}</button><button class="danger-button" data-reply-delete="${item.id}">Delete</button></div>
          </div>
          <div class="item-body">${escapeHtml(item.response)}</div>
        </div>`).join("");
      viewRoot.innerHTML += `<section class="card section">${sectionHeader("Rules", `${state.replies.length} rule(s)`, `<button class="primary-button" data-action="create-reply">Create rule</button>`)}<div class="list">${rows || renderEmpty("No auto reply rules configured.")}</div></section>`;
      bindDataActions();
    } finally {
      setLoading(false);
    }
  }

  async function renderChats() {
    setLoading(true, "Loading chats…");
    try {
      state.chats = (await api("/api/admin/chats?limit=100")).items || [];
      viewRoot.innerHTML = pageHead("Chats", "Connected chats", "Inspect registered chats and enable or disable platform modules per chat.");
      const rows = state.chats.map((chat) => {
        const modules = Object.entries(chat.modules || {}).map(([name, enabled]) => `<button class="secondary-button" data-chat-toggle="${chat.telegram_id}" data-module="${escapeHtml(name)}">${escapeHtml(name)}: ${enabled ? "On" : "Off"}</button>`).join("");
        return `<article class="list-item"><div class="item-top"><div><h3>${escapeHtml(chat.title || chat.username || String(chat.telegram_id))}</h3><div class="meta-line"><span>${escapeHtml(chat.chat_type)}</span><span>${escapeHtml(chat.username ? `@${chat.username}` : "No username")}</span><span>${chat.is_active ? "Active" : "Inactive"}</span></div></div></div><div class="actions" style="margin-top:12px">${modules || `<span class="muted">No modules configured.</span>`}</div></article>`;
      }).join("");
      viewRoot.innerHTML += `<section class="card section">${sectionHeader("Registry", `${state.chats.length} chat(s)`)}<div class="list">${rows || renderEmpty("No registered chats yet.")}</div></section>`;
      bindDataActions();
    } finally {
      setLoading(false);
    }
  }

  async function renderTeam() {
    setLoading(true, "Loading team…");
    try {
      state.users = (await api("/api/admin/users?limit=100")).items || [];
      viewRoot.innerHTML = pageHead("Team", "Users and roles", "Manage persistent platform roles using Telegram user IDs.");
      const rows = state.users.map((user) => `
        <div class="list-item">
          <div class="item-top"><div><h3>${escapeHtml([user.first_name, user.last_name].filter(Boolean).join(" ") || user.username || String(user.telegram_id))}</h3><div class="meta-line"><span>${escapeHtml(user.username ? `@${user.username}` : "No username")}</span><span>ID ${escapeHtml(user.telegram_id)}</span><span>Last seen ${formatDate(user.last_seen_at)}</span></div></div><div class="row-actions"><button class="secondary-button" data-user-role="${user.telegram_id}">Manage roles</button></div></div>
          <div class="meta-line">${(user.roles || []).map((role) => `<span class="pill pill-info">${escapeHtml(role)}</span>`).join("") || `<span class="muted">No persistent roles</span>`}</div>
        </div>`).join("");
      viewRoot.innerHTML += `<section class="card section">${sectionHeader("User registry", `${state.users.length} user(s)`)}<div class="list">${rows || renderEmpty("No users registered yet.")}</div></section>`;
      bindDataActions();
    } finally {
      setLoading(false);
    }
  }

  async function renderActivity() {
    setLoading(true, "Loading activity…");
    try {
      state.audit = (await api("/api/admin/audit?limit=100")).items || [];
      viewRoot.innerHTML = pageHead("Activity", "Audit trail", "A read-only record of important administrative operations.");
      const rows = state.audit.map((item) => `<div class="list-item"><div class="item-top"><div><h3>${escapeHtml(item.action)}</h3><div class="meta-line"><span>Actor ${escapeHtml(item.actor_telegram_id ?? "system")}</span><span>${formatDate(item.created_at)}</span><span>${escapeHtml(item.target || "—")}</span></div></div></div>${item.metadata_json && Object.keys(item.metadata_json).length ? `<div class="item-body">${escapeHtml(JSON.stringify(item.metadata_json, null, 2))}</div>` : ""}</div>`).join("");
      viewRoot.innerHTML += `<section class="card section">${sectionHeader("Recent events", `${state.audit.length} event(s)`)}<div class="list">${rows || renderEmpty("No audit events yet.")}</div></section>`;
    } finally {
      setLoading(false);
    }
  }

  async function renderSettings() {
    const config = await api("/api/admin/settings");
    viewRoot.innerHTML = pageHead("Settings", "Platform configuration", "Read-only runtime information exposed safely to the Mini App.");
    viewRoot.innerHTML += `<section class="card section"><div class="list">
      <div class="list-item"><div class="stat-row" style="justify-content:space-between"><span>Environment</span><strong>${escapeHtml(config.environment)}</strong></div></div>
      <div class="list-item"><div class="stat-row" style="justify-content:space-between"><span>Application</span><strong>${escapeHtml(config.app_name)}</strong></div></div>
      <div class="list-item"><div class="stat-row" style="justify-content:space-between"><span>Default locale</span><strong>${escapeHtml(config.default_locale)}</strong></div></div>
      <div class="list-item"><div class="stat-row" style="justify-content:space-between"><span>Scheduler</span><strong>${config.scheduler_enabled ? "Enabled" : "Disabled"}</strong></div></div>
      <div class="list-item"><div class="stat-row" style="justify-content:space-between"><span>Rate limit</span><strong>${escapeHtml(`${config.rate_limit_requests} / ${config.rate_limit_window_seconds}s`)}</strong></div></div>
      <div class="notice">Secrets, tokens and database credentials are never returned by this endpoint.</div>
    </div></section>`;
  }

  function bindDataActions() {
    document.querySelectorAll("[data-action]").forEach((node) => {
      node.addEventListener("click", () => {
        const action = node.dataset.action;
        if (action === "create-content" || action === "quick-create-content") openContentDialog();
        if (action === "schedule-message" || action === "quick-schedule") openScheduleDialog();
        if (action === "create-reply" || action === "quick-replies") { navigate("automation"); }
        if (action === "navigate-content") navigate("content");
      });
    });
    document.querySelectorAll("[data-content-edit]").forEach((node) => node.addEventListener("click", () => {
      const item = state.content.find((entry) => entry.id === Number(node.dataset.contentEdit));
      if (item) openContentDialog(item);
    }));
    document.querySelectorAll("[data-content-publish]").forEach((node) => node.addEventListener("click", () => publishContent(Number(node.dataset.contentPublish))));
    document.querySelectorAll("[data-content-archive]").forEach((node) => node.addEventListener("click", () => archiveContent(Number(node.dataset.contentArchive))));
    document.querySelectorAll("[data-content-schedule]").forEach((node) => node.addEventListener("click", () => openScheduleDialog(Number(node.dataset.contentSchedule))));
    document.querySelectorAll("[data-schedule-cancel]").forEach((node) => node.addEventListener("click", () => cancelSchedule(Number(node.dataset.scheduleCancel))));
    document.querySelectorAll("[data-reply-edit]").forEach((node) => node.addEventListener("click", () => {
      const item = state.replies.find((entry) => entry.id === Number(node.dataset.replyEdit));
      if (item) openReplyDialog(item);
    }));
    document.querySelectorAll("[data-reply-toggle]").forEach((node) => node.addEventListener("click", () => toggleReply(Number(node.dataset.replyToggle))));
    document.querySelectorAll("[data-reply-delete]").forEach((node) => node.addEventListener("click", () => deleteReply(Number(node.dataset.replyDelete))));
    document.querySelectorAll("[data-chat-toggle]").forEach((node) => node.addEventListener("click", () => toggleChatModule(Number(node.dataset.chatToggle), node.dataset.module)));
    document.querySelectorAll("[data-user-role]").forEach((node) => node.addEventListener("click", () => manageRoles(Number(node.dataset.userRole))));
  }

  async function publishContent(id) {
    setLoading(true, "Publishing…");
    try { await api(`/api/content/${id}/publish`, { method: "POST" }); toast("Content published."); state.dashboard = null; await renderContent(); }
    catch (error) { handleError(error); }
    finally { setLoading(false); }
  }

  async function archiveContent(id) {
    if (!window.confirm("Archive this content?")) return;
    setLoading(true, "Archiving…");
    try { await api(`/api/admin/content/${id}/archive`, { method: "POST" }); toast("Content archived."); await renderContent(); }
    catch (error) { handleError(error); }
    finally { setLoading(false); }
  }

  function openContentDialog(item = null) {
    $("content-dialog-title").textContent = item ? "Edit content" : "Create content";
    $("content-dialog-eyebrow").textContent = item ? `Content #${item.id}` : "Content";
    $("content-id").value = item?.id || "";
    $("content-title").value = item?.title || "";
    $("content-body").value = item?.body || "";
    $("content-dialog").showModal();
    window.setTimeout(() => $("content-title").focus(), 30);
  }

  function closeDialog(id) { const dialog = $(id); if (dialog.open) dialog.close(); }

  async function saveContent(event) {
    event.preventDefault();
    const id = Number($("content-id").value || 0);
    const payload = { title: $("content-title").value.trim(), body: $("content-body").value.trim() };
    if (!payload.title || !payload.body) return toast("Title and body are required.", "error");
    setLoading(true, "Saving content…");
    try {
      if (id) await api(`/api/admin/content/${id}`, { method: "PUT", body: JSON.stringify(payload) });
      else await api("/api/content", { method: "POST", body: JSON.stringify(payload) });
      closeDialog("content-dialog"); toast(id ? "Content updated." : "Draft created."); await renderContent();
    } catch (error) { handleError(error); }
    finally { setLoading(false); }
  }

  function openScheduleDialog(contentId = 0) {
    const content = contentId ? state.content.find((entry) => entry.id === Number(contentId)) : null;
    const when = new Date(Date.now() + 60 * 60 * 1000);
    const local = new Date(when.getTime() - when.getTimezoneOffset() * 60 * 1000).toISOString().slice(0, 16);
    const text = content ? `${content.title}\n\n${content.body}` : "";
    const html = `<form method="dialog" class="modal-card" id="schedule-runtime-form"><div class="modal-header"><div><div class="eyebrow">Scheduling</div><h2>${content ? "Schedule content" : "Schedule message"}</h2></div><button class="icon-button" type="button" data-runtime-close>×</button></div>${content ? `<input type="hidden" name="content_id" value="${content.id}"><div class="notice">Content #${content.id} will be published and delivered by the worker.</div>` : `<label>Target chat ID<input name="chat_id" type="number" required placeholder="-1001234567890"></label><label>Message<textarea name="text" maxlength="4096" required>${escapeHtml(text)}</textarea></label><label>Parse mode<select name="parse_mode"><option value="">Plain text</option><option value="HTML">HTML</option><option value="MarkdownV2">MarkdownV2</option></select></label>`}<label>Run at<input name="run_at" type="datetime-local" value="${local}" required></label>${content ? `<label>Target chat ID (optional)<input name="target_chat_id" type="number" placeholder="Leave blank for configured default"></label>` : ""}<div class="modal-actions"><button class="secondary-button" type="button" data-runtime-close>Cancel</button><button class="primary-button" type="submit">Schedule</button></div></form>`;
    const wrapper = document.createElement("dialog");
    wrapper.className = "modal";
    wrapper.innerHTML = html;
    document.body.append(wrapper);
    wrapper.showModal();
    wrapper.querySelectorAll("[data-runtime-close]").forEach((node) => node.addEventListener("click", () => { wrapper.close(); wrapper.remove(); }));
    wrapper.querySelector("form").addEventListener("submit", async (event) => {
      event.preventDefault();
      const form = new FormData(event.currentTarget);
      const runAt = new Date(form.get("run_at")).toISOString();
      try {
        setLoading(true, "Scheduling…");
        if (content) {
          await api("/api/admin/schedule-content", { method: "POST", body: JSON.stringify({ content_id: Number(form.get("content_id")), run_at: runAt, target_chat_id: form.get("target_chat_id") ? Number(form.get("target_chat_id")) : null }) });
        } else {
          await api("/api/admin/schedule-message", { method: "POST", body: JSON.stringify({ chat_id: Number(form.get("chat_id")), text: String(form.get("text")), run_at: runAt, parse_mode: form.get("parse_mode") || null }) });
        }
        wrapper.close(); wrapper.remove(); toast("Scheduled successfully."); await renderSchedule();
      } catch (error) { handleError(error); }
      finally { setLoading(false); }
    });
  }

  async function cancelSchedule(id) {
    if (!window.confirm("Cancel this scheduled job?")) return;
    setLoading(true, "Cancelling…");
    try { await api(`/api/admin/schedules/${id}/cancel`, { method: "POST" }); toast("Scheduled job cancelled."); await renderSchedule(); }
    catch (error) { handleError(error); }
    finally { setLoading(false); }
  }

  function openReplyDialog(item = null) {
    $("reply-dialog-title").textContent = item ? "Edit auto reply" : "Create auto reply";
    $("reply-id").value = item?.id || "";
    $("reply-trigger").value = item?.trigger || "";
    $("reply-mode").value = item?.match_mode || "contains";
    $("reply-response").value = item?.response || "";
    $("reply-priority").value = item?.priority ?? 100;
    $("reply-enabled").checked = item?.enabled ?? true;
    $("reply-dialog").showModal();
    window.setTimeout(() => $("reply-trigger").focus(), 30);
  }

  async function saveReply(event) {
    event.preventDefault();
    const id = Number($("reply-id").value || 0);
    const payload = {
      trigger: $("reply-trigger").value.trim(),
      response: $("reply-response").value.trim(),
      match_mode: $("reply-mode").value,
      priority: Number($("reply-priority").value),
      enabled: $("reply-enabled").checked,
    };
    if (!payload.trigger || !payload.response) return toast("Trigger and response are required.", "error");
    setLoading(true, "Saving rule…");
    try {
      await api(id ? `/api/admin/auto-replies/${id}` : "/api/admin/auto-replies", { method: id ? "PUT" : "POST", body: JSON.stringify(payload) });
      closeDialog("reply-dialog"); toast(id ? "Rule updated." : "Rule created."); await renderAutomation();
    } catch (error) { handleError(error); }
    finally { setLoading(false); }
  }

  async function toggleReply(id) {
    setLoading(true, "Updating rule…");
    try { await api(`/api/admin/auto-replies/${id}/toggle`, { method: "POST" }); toast("Rule status updated."); await renderAutomation(); }
    catch (error) { handleError(error); }
    finally { setLoading(false); }
  }

  async function deleteReply(id) {
    if (!window.confirm("Delete this auto reply rule?")) return;
    setLoading(true, "Deleting rule…");
    try { await api(`/api/admin/auto-replies/${id}`, { method: "DELETE" }); toast("Rule deleted."); await renderAutomation(); }
    catch (error) { handleError(error); }
    finally { setLoading(false); }
  }

  async function toggleChatModule(chatId, module) {
    setLoading(true, "Updating module…");
    try { await api(`/api/admin/chats/${chatId}/modules/${encodeURIComponent(module)}/toggle`, { method: "POST" }); toast("Module status updated."); await renderChats(); }
    catch (error) { handleError(error); }
    finally { setLoading(false); }
  }

  async function manageRoles(telegramId) {
    const user = state.users.find((item) => item.telegram_id === telegramId);
    const current = user?.roles || [];
    const raw = window.prompt("Enter roles separated by commas. Allowed: owner, admin, manager, staff, support, moderator, analyst, client, member", current.join(", "));
    if (raw === null) return;
    const roles = raw.split(",").map((role) => role.trim().toLowerCase()).filter(Boolean);
    setLoading(true, "Saving roles…");
    try { await api(`/api/admin/users/${telegramId}/roles`, { method: "PUT", body: JSON.stringify({ roles }) }); toast("Roles updated."); await renderTeam(); }
    catch (error) { handleError(error); }
    finally { setLoading(false); }
  }

  function handleError(error, showToast = true) {
    if (error?.status === 401) {
      toast("Your session expired. Reopen the Mini App.", "error");
      return;
    }
    if (showToast) toast(error?.message || "Unexpected error.", "error");
  }

  async function authenticate() {
    if (!tg?.initData) throw new Error("Open this Mini App inside Telegram.");
    initTelegram();
    refreshTheme();
    const result = await api("/api/auth/telegram", {
      method: "POST",
      body: JSON.stringify({ init_data: tg.initData }),
    });
    state.user = result.user;
    const me = await api("/api/me");
    state.user = me;
    state.isAdmin = Boolean(me.is_admin);
    $("identity-name").textContent = [me.first_name, me.last_name].filter(Boolean).join(" ") || me.username || `User ${me.id}`;
    $("identity-role").textContent = roleLabel(me.roles);
    $("avatar").textContent = ((me.first_name || me.username || "U")[0] || "U").toUpperCase();
    $("connection-pill").textContent = state.isAdmin ? "Administrator" : "Connected";
    $("connection-pill").className = `pill ${state.isAdmin ? "pill-info" : "pill-success"}`;
    buildNavigation();
    updateNavState();
  }

  function setupUi() {
    $("menu-button").addEventListener("click", () => sidebar.classList.toggle("open"));
    $("close-button").addEventListener("click", () => tg?.close());
    $("logout-button").addEventListener("click", async () => {
      try { await api("/api/auth/logout", { method: "POST" }); tg?.close(); } catch (error) { handleError(error); }
    });
    $("content-form").addEventListener("submit", saveContent);
    $("content-dialog-close").addEventListener("click", () => closeDialog("content-dialog"));
    $("content-cancel").addEventListener("click", () => closeDialog("content-dialog"));
    $("reply-form").addEventListener("submit", saveReply);
    $("reply-dialog-close").addEventListener("click", () => closeDialog("reply-dialog"));
    $("reply-cancel").addEventListener("click", () => closeDialog("reply-dialog"));
    tg?.onEvent?.("themeChanged", refreshTheme);
    tg?.onEvent?.("viewportChanged", () => document.documentElement.style.setProperty("--app-viewport-height", `${tg.viewportHeight}px`));
  }

  async function start() {
    setupUi();
    setLoading(true, "Authenticating with Telegram…");
    try {
      await authenticate();
      await renderView();
    } catch (error) {
      $("connection-pill").textContent = "Authentication failed";
      $("connection-pill").className = "pill pill-danger";
      viewRoot.innerHTML = `${pageHead("Mini App", "Unable to open the console", error.message)}<section class="card section"><div class="notice">This application requires a valid Telegram Mini App session. Launch it from the bot inside Telegram.</div></section>`;
      handleError(error, false);
    } finally {
      setLoading(false);
    }
  }

  window.addEventListener("load", start);
})();
