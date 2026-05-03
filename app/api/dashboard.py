# ruff: noqa: E501
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
@router.get("/dashboard", response_class=HTMLResponse)
def dashboard() -> str:
    return """
<!doctype html>
<html lang="it">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>NicoWay Dashboard</title>
  <style>
    :root {
      --bg: #f6f4ef;
      --panel: #ffffff;
      --ink: #232426;
      --muted: #646b73;
      --line: #ded9cf;
      --accent: #0f766e;
      --accent-strong: #115e59;
      --danger: #b42318;
      --warn: #a15c07;
      --ok: #157347;
      --shadow: 0 10px 24px rgba(25, 25, 25, 0.08);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font: 14px/1.45 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--ink);
      background: var(--bg);
    }
    header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      padding: 20px 28px;
      border-bottom: 1px solid var(--line);
      background: rgba(255, 255, 255, 0.76);
      backdrop-filter: blur(12px);
      position: sticky;
      top: 0;
      z-index: 4;
    }
    h1, h2, h3 { margin: 0; line-height: 1.15; letter-spacing: 0; }
    h1 { font-size: 24px; }
    h2 { font-size: 18px; }
    h3 { font-size: 15px; }
    main {
      width: min(1180px, 100%);
      margin: 0 auto;
      padding: 24px;
      display: grid;
      grid-template-columns: 360px 1fr;
      gap: 20px;
    }
    section, aside {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: var(--shadow);
    }
    aside { padding: 18px; height: fit-content; }
    section { padding: 0; overflow: hidden; }
    .section-head {
      padding: 18px;
      border-bottom: 1px solid var(--line);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
    }
    .toolbar { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
    button {
      appearance: none;
      border: 1px solid var(--line);
      background: #fff;
      color: var(--ink);
      min-height: 36px;
      padding: 0 12px;
      border-radius: 6px;
      font: inherit;
      cursor: pointer;
      white-space: nowrap;
    }
    button:hover { border-color: var(--accent); color: var(--accent-strong); }
    button.primary { background: var(--accent); border-color: var(--accent); color: #fff; }
    button.primary:hover { background: var(--accent-strong); color: #fff; }
    button.danger { color: var(--danger); }
    label { display: grid; gap: 6px; color: var(--muted); font-size: 12px; }
    input {
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 6px;
      min-height: 38px;
      padding: 8px 10px;
      font: inherit;
      color: var(--ink);
      background: #fff;
    }
    form { display: grid; gap: 12px; margin-top: 16px; }
    .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
    .status {
      display: inline-flex;
      align-items: center;
      gap: 7px;
      color: var(--muted);
      font-size: 13px;
    }
    .dot { width: 8px; height: 8px; border-radius: 50%; background: var(--warn); }
    .dot.ok { background: var(--ok); }
    .list { display: grid; }
    .search-row {
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 14px;
      padding: 16px 18px;
      border-bottom: 1px solid var(--line);
    }
    .search-row:last-child { border-bottom: 0; }
    .meta {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      color: var(--muted);
      margin-top: 8px;
      font-size: 13px;
    }
    .pill {
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 2px 8px;
      background: #fbfaf7;
    }
    .pill.active { border-color: #b9ded7; color: var(--accent-strong); background: #edf9f7; }
    .pill.paused { border-color: #efd0c8; color: var(--danger); background: #fff4f1; }
    .deals {
      padding: 18px;
      display: grid;
      gap: 12px;
      background: #fbfaf7;
      border-top: 1px solid var(--line);
    }
    .deal {
      background: #fff;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px;
      display: grid;
      gap: 10px;
    }
    .deal-head {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: start;
    }
    .price { font-size: 22px; font-weight: 700; }
    .muted { color: var(--muted); }
    .empty { padding: 28px 18px; color: var(--muted); }
    a { color: var(--accent-strong); text-decoration: none; }
    a:hover { text-decoration: underline; }
    .toast {
      position: fixed;
      right: 18px;
      bottom: 18px;
      max-width: min(420px, calc(100vw - 36px));
      background: #1f2937;
      color: #fff;
      padding: 12px 14px;
      border-radius: 8px;
      box-shadow: var(--shadow);
      display: none;
      z-index: 8;
    }
    @media (max-width: 880px) {
      header { padding: 16px; align-items: start; flex-direction: column; }
      main { grid-template-columns: 1fr; padding: 16px; }
      .search-row { grid-template-columns: 1fr; }
      .toolbar { justify-content: flex-start; }
    }
  </style>
</head>
<body>
  <header>
    <div>
      <h1>NicoWay</h1>
      <div class="muted">Travel Deal Watcher</div>
    </div>
    <div class="toolbar">
      <span class="status"><span id="healthDot" class="dot"></span><span id="healthText">checking</span></span>
      <button id="refreshBtn">Aggiorna</button>
    </div>
  </header>

  <main>
    <aside>
      <h2>Nuova ricerca</h2>
      <form id="searchForm">
        <label>Telegram chat id<input name="telegram_chat_id" required inputmode="numeric"></label>
        <label>Nome<input name="name" required placeholder="Scozia 2026"></label>
        <div class="grid-2">
          <label>Partenza<input name="origin" required placeholder="FCO"></label>
          <label>Destinazione<input name="destination" required placeholder="Edimburgo"></label>
        </div>
        <div class="grid-2">
          <label>Dal<input name="date_from" required type="date"></label>
          <label>Al<input name="date_to" required type="date"></label>
        </div>
        <div class="grid-2">
          <label>Flessibilità<input name="flexible_days" type="number" value="2" min="0"></label>
          <label>Adulti<input name="adults" type="number" value="2" min="1"></label>
        </div>
        <label>Budget totale<input name="max_budget_total" required type="number" value="1800" min="1"></label>
        <div class="grid-2">
          <label>Max volo<input name="max_flight_price" type="number" value="350" min="0"></label>
          <label>Max hotel/notte<input name="max_hotel_price_per_night" type="number" value="120" min="0"></label>
        </div>
        <button class="primary" type="submit">Crea</button>
      </form>
    </aside>

    <section>
      <div class="section-head">
        <h2>Ricerche</h2>
        <span id="count" class="muted">0</span>
      </div>
      <div id="searches" class="list"></div>
    </section>
  </main>
  <div id="toast" class="toast"></div>

  <script>
    const searchesEl = document.querySelector("#searches");
    const countEl = document.querySelector("#count");
    const toastEl = document.querySelector("#toast");

    function money(value) {
      if (value === null || value === undefined) return "-";
      return new Intl.NumberFormat("it-IT", { style: "currency", currency: "EUR", maximumFractionDigits: 0 }).format(Number(value));
    }

    function dateTime(value) {
      if (!value) return "-";
      return new Intl.DateTimeFormat("it-IT", { dateStyle: "short", timeStyle: "short" }).format(new Date(value));
    }

    function toast(message) {
      toastEl.textContent = message;
      toastEl.style.display = "block";
      clearTimeout(window.__toastTimer);
      window.__toastTimer = setTimeout(() => { toastEl.style.display = "none"; }, 3200);
    }

    async function request(path, options = {}) {
      const res = await fetch(path, options);
      if (!res.ok) throw new Error(await res.text());
      return res.json();
    }

    async function refreshHealth() {
      try {
        const health = await request("/health");
        document.querySelector("#healthDot").classList.add("ok");
        document.querySelector("#healthText").textContent = health.status + " · " + health.env;
      } catch {
        document.querySelector("#healthDot").classList.remove("ok");
        document.querySelector("#healthText").textContent = "offline";
      }
    }

    async function loadDeals(searchId) {
      const deals = await request(`/deals/${searchId}`);
      if (!deals.length) return `<div class="deals"><div class="muted">Nessun deal salvato.</div></div>`;
      return `<div class="deals">${deals.map(deal => `
        <article class="deal">
          <div class="deal-head">
            <div>
              <div class="price">${money(deal.total_estimated_price)}</div>
              <div class="muted">${dateTime(deal.created_at)} · score ${Math.round(deal.score)}/100 · ${deal.is_notified ? "notificato" : "non notificato"}</div>
            </div>
          </div>
          ${deal.flight ? `<div>✈️ ${deal.flight.origin} → ${deal.flight.destination}, ${dateTime(deal.flight.departure_datetime)}, ${money(deal.flight.total_price)}, ${deal.flight.stops} scali · <a href="${deal.flight.booking_url}" target="_blank" rel="noreferrer">volo</a></div>` : ""}
          ${deal.hotel ? `<div>🏨 ${deal.hotel.hotel_name}, ${money(deal.hotel.price_per_night)}/notte, rating ${deal.hotel.rating} · <a href="${deal.hotel.booking_url}" target="_blank" rel="noreferrer">hotel</a></div>` : ""}
        </article>`).join("")}</div>`;
    }

    async function render() {
      await refreshHealth();
      const searches = await request("/searches");
      countEl.textContent = searches.length + " totali";
      if (!searches.length) {
        searchesEl.innerHTML = `<div class="empty">Nessuna ricerca.</div>`;
        return;
      }
      const rows = await Promise.all(searches.map(async search => {
        const dealsHtml = await loadDeals(search.id);
        return `<div class="search-row" data-id="${search.id}">
          <div>
            <h3>${search.name}</h3>
            <div class="meta">
              <span class="pill ${search.is_active ? "active" : "paused"}">${search.is_active ? "attiva" : "pausa"}</span>
              <span>${search.origin} → ${search.destination}</span>
              <span>${search.date_from} / ${search.date_to}</span>
              <span>budget ${money(search.max_budget_total)}</span>
              <span>ogni ${search.check_frequency_minutes} min</span>
            </div>
          </div>
          <div class="toolbar">
            <button data-action="check">Check</button>
            <button data-action="${search.is_active ? "disable" : "enable"}">${search.is_active ? "Pausa" : "Attiva"}</button>
            <button class="danger" data-action="delete">Elimina</button>
          </div>
          ${dealsHtml}
        </div>`;
      }));
      searchesEl.innerHTML = rows.join("");
    }

    searchesEl.addEventListener("click", async event => {
      const button = event.target.closest("button[data-action]");
      if (!button) return;
      const row = button.closest("[data-id]");
      const id = row.dataset.id;
      const action = button.dataset.action;
      try {
        if (action === "delete") {
          if (!confirm("Eliminare questa ricerca?")) return;
          await request(`/searches/${id}`, { method: "DELETE" });
        } else {
          await request(`/searches/${id}/${action}`, { method: "POST" });
        }
        toast(action === "check" ? "Controllo completato." : "Aggiornato.");
        await render();
      } catch (error) {
        toast("Errore: " + error.message);
      }
    });

    document.querySelector("#refreshBtn").addEventListener("click", render);

    document.querySelector("#searchForm").addEventListener("submit", async event => {
      event.preventDefault();
      const data = Object.fromEntries(new FormData(event.currentTarget).entries());
      for (const key of ["telegram_chat_id", "flexible_days", "adults"]) data[key] = Number(data[key]);
      for (const key of ["max_budget_total", "max_flight_price", "max_hotel_price_per_night"]) {
        data[key] = data[key] === "" ? null : Number(data[key]);
      }
      try {
        await request("/searches", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(data),
        });
        event.currentTarget.reset();
        toast("Ricerca creata.");
        await render();
      } catch (error) {
        toast("Errore: " + error.message);
      }
    });

    render();
  </script>
</body>
</html>
"""
