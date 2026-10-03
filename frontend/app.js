(() => {
  const tg = window.Telegram?.WebApp;
  const el = (id) => document.getElementById(id);

  function showStatus(message) {
    el("status").textContent = message;
  }

  async function api(path, options = {}) {
    const response = await fetch(path, {
      credentials: "include",
      headers: { "Content-Type": "application/json", ...(options.headers || {}) },
      ...options,
    });
    if (!response.ok) {
      let detail = `HTTP ${response.status}`;
      try { detail = (await response.json()).detail || detail; } catch (_) {}
      throw new Error(detail);
    }
    return response.json();
  }

  async function authenticate() {
    if (!tg || !tg.initData) throw new Error("Open this page inside Telegram.");
    tg.ready();
    tg.expand();
    const result = await api("/api/auth/telegram", {
      method: "POST",
      body: JSON.stringify({ init_data: tg.initData }),
    });
    el("greeting").textContent = `Hello ${result.user?.name || "there"}`;
    return result.user;
  }

  async function loadContent() {
    const root = el("content");
    root.textContent = "Loading…";
    const data = await api("/api/content");
    root.replaceChildren();
    if (!data.items?.length) {
      root.textContent = "No published content is available yet.";
      return;
    }
    for (const item of data.items) {
      const card = document.createElement("article");
      card.className = "item";
      const title = document.createElement("h3");
      title.textContent = item.title;
      const body = document.createElement("p");
      body.textContent = item.body;
      card.append(title, body);
      root.append(card);
    }
  }

  async function init() {
    try {
      const user = await authenticate();
      showStatus(user?.is_admin ? "Authenticated administrator" : "Authenticated");
      if (user?.is_admin) el("admin").classList.remove("hidden");
      await loadContent();
    } catch (error) {
      console.error(error);
      showStatus(error.message || "Authentication failed");
    }
  }

  el("refresh").addEventListener("click", () => loadContent().catch((e) => showStatus(e.message)));
  el("close").addEventListener("click", () => tg?.close());
  el("summary").addEventListener("click", async () => {
    try {
      el("admin-output").textContent = JSON.stringify(await api("/api/admin/summary"), null, 2);
    } catch (e) { el("admin-output").textContent = e.message; }
  });
  el("create-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
      const result = await api("/api/content", {
        method: "POST",
        body: JSON.stringify({ title: el("title").value, body: el("body").value }),
      });
      el("admin-output").textContent = `Draft created: ${result.id}`;
      event.target.reset();
    } catch (e) { el("admin-output").textContent = e.message; }
  });

  init();
})();
