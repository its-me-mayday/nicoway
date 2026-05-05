# ruff: noqa: E501
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
@router.get("/dashboard", response_class=HTMLResponse)
def dashboard() -> str:
    return r"""
<!doctype html>
<html lang="it">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>NicoWay</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    :root {
      --bg:         #f0f4f8;
      --layer:      #ffffff;
      --panel:      #ffffff;
      --panel-alt:  #f8fafc;
      --ink:        #1e293b;
      --ink-bright: #0f172a;
      --muted:      #64748b;
      --line:       #e2e8f0;
      --line-bright:#cbd5e1;
      --gold:       #92680a;
      --gold-dim:   #b8860b;
      --gold-glow:  rgba(146,104,10,0.10);
      --gold-bright:#7a5508;
      --danger:     #dc2626;
      --ok:         #16a34a;
      --shadow:     0 2px 12px rgba(15,23,42,0.08);
      --shadow-md:  0 4px 24px rgba(15,23,42,0.12);
      --radius:     10px;
    }
    * { box-sizing:border-box; margin:0; padding:0; }
    body {
      font-family:'Inter',system-ui,-apple-system,sans-serif;
      font-size:13px; line-height:1.5;
      color:var(--ink); background:var(--bg);
      min-height:100vh;
      padding-bottom:32px;
    }

    /* ── Header ── */
    header {
      display:flex; align-items:center; justify-content:space-between; gap:16px;
      padding:0 28px; height:52px;
      background:var(--layer); border-bottom:1px solid var(--line);
      position:sticky; top:0; z-index:50; box-shadow:var(--shadow);
    }
    .logo { display:flex; align-items:baseline; gap:8px; }
    .logo-name { font-size:17px; font-weight:700; letter-spacing:-.3px; color:var(--gold); }
    .logo-tag  { font-size:10px; font-weight:500; letter-spacing:.12em; text-transform:uppercase; color:var(--muted); }

    /* ── Account chip ── */
    .account-chip {
      display:inline-flex; align-items:center; gap:7px;
      background:var(--bg); border:1px solid var(--line-bright);
      border-radius:999px; padding:4px 12px 4px 10px;
      cursor:pointer; font-size:12px; color:var(--ink);
      transition:border-color .15s, box-shadow .15s;
      user-select:none;
    }
    .account-chip:hover { border-color:var(--gold-dim); box-shadow:0 0 0 3px var(--gold-glow); }
    .account-chip .chip-dot { width:7px; height:7px; border-radius:50%; background:var(--line-bright); flex-shrink:0; }
    .account-chip.set .chip-dot { background:var(--ok); }
    .account-chip .chip-label { color:var(--muted); font-size:11px; }
    .account-chip .chip-id { font-weight:600; color:var(--ink); }

    /* ── Setup overlay ── */
    .overlay { position:fixed; inset:0; background:rgba(15,23,42,.45); z-index:200; display:flex; align-items:center; justify-content:center; }
    .overlay.hidden { display:none; }
    .setup-card { background:var(--layer); border-radius:14px; padding:32px; width:min(400px,90vw); box-shadow:var(--shadow-md); display:grid; gap:16px; }
    .setup-card h2 { font-size:16px; font-weight:700; color:var(--ink-bright); margin:0; }
    .setup-card p  { font-size:13px; color:var(--muted); }

    /* ── Layout ── */
    main { width:min(1280px,100%); margin:0 auto; padding:20px 24px; display:grid; grid-template-columns:340px 1fr; gap:20px; align-items:start; }
    aside { display:grid; background:var(--layer); border:1px solid var(--line); border-radius:var(--radius); box-shadow:var(--shadow); overflow:hidden; }
    .aside-block { padding:18px 20px; border-bottom:1px solid var(--line); }
    .aside-block:last-child { border-bottom:0; }
    section { background:var(--layer); border:1px solid var(--line); border-radius:var(--radius); box-shadow:var(--shadow); overflow:hidden; }

    /* ── Type ── */
    h2 { font-size:10px; font-weight:600; letter-spacing:.14em; text-transform:uppercase; color:var(--gold); margin-bottom:12px; }
    h3 { font-size:13px; font-weight:600; color:var(--ink-bright); }

    /* ── Forms ── */
    form { display:grid; gap:8px; }
    label { display:grid; gap:3px; font-size:10px; font-weight:600; letter-spacing:.06em; text-transform:uppercase; color:var(--muted); }
    input, select {
      width:100%; background:var(--bg); border:1px solid var(--line-bright); border-radius:6px;
      min-height:33px; padding:5px 10px; font:inherit; font-size:13px; color:var(--ink-bright);
      outline:none; transition:border-color .15s, box-shadow .15s;
    }
    input:focus, select:focus { border-color:var(--gold-dim); box-shadow:0 0 0 3px var(--gold-glow); background:var(--layer); }
    input::placeholder { color:var(--muted); opacity:.55; }
    select option { background:var(--layer); color:var(--ink); }
    input[type="date"]::-webkit-calendar-picker-indicator { opacity:.5; }
    .grid-2 { display:grid; grid-template-columns:1fr 1fr; gap:8px; }
    .grid-3 { display:grid; grid-template-columns:1fr 1fr 1fr; gap:8px; }

    /* ── Buttons ── */
    button { appearance:none; background:transparent; border:1px solid var(--line-bright); color:var(--ink); min-height:32px; padding:0 12px; border-radius:6px; font:inherit; font-size:12px; font-weight:500; cursor:pointer; white-space:nowrap; transition:border-color .15s,color .15s,background .15s,box-shadow .15s; }
    button:hover { border-color:var(--gold-dim); color:var(--gold); }
    button.primary { background:var(--gold); border-color:var(--gold); color:#fff; font-weight:600; }
    button.primary:hover { background:var(--gold-bright); border-color:var(--gold-bright); }
    button.danger { border-color:transparent; color:var(--danger); opacity:.7; }
    button.danger:hover { opacity:1; border-color:rgba(220,38,38,.3); }
    button.ghost { border-color:transparent; color:var(--muted); font-size:11px; }
    button.ghost:hover { color:var(--gold); }
    .toolbar { display:flex; gap:6px; align-items:center; flex-wrap:wrap; }

    /* ── Status ── */
    .status { display:inline-flex; align-items:center; gap:6px; font-size:12px; color:var(--muted); }
    .dot { width:7px; height:7px; border-radius:50%; background:var(--danger); flex-shrink:0; }
    .dot.ok { background:var(--ok); box-shadow:0 0 5px var(--ok); }

    /* ── Tooltip ── */
    .tip { position:relative; display:inline-flex; align-items:center; justify-content:center; width:14px; height:14px; border-radius:50%; background:var(--line-bright); color:var(--muted); font-size:9px; font-weight:700; cursor:help; vertical-align:middle; margin-left:3px; flex-shrink:0; }
    .tip::after { content:attr(data-tip); position:absolute; bottom:calc(100% + 5px); left:50%; transform:translateX(-50%); background:var(--ink-bright); color:#f8fafc; padding:5px 9px; border-radius:5px; font-size:11px; font-weight:400; white-space:nowrap; max-width:220px; white-space:normal; line-height:1.4; text-align:left; opacity:0; pointer-events:none; transition:opacity .15s; z-index:200; letter-spacing:0; text-transform:none; }
    .tip:hover::after { opacity:1; }

    /* ── Guide banner ── */
    .guide { background:var(--bg); border-bottom:1px solid var(--line); }
    .guide-toggle { display:flex; align-items:center; justify-content:space-between; padding:10px 20px; cursor:pointer; font-size:11px; font-weight:600; color:var(--muted); letter-spacing:.07em; text-transform:uppercase; user-select:none; }
    .guide-toggle:hover { color:var(--gold); }
    .guide-toggle .arrow { transition:transform .2s; font-size:10px; }
    .guide-toggle.open .arrow { transform:rotate(180deg); }
    .guide-body { display:none; padding:0 20px 14px; display:none; }
    .guide-body.open { display:grid; gap:8px; }
    .guide-step { display:flex; gap:10px; align-items:flex-start; font-size:12px; color:var(--ink); line-height:1.5; }
    .guide-num { width:20px; height:20px; border-radius:50%; background:var(--gold); color:#fff; font-size:10px; font-weight:700; display:flex; align-items:center; justify-content:center; flex-shrink:0; margin-top:1px; }

    /* ── Section head ── */
    .section-head { padding:12px 18px; border-bottom:1px solid var(--line); display:flex; align-items:center; justify-content:space-between; gap:12px; }
    .section-head h2 { margin:0; }

    /* ── Search rows ── */
    .search-row { border-bottom:1px solid var(--line); }
    .search-row:last-child { border-bottom:0; }
    .search-row-head { display:grid; grid-template-columns:1fr auto; gap:12px; padding:12px 18px; }
    .meta { display:flex; gap:5px; flex-wrap:wrap; align-items:center; margin-top:5px; }
    .pill { border:1px solid var(--line-bright); border-radius:999px; padding:1px 8px; font-size:10px; font-weight:500; letter-spacing:.05em; text-transform:uppercase; color:var(--muted); background:var(--bg); }
    .pill.active { border-color:rgba(22,163,74,.35); color:var(--ok); background:rgba(22,163,74,.07); }
    .pill.paused { border-color:rgba(220,38,38,.25); color:var(--danger); background:rgba(220,38,38,.06); }
    .pill.trip { border-color:var(--gold-dim); color:var(--gold); background:var(--gold-glow); }
    .meta-item { font-size:11px; color:var(--muted); }

    /* ── Boarding pass ── */
    .deals { padding:10px 18px 14px; display:grid; gap:10px; background:var(--panel-alt); border-top:1px solid var(--line); }
    .bp-card { background:var(--layer); border:1px solid var(--line); border-radius:8px; overflow:hidden; transition:border-color .15s, box-shadow .15s; }
    .bp-card:hover { border-color:var(--gold-dim); box-shadow:var(--shadow); }
    .bp-body { display:grid; grid-template-columns:1fr auto 1fr; align-items:center; padding:12px 16px 8px; }
    .bp-airport { display:grid; gap:1px; }
    .bp-airport.right { text-align:right; }
    .bp-iata { font-size:24px; font-weight:700; letter-spacing:-1px; color:var(--ink-bright); }
    .bp-time { font-size:13px; font-weight:600; color:var(--gold); }
    .bp-date-label { font-size:11px; color:var(--muted); }
    .bp-route { display:flex; flex-direction:column; align-items:center; gap:3px; padding:0 10px; }
    .bp-airline img { border-radius:4px; object-fit:contain; display:block; }
    .bp-line { display:flex; align-items:center; width:100%; gap:4px; }
    .bp-dash { flex:1; height:1px; background:repeating-linear-gradient(90deg,var(--line-bright) 0,var(--line-bright) 4px,transparent 4px,transparent 8px); }
    .bp-plane-icon { font-size:13px; color:var(--gold); }
    .bp-dur { font-size:10px; letter-spacing:.07em; text-transform:uppercase; color:var(--muted); text-align:center; }
    .bp-footer-strip { border-top:1px dashed var(--line-bright); padding:7px 16px; display:flex; justify-content:space-between; align-items:center; gap:10px; background:var(--bg); }
    .bp-price-big { font-size:19px; font-weight:700; color:var(--gold); letter-spacing:-.5px; }
    .bp-meta-right { display:flex; gap:8px; align-items:center; font-size:11px; color:var(--muted); }
    .bp-score { background:var(--gold-glow); border:1px solid rgba(146,104,10,.25); border-radius:4px; padding:2px 7px; font-size:11px; font-weight:600; color:var(--gold); }
    .bp-book { background:var(--gold); color:#fff; border:none; border-radius:5px; padding:4px 12px; font-size:11px; font-weight:700; cursor:pointer; text-decoration:none; letter-spacing:.04em; text-transform:uppercase; transition:background .15s; }
    .bp-book:hover { background:var(--gold-bright); }

    /* ── Leg builder ── */
    .leg-group { display:grid; gap:7px; border:1px solid var(--line); border-radius:7px; padding:10px 12px; background:var(--bg); }
    .leg-group h4 { font-size:10px; font-weight:600; letter-spacing:.1em; text-transform:uppercase; color:var(--gold); display:flex; justify-content:space-between; align-items:center; }

    /* ── Mode tabs ── */
    .mode-tabs { display:grid; grid-template-columns:1fr 1fr; border:1px solid var(--line-bright); border-radius:8px; overflow:hidden; margin-bottom:14px; }
    .mode-tab { appearance:none; background:transparent; border:none; border-radius:0; min-height:34px; padding:0 12px; font:inherit; font-size:12px; font-weight:500; color:var(--muted); cursor:pointer; transition:background .15s,color .15s; }
    .mode-tab:hover { background:var(--gold-glow); color:var(--gold); }
    .mode-tab.active { background:var(--gold); color:#fff; font-weight:600; }
    .mode-pane { display:none; }
    .mode-pane.visible { display:grid; gap:8px; }

    /* ── Misc ── */
    .empty { padding:28px 18px; color:var(--muted); font-size:13px; }
    .muted { color:var(--muted); }
    .toast { position:fixed; right:18px; bottom:18px; max-width:min(380px,calc(100vw - 36px)); background:var(--ink-bright); color:#f8fafc; padding:10px 16px; border-radius:8px; box-shadow:var(--shadow-md); display:none; z-index:300; font-size:13px; }
    a { color:var(--gold); text-decoration:none; }
    a:hover { color:var(--gold-bright); }

    /* ── Log panel ── */
    .logpanel { position:fixed; bottom:0; left:0; right:0; z-index:40; font-family:'Menlo','Consolas',monospace; font-size:11px; }
    .logpanel-header { display:flex; align-items:center; gap:10px; padding:5px 16px; background:#1e293b; color:#94a3b8; cursor:pointer; border-top:1px solid #334155; user-select:none; }
    .logpanel-header:hover { background:#263347; }
    .logpanel-title { font-weight:600; letter-spacing:.06em; text-transform:uppercase; font-size:10px; }
    .logpanel-badge { background:#334155; border-radius:999px; padding:1px 7px; font-size:10px; }
    .logpanel-toggle { margin-left:auto; font-size:10px; color:#475569; transition:transform .2s; }
    .logpanel-toggle.open { transform:rotate(180deg); }
    .logpanel-body { background:#0f172a; max-height:180px; overflow-y:auto; display:none; border-top:1px solid #1e293b; }
    .logpanel-body.open { display:block; }
    .logpanel-body::-webkit-scrollbar { width:4px; }
    .logpanel-body::-webkit-scrollbar-thumb { background:#334155; }
    .log-row { display:grid; grid-template-columns:72px 40px 80px 1fr; gap:8px; padding:3px 16px; border-bottom:1px solid rgba(255,255,255,.03); align-items:baseline; }
    .log-row:last-child { border-bottom:0; }
    .log-t { color:#475569; font-size:10px; }
    .log-level { font-weight:700; font-size:10px; }
    .log-level.INFO  { color:#38bdf8; }
    .log-level.WARN  { color:#fb923c; }
    .log-level.ERROR,.log-level.CRIT { color:#f87171; }
    .log-level.DEBUG { color:#6b7280; }
    .log-logger { color:#64748b; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
    .log-msg { color:#cbd5e1; white-space:pre-wrap; word-break:break-all; }

    /* ── Airport Autocomplete ── */
    .ac-root { position:relative; }
    .ac-display { padding-right:28px; cursor:text; }
    .ac-clear {
      position:absolute; right:8px; top:50%; transform:translateY(-50%);
      color:var(--muted); font-size:14px; cursor:pointer; display:none; line-height:1;
      border:none; background:none; padding:0; min-height:unset;
    }
    .ac-clear:hover { color:var(--gold); }
    .ac-list {
      display:none; position:absolute; top:calc(100% + 4px); left:0; right:0;
      background:var(--layer); border:1px solid var(--line-bright); border-radius:7px;
      z-index:100; box-shadow:var(--shadow-md); overflow:hidden; max-height:260px; overflow-y:auto;
    }
    .ac-list::-webkit-scrollbar { width:4px; }
    .ac-list::-webkit-scrollbar-thumb { background:var(--line-bright); border-radius:2px; }
    .ac-item { display:grid; grid-template-columns:44px 1fr auto; align-items:center; gap:10px; padding:8px 12px; cursor:pointer; border-bottom:1px solid var(--line); transition:background .1s; }
    .ac-item:last-child { border-bottom:0; }
    .ac-item:hover, .ac-item.focused { background:var(--gold-glow); }
    .ac-iata-tag { font-size:13px; font-weight:700; letter-spacing:.04em; color:var(--gold); }
    .ac-label { font-size:12px; color:var(--ink); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
    .ac-label em { font-style:normal; color:var(--gold); font-weight:600; }
    .ac-country-tag { font-size:10px; color:var(--muted); letter-spacing:.05em; text-transform:uppercase; }
    .ac-hint { padding:8px 12px; font-size:11px; color:var(--muted); text-align:center; }
    .ac-item-city { background:var(--gold-glow); border-bottom:1px solid rgba(146,104,10,.15) !important; }
    .ac-item-city:hover, .ac-item-city.focused { background:rgba(146,104,10,.15); }
    .ac-city-tag { color:var(--gold-bright) !important; }
    .ac-all-badge { display:inline-block; background:var(--gold); color:#fff; font-size:9px; font-weight:700; letter-spacing:.05em; text-transform:uppercase; border-radius:3px; padding:1px 5px; margin-left:4px; vertical-align:middle; }

    /* ── Fare Calendar ── */
    .cal-wrap { width:min(1280px,100%); margin:0 auto 80px; padding:0 24px; }
    .cal-header {
      display:flex; align-items:center; justify-content:space-between;
      padding:12px 18px; background:var(--layer); border:1px solid var(--line);
      border-radius:var(--radius); cursor:pointer; user-select:none;
      transition:border-color .15s, box-shadow .15s;
    }
    .cal-header:hover { border-color:var(--gold-dim); box-shadow:var(--shadow); }
    .cal-header.open { border-bottom-left-radius:0; border-bottom-right-radius:0; }
    .cal-title { font-size:13px; font-weight:600; color:var(--ink-bright); }
    .cal-sub { font-size:11px; color:var(--muted); margin-left:4px; }
    .cal-arrow { font-size:11px; color:var(--muted); transition:transform .2s; }
    .cal-arrow.open { transform:rotate(180deg); }
    .cal-body {
      display:none; background:var(--layer); border:1px solid var(--line); border-top:0;
      border-radius:0 0 var(--radius) var(--radius); padding:16px 18px;
    }
    .cal-body.open { display:block; }
    .cal-form {
      display:grid; grid-template-columns:1fr 1fr auto auto; gap:8px;
      align-items:end; margin-bottom:16px;
    }
    .cal-result-header {
      display:flex; align-items:center; justify-content:space-between; gap:12px; margin-bottom:12px;
    }
    .cal-month-title {
      font-size:11px; font-weight:700; letter-spacing:.1em; text-transform:uppercase;
      color:var(--gold);
    }
    .cal-monitor-btn {
      appearance:none; background:var(--gold-glow); border:1px solid var(--gold-dim);
      border-radius:6px; color:var(--gold); font:inherit; font-size:11px; font-weight:600;
      padding:4px 12px; cursor:pointer; white-space:nowrap; transition:background .15s,box-shadow .15s;
    }
    .cal-monitor-btn:hover { background:var(--gold); color:#fff; box-shadow:var(--shadow); }
    .cal-grid {
      display:grid; grid-template-columns:repeat(7,1fr); gap:4px;
    }
    .cal-day-hdr {
      text-align:center; font-size:10px; font-weight:600; letter-spacing:.07em;
      text-transform:uppercase; color:var(--muted); padding:4px 2px;
    }
    .cal-day-cell {
      min-height:58px; border-radius:6px; border:1px solid var(--line);
      padding:5px 6px; display:flex; flex-direction:column; gap:2px;
      background:var(--bg); transition:transform .1s, box-shadow .1s;
    }
    .cal-day-cell.empty { border-color:transparent; background:transparent; }
    .cal-day-cell.has-price { cursor:pointer; }
    .cal-day-cell.has-price:hover { transform:translateY(-2px); box-shadow:var(--shadow); z-index:2; }
    .cal-day-num { font-size:11px; font-weight:600; color:var(--ink-bright); line-height:1; }
    .cal-day-price { font-size:13px; font-weight:700; line-height:1.2; margin-top:2px; }
    .cal-day-airline { font-size:9px; font-weight:600; letter-spacing:.05em; color:rgba(0,0,0,.5); }
    .cal-legend {
      display:flex; align-items:center; gap:6px; margin-top:12px;
      font-size:10px; color:var(--muted); justify-content:flex-end;
    }
    .cal-legend-bar {
      width:120px; height:8px; border-radius:4px;
      background:linear-gradient(to right,#4ade80,#facc15,#ef4444);
    }

    @media(max-width:880px) {
      header { padding:0 16px; }
      main { grid-template-columns:1fr; padding:14px; }
      .cal-form { grid-template-columns:1fr 1fr; }
      .cal-wrap { padding:0 14px; }
    }
  </style>
</head>
<body>

<!-- Setup overlay (prima visita) -->
<div class="overlay" id="setupOverlay">
  <div class="setup-card">
    <h2>Benvenuto su NicoWay</h2>
    <p>Inserisci il tuo <strong>Telegram chat ID</strong> per iniziare. Puoi trovarlo scrivendo a @userinfobot su Telegram.</p>
    <label>Telegram Chat ID
      <input id="setupInput" inputmode="numeric" placeholder="123456789" autofocus>
    </label>
    <button class="primary" id="setupBtn">Inizia</button>
  </div>
</div>

<header>
  <div class="logo">
    <span class="logo-name">NicoWay</span>
    <span class="logo-tag">Flight Tracker</span>
  </div>
  <div class="toolbar">
    <span class="status"><span id="healthDot" class="dot"></span><span id="healthText">checking…</span></span>
    <div class="account-chip" id="accountChip" title="Cambia account">
      <span class="chip-dot"></span>
      <span class="chip-label">Chat ID:</span>
      <span class="chip-id" id="chipId">—</span>
    </div>
    <button id="refreshBtn">Aggiorna</button>
  </div>
</header>

<main>
  <aside>
    <div class="guide">
      <div class="guide-toggle" id="guideToggle">
        <span>ⓘ Come funziona</span>
        <span class="arrow">▼</span>
      </div>
      <div class="guide-body" id="guideBody">
        <div class="guide-step"><span class="guide-num">1</span><span>Inserisci il tuo <strong>Telegram Chat ID</strong> (in alto a destra). Trovi il tuo ID scrivendo a <strong>@userinfobot</strong> su Telegram.</span></div>
        <div class="guide-step"><span class="guide-num">2</span><span>Aggiungi una <strong>tratta singola</strong> o un <strong>viaggio multi-tratta</strong> con i tuoi criteri: rotta, date, budget e numero di scali accettati.</span></div>
        <div class="guide-step"><span class="guide-num">3</span><span>Il sistema cerca voli automaticamente ogni N minuti. Quando trova un'offerta sotto budget, la salva e ti manda una notifica su Telegram.</span></div>
        <div class="guide-step"><span class="guide-num">4</span><span>Premi <strong>Check</strong> per cercare subito senza aspettare il ciclo automatico.</span></div>
        <div class="guide-step"><span class="guide-num">5</span><span><strong>Prenota</strong> apre una ricerca su Kayak per quella rotta e quella data. Con una API reale il link porta direttamente all'offerta specifica.</span></div>
      </div>
    </div>
    <div class="aside-block">
      <div class="mode-tabs">
        <button class="mode-tab active" data-tab="single">✈ Tratta singola</button>
        <button class="mode-tab" data-tab="multi">🗺 Multi-tratta</button>
      </div>

      <!-- Tratta singola -->
      <div class="mode-pane visible" id="pane-single">
        <form id="searchForm">
          <div class="grid-2">
            <label>Partenza<div class="ac-root"><input type="text" class="ac-display" placeholder="Roma, FCO…" autocomplete="off"><input type="hidden" name="origin" class="ac-value"><button type="button" class="ac-clear">×</button><div class="ac-list"></div></div></label>
            <label>Arrivo<div class="ac-root"><input type="text" class="ac-display" placeholder="Londra, LHR…" autocomplete="off"><input type="hidden" name="destination" class="ac-value"><button type="button" class="ac-clear">×</button><div class="ac-list"></div></div></label>
          </div>
          <div class="grid-2">
            <label>Dal<input name="date_from" required type="date"></label>
            <label>Al<input name="date_to" required type="date"></label>
          </div>
          <div class="grid-3">
            <label>Adulti<input name="adults" type="number" value="2" min="1"></label>
            <label>Flex. giorni<span class="tip" data-tip="Allarga la ricerca ai giorni vicini alla data 'Al'. Es: 2 = cerca anche 2 giorni prima e dopo.">i</span><input name="flexible_days" type="number" value="0" min="0"></label>
            <label>Scali<input name="max_stops" type="number" value="0" min="-1" placeholder="0=diretto, -1=qualsiasi"></label>
          </div>
          <div class="grid-2">
            <label>Budget max (€)<span class="tip" data-tip="Prezzo totale massimo accettato (volo × adulti). Offerte sopra soglia vengono ignorate.">i</span><input name="max_budget_total" required type="number" min="1" placeholder="500"></label>
            <label>Cap volo (€)<span class="tip" data-tip="Opzionale. Prezzo massimo per il solo volo, indipendente dal budget totale.">i</span><input name="max_flight_price" type="number" min="0" placeholder="—"></label>
          </div>
          <button class="primary" type="submit" style="margin-top:2px;">Aggiungi tratta</button>
        </form>
      </div>

      <!-- Multi-tratta -->
      <div class="mode-pane" id="pane-multi">
        <form id="tripForm">
          <div id="legsContainer" style="display:grid;gap:10px;"></div>
          <button type="button" id="addLegBtn" class="ghost" style="justify-self:start;">+ Aggiungi tratta</button>
          <button class="primary" type="submit">Crea viaggio</button>
        </form>
      </div>
    </div>
  </aside>

  <section>
    <div class="section-head">
      <h2 style="margin:0;">Tratte monitorate</h2>
      <span id="count" class="muted" style="font-size:11px;">—</span>
    </div>
    <div id="searches"></div>
  </section>
</main>

<!-- Fare calendar -->
<div class="cal-wrap">
  <div class="cal-header" id="calToggle">
    <div style="display:flex;align-items:center;gap:10px;">
      <span style="font-size:15px;">📅</span>
      <span class="cal-title">Tariffe del mese</span>
      <span class="cal-sub">Trova il giorno più economico sulla tua rotta</span>
    </div>
    <span class="cal-arrow" id="calArrow">▼</span>
  </div>
  <div class="cal-body" id="calBody">
    <div class="cal-form">
      <label>Partenza
        <div class="ac-root"><input type="text" class="ac-display" id="calOriginDisplay" placeholder="Roma, FCO…" autocomplete="off"><input type="hidden" id="calOrigin" class="ac-value"><button type="button" class="ac-clear">×</button><div class="ac-list"></div></div>
      </label>
      <label>Arrivo
        <div class="ac-root"><input type="text" class="ac-display" id="calDestDisplay" placeholder="Londra, LHR…" autocomplete="off"><input type="hidden" id="calDest" class="ac-value"><button type="button" class="ac-clear">×</button><div class="ac-list"></div></div>
      </label>
      <label>Mese<input type="month" id="calMonth" min="2024-01"></label>
      <button class="primary" id="calSearchBtn">Cerca</button>
    </div>
    <div id="calResult"></div>
  </div>
</div>

<div id="toast" class="toast"></div>

<!-- Log panel -->
<div class="logpanel" id="logPanel">
  <div class="logpanel-header" id="logHeader">
    <span>●</span>
    <span class="logpanel-title">Activity Log</span>
    <span class="logpanel-badge" id="logBadge">0</span>
    <span class="logpanel-toggle" id="logToggleArrow">▲</span>
  </div>
  <div class="logpanel-body" id="logBody"></div>
</div>

<script>
/* ════════════════════════════════════════════════
   AIRPORT DATABASE  [IATA, City, Name, Country]
   ════════════════════════════════════════════════ */
const AIRPORTS = [
  ["FCO","Roma","Fiumicino","IT"],["CIA","Roma","Ciampino","IT"],
  ["MXP","Milano","Malpensa","IT"],["LIN","Milano","Linate","IT"],["BGY","Bergamo","Orio al Serio","IT"],
  ["NAP","Napoli","Capodichino","IT"],["VCE","Venezia","Marco Polo","IT"],["TSF","Venezia","Treviso","IT"],
  ["BLQ","Bologna","Marconi","IT"],["TRN","Torino","Caselle","IT"],["PSA","Pisa","Galileo Galilei","IT"],
  ["PMO","Palermo","Falcone-Borsellino","IT"],["CTA","Catania","Fontanarossa","IT"],
  ["BRI","Bari","Karol Wojtyla","IT"],["AOI","Ancona","Falconara","IT"],["FLR","Firenze","Peretola","IT"],
  ["GOA","Genova","Cristoforo Colombo","IT"],["OLB","Olbia","Costa Smeralda","IT"],
  ["CAG","Cagliari","Elmas","IT"],["PMF","Parma","Parma","IT"],["VRN","Verona","Catullo","IT"],
  ["BDS","Brindisi","Casale","IT"],["REG","Reggio Calabria","Tito Minniti","IT"],
  ["LHR","Londra","Heathrow","GB"],["LGW","Londra","Gatwick","GB"],["STN","Londra","Stansted","GB"],
  ["LTN","Londra","Luton","GB"],["LCY","Londra","City","GB"],["EDI","Edimburgo","Edinburgh","GB"],
  ["GLA","Glasgow","International","GB"],["MAN","Manchester","Manchester","GB"],
  ["BRS","Bristol","Bristol","GB"],["BHX","Birmingham","Birmingham","GB"],["NCL","Newcastle","Newcastle","GB"],
  ["LPL","Liverpool","John Lennon","GB"],["ABZ","Aberdeen","Aberdeen","GB"],["INV","Inverness","Inverness","GB"],
  ["CDG","Parigi","Charles de Gaulle","FR"],["ORY","Parigi","Orly","FR"],["NCE","Nizza","Côte d'Azur","FR"],
  ["MRS","Marsiglia","Provence","FR"],["LYS","Lione","Saint-Exupéry","FR"],["BOD","Bordeaux","Mérignac","FR"],
  ["TLS","Tolosa","Blagnac","FR"],["NTE","Nantes","Atlantique","FR"],["SXB","Strasburgo","Entzheim","FR"],
  ["MPL","Montpellier","Méditerranée","FR"],["BIQ","Biarritz","Pays Basque","FR"],
  ["FRA","Francoforte","Frankfurt","DE"],["MUC","Monaco","Franz Josef Strauss","DE"],["BER","Berlino","Brandenburg","DE"],
  ["HAM","Amburgo","Hamburg","DE"],["DUS","Düsseldorf","Düsseldorf","DE"],["CGN","Colonia","Bonn","DE"],
  ["STR","Stoccarda","Stuttgart","DE"],["NUE","Norimberga","Nuremberg","DE"],["HAJ","Hannover","Hannover","DE"],
  ["LEJ","Lipsia","Leipzig/Halle","DE"],["DTM","Dortmund","Dortmund","DE"],
  ["MAD","Madrid","Barajas","ES"],["BCN","Barcellona","El Prat","ES"],["PMI","Palma di Maiorca","Son Sant Joan","ES"],
  ["AGP","Malaga","Costa del Sol","ES"],["ALC","Alicante","El Altet","ES"],["VLC","Valencia","Manises","ES"],
  ["SVQ","Siviglia","San Pablo","ES"],["IBZ","Ibiza","Ibiza","ES"],["TFS","Tenerife","Sur","ES"],
  ["LPA","Gran Canaria","Las Palmas","ES"],["ACE","Lanzarote","Arrecife","ES"],["FUE","Fuerteventura","El Matorral","ES"],
  ["SDR","Santander","Parayas","ES"],["BIO","Bilbao","Bilbao","ES"],["SCQ","Santiago de Compostela","Lavacolla","ES"],
  ["LIS","Lisbona","Humberto Delgado","PT"],["OPO","Porto","Francisco de Sá Carneiro","PT"],
  ["FAO","Faro","Faro","PT"],["FNC","Madeira","Cristiano Ronaldo","PT"],["PDL","Azzorre","João Paulo II","PT"],
  ["AMS","Amsterdam","Schiphol","NL"],["EIN","Eindhoven","Eindhoven","NL"],["RTM","Rotterdam","The Hague","NL"],
  ["BRU","Bruxelles","Zaventem","BE"],["CRL","Bruxelles","Charleroi","BE"],["LGG","Liegi","Liège","BE"],
  ["LUX","Lussemburgo","Findel","LU"],
  ["ZRH","Zurigo","Kloten","CH"],["GVA","Ginevra","Cointrin","CH"],["BSL","Basilea","EuroAirport","CH"],
  ["VIE","Vienna","Schwechat","AT"],["GRZ","Graz","Thalerhof","AT"],["SZG","Salisburgo","W. A. Mozart","AT"],["INN","Innsbruck","Innsbruck","AT"],
  ["OSL","Oslo","Gardermoen","NO"],["BGO","Bergen","Flesland","NO"],["TRD","Trondheim","Vaernes","NO"],
  ["ARN","Stoccolma","Arlanda","SE"],["GOT","Göteborg","Landvetter","SE"],["MMX","Malmö","Sturup","SE"],
  ["CPH","Copenaghen","Kastrup","DK"],["BLL","Billund","Billund","DK"],["AAR","Aarhus","Tirstrup","DK"],
  ["HEL","Helsinki","Vantaa","FI"],["TMP","Tampere","Pirkkala","FI"],["OUL","Oulu","Oulu","FI"],
  ["KEF","Reykjavik","Keflavik","IS"],
  ["WAW","Varsavia","Chopin","PL"],["KRK","Cracovia","John Paul II","PL"],["GDN","Danzica","Lech Walesa","PL"],
  ["WRO","Breslavia","Copernicus","PL"],["PRG","Praga","Václav Havel","CZ"],["BRQ","Brno","Tuřany","CZ"],
  ["BUD","Budapest","Ferenc Liszt","HU"],["OTP","Bucarest","Henri Coanda","RO"],["CLJ","Cluj-Napoca","Avram Iancu","RO"],
  ["SOF","Sofia","Sofia","BG"],["SKP","Skopje","Alexander the Great","MK"],["TIA","Tirana","Nënë Tereza","AL"],
  ["BEG","Belgrado","Nikola Tesla","RS"],["ZAG","Zagabria","Franjo Tuđman","HR"],["SPU","Spalato","Split","HR"],
  ["DBV","Dubrovnik","Dubrovnik","HR"],["LJU","Lubiana","Jože Pučnik","SI"],["SJJ","Sarajevo","Sarajevo","BA"],
  ["ATH","Atene","Eleftherios Venizelos","GR"],["HER","Heraklion","Nikos Kazantzakis","GR"],
  ["RHO","Rodi","Diagoras","GR"],["JTR","Santorini","Thira","GR"],["SKG","Salonicco","Makedonia","GR"],
  ["CFU","Corfù","Ioannis Kapodistrias","GR"],["ZTH","Zante","Zakynthos","GR"],["KGS","Kos","Ippokratis","GR"],
  ["RIX","Riga","Riga","LV"],["TLL","Tallinn","Lennart Meri","EE"],["VNO","Vilnius","Vilnius","LT"],
  ["KIV","Chisinau","Chisinau","MD"],["KBP","Kiev","Boryspil","UA"],["LWO","Leopoli","Danylo Halytskyi","UA"],
  ["IST","Istanbul","Istanbul","TR"],["SAW","Istanbul","Sabiha Gökçen","TR"],["AYT","Antalya","Antalya","TR"],
  ["DLM","Dalaman","Dalaman","TR"],["BJV","Bodrum","Milas","TR"],["ADB","Smirne","Adnan Menderes","TR"],
  ["ESB","Ankara","Esenboğa","TR"],["TZX","Trebisonda","Trabzon","TR"],
  ["SVO","Mosca","Sheremetyevo","RU"],["DME","Mosca","Domodedovo","RU"],["LED","San Pietroburgo","Pulkovo","RU"],
  ["DUB","Dublino","Dublin","IE"],["SNN","Shannon","Shannon","IE"],["ORK","Cork","Cork","IE"],
  ["DXB","Dubai","International","AE"],["AUH","Abu Dhabi","Zayed","AE"],["SHJ","Sharjah","Sharjah","AE"],
  ["DOH","Doha","Hamad","QA"],["KWI","Kuwait City","Kuwait","KW"],["BAH","Manama","Bahrain","BH"],
  ["MCT","Muscat","Muscat","OM"],["AMM","Amman","Queen Alia","JO"],["BEY","Beirut","Rafic Hariri","LB"],
  ["TLV","Tel Aviv","Ben Gurion","IL"],["RUH","Riyadh","King Khalid","SA"],["JED","Jeddah","King Abdulaziz","SA"],
  ["CAI","Il Cairo","Cairo","EG"],["HRG","Hurghada","Hurghada","EG"],["SSH","Sharm el-Sheikh","Sharm","EG"],
  ["CMN","Casablanca","Mohammed V","MA"],["RAK","Marrakech","Menara","MA"],["TNG","Tangeri","Ibn Batouta","MA"],
  ["FEZ","Fes","Saïss","MA"],["AGA","Agadir","Al Massira","MA"],
  ["TUN","Tunisi","Carthage","TN"],["DJE","Djerba","Zarzis","TN"],["MIR","Monastir","Habib Bourguiba","TN"],
  ["ALG","Algeri","Houari Boumediene","DZ"],["ORN","Orano","Es Sénia","DZ"],
  ["JNB","Johannesburg","O.R. Tambo","ZA"],["CPT","Città del Capo","Cape Town","ZA"],["DUR","Durban","King Shaka","ZA"],
  ["NBO","Nairobi","Jomo Kenyatta","KE"],["MBA","Mombasa","Moi","KE"],
  ["DAR","Dar es Salaam","Julius Nyerere","TZ"],["ZNZ","Zanzibar","Abeid Karume","TZ"],
  ["ADD","Addis Abeba","Bole","ET"],["LOS","Lagos","Murtala Muhammed","NG"],["ACC","Accra","Kotoka","GH"],
  ["MRU","Mauritius","Sir Seewoosagur","MU"],["RUN","Réunion","Roland Garros","RE"],["SEZ","Seychelles","Mahé","SC"],
  ["DEL","Nuova Delhi","Indira Gandhi","IN"],["BOM","Mumbai","Chhatrapati Shivaji","IN"],
  ["BLR","Bangalore","Kempegowda","IN"],["MAA","Chennai","Chennai","IN"],["HYD","Hyderabad","Rajiv Gandhi","IN"],
  ["GOI","Goa","Dabolim","IN"],["CMB","Colombo","Bandaranaike","LK"],["MLE","Male","Velana","MV"],
  ["KTM","Kathmandu","Tribhuvan","NP"],["KHI","Karachi","Jinnah","PK"],["ISB","Islamabad","Islamabad","PK"],
  ["SIN","Singapore","Changi","SG"],["KUL","Kuala Lumpur","KLIA","MY"],["PEN","Penang","Penang","MY"],
  ["BKK","Bangkok","Suvarnabhumi","TH"],["DMK","Bangkok","Don Mueang","TH"],["HKT","Phuket","Phuket","TH"],
  ["CNX","Chiang Mai","Chiang Mai","TH"],["CGK","Giacarta","Soekarno-Hatta","ID"],["DPS","Bali","Ngurah Rai","ID"],
  ["MNL","Manila","Ninoy Aquino","PH"],["CEB","Cebu","Mactan","PH"],
  ["SGN","Ho Chi Minh","Tan Son Nhat","VN"],["HAN","Hanoi","Noi Bai","VN"],["DAD","Da Nang","Da Nang","VN"],
  ["HKG","Hong Kong","Hong Kong","HK"],["PVG","Shanghai","Pudong","CN"],["PEK","Pechino","Capital","CN"],
  ["CAN","Guangzhou","Baiyun","CN"],["CTU","Chengdu","Tianfu","CN"],["SZX","Shenzhen","Shenzhen","CN"],
  ["NRT","Tokyo","Narita","JP"],["HND","Tokyo","Haneda","JP"],["KIX","Osaka","Kansai","JP"],
  ["CTS","Sapporo","New Chitose","JP"],["OKA","Okinawa","Naha","JP"],["FUK","Fukuoka","Fukuoka","JP"],
  ["ICN","Seoul","Incheon","KR"],["GMP","Seoul","Gimpo","KR"],["PUS","Busan","Gimhae","KR"],["CJU","Jeju","Jeju","KR"],
  ["TPE","Taipei","Taoyuan","TW"],["KHH","Kaohsiung","Kaohsiung","TW"],
  ["SYD","Sydney","Kingsford Smith","AU"],["MEL","Melbourne","Tullamarine","AU"],["BNE","Brisbane","Brisbane","AU"],
  ["PER","Perth","Perth","AU"],["ADL","Adelaide","Adelaide","AU"],["CNS","Cairns","Cairns","AU"],
  ["AKL","Auckland","Auckland","NZ"],["CHC","Christchurch","Christchurch","NZ"],["WLG","Wellington","Wellington","NZ"],
  ["NAN","Nadi","Nadi","FJ"],["PPT","Papeete","Fa'a'ā","PF"],
  ["JFK","New York","John F. Kennedy","US"],["EWR","New York","Newark","US"],["LGA","New York","LaGuardia","US"],
  ["LAX","Los Angeles","Los Angeles","US"],["SFO","San Francisco","San Francisco","US"],
  ["ORD","Chicago","O'Hare","US"],["MIA","Miami","Miami","US"],["ATL","Atlanta","Hartsfield-Jackson","US"],
  ["DFW","Dallas","Fort Worth","US"],["BOS","Boston","Logan","US"],["DCA","Washington","Reagan National","US"],
  ["IAD","Washington","Dulles","US"],["SEA","Seattle","Sea-Tac","US"],["LAS","Las Vegas","Harry Reid","US"],
  ["PHX","Phoenix","Sky Harbor","US"],["DEN","Denver","Denver","US"],["MCO","Orlando","Orlando","US"],
  ["HNL","Honolulu","Daniel K. Inouye","US"],["SAN","San Diego","San Diego","US"],
  ["YYZ","Toronto","Pearson","CA"],["YVR","Vancouver","Vancouver","CA"],["YUL","Montréal","Trudeau","CA"],
  ["MEX","Città del Messico","Benito Juárez","MX"],["CUN","Cancún","Cancún","MX"],
  ["GDL","Guadalajara","Miguel Hidalgo","MX"],["SJO","San José","Juan Santamaría","CR"],
  ["PTY","Panama City","Tocumen","PA"],["HAV","L'Avana","José Martí","CU"],
  ["GRU","São Paulo","Guarulhos","BR"],["GIG","Rio de Janeiro","Galeão","BR"],["BSB","Brasilia","Presidente Juscelino","BR"],
  ["EZE","Buenos Aires","Ministro Pistarini","AR"],["AEP","Buenos Aires","Aeroparque","AR"],
  ["SCL","Santiago","Arturo Merino Benítez","CL"],["LIM","Lima","Jorge Chávez","PE"],["CUZ","Cusco","Alejandro Velasco","PE"],
  ["BOG","Bogotá","El Dorado","CO"],["MDE","Medellín","José María Córdova","CO"],
  ["UIO","Quito","Mariscal Sucre","EC"],["GYE","Guayaquil","José Joaquín de Olmedo","EC"],
  ["MVD","Montevideo","Carrasco","UY"],["ASU","Asunción","Silvio Pettirossi","PY"],
];

/* ════════════════════════════════════════════════
   CITY CODES — multi-airport cities
   [cityCode, cityName, [iata…], country]
   ════════════════════════════════════════════════ */
const CITY_CODES = [
  ["ROM","Roma",["FCO","CIA"],"IT"],
  ["MIL","Milano",["MXP","LIN","BGY"],"IT"],
  ["LON","Londra",["LHR","LGW","STN","LTN","LCY"],"GB"],
  ["PAR","Parigi",["CDG","ORY"],"FR"],
  ["NYC","New York",["JFK","EWR","LGA"],"US"],
  ["CHI","Chicago",["ORD","MDW"],"US"],
  ["WAS","Washington",["DCA","IAD","BWI"],"US"],
  ["LAX","Los Angeles",["LAX","BUR","SNA","LGB"],"US"],
  ["SFB","San Francisco",["SFO","OAK","SJC"],"US"],
  ["MOW","Mosca",["SVO","DME","VKO"],"RU"],
  ["TYO","Tokyo",["NRT","HND"],"JP"],
  ["SEL","Seoul",["ICN","GMP"],"KR"],
  ["BKS","Bangkok",["BKK","DMK"],"TH"],
  ["IST","Istanbul",["IST","SAW"],"TR"],
  ["BUE","Buenos Aires",["EZE","AEP"],"AR"],
  ["SAO","São Paulo",["GRU","CGH"],"BR"],
  ["SHA","Shanghai",["PVG","SHA"],"CN"],
  ["STO","Stoccolma",["ARN","GOT","MMX"],"SE"],
  ["OSL","Oslo",["OSL","TRF"],"NO"],
  ["DUB","Dubai",["DXB","DWC"],"AE"],
];

/* ════════════════════════════════════════════════
   SESSION — chat_id in localStorage
   ════════════════════════════════════════════════ */
const LS_KEY = "nicoway_chat_id";

function getChatId() { return localStorage.getItem(LS_KEY) || ""; }
function setChatId(v) {
  localStorage.setItem(LS_KEY, v);
  updateChip();
}

function updateChip() {
  const id = getChatId();
  const chip = document.getElementById("accountChip");
  document.getElementById("chipId").textContent = id || "—";
  chip.classList.toggle("set", !!id);
}

document.getElementById("accountChip").addEventListener("click", () => {
  const cur = getChatId();
  const v = prompt("Inserisci il tuo Telegram Chat ID:", cur);
  if(v === null) return;
  const n = v.trim();
  if(!n || isNaN(Number(n))) { toast("Chat ID non valido."); return; }
  setChatId(n);
  render();
});

document.getElementById("setupBtn").addEventListener("click", () => {
  const v = document.getElementById("setupInput").value.trim();
  if(!v || isNaN(Number(v))) { toast("Inserisci un Chat ID valido."); return; }
  setChatId(v);
  document.getElementById("setupOverlay").classList.add("hidden");
  render();
});

document.getElementById("setupInput").addEventListener("keydown", e => {
  if(e.key === "Enter") document.getElementById("setupBtn").click();
});

/* ════════════════════════════════════════════════
   AUTOCOMPLETE ENGINE
   ════════════════════════════════════════════════ */
function highlight(text, query) {
  if(!query) return text;
  const idx = text.toLowerCase().indexOf(query.toLowerCase());
  if(idx < 0) return text;
  return text.slice(0,idx)+"<em>"+text.slice(idx,idx+query.length)+"</em>"+text.slice(idx+query.length);
}

function searchAirports(q) {
  const lq = q.toLowerCase().trim();
  if(!lq) return [];
  // City codes first (multi-airport entries)
  const cities = CITY_CODES.filter(([code,city,,country]) =>
    code.toLowerCase().startsWith(lq)||city.toLowerCase().includes(lq)
  ).map(([code,city,airports,country]) => ({isCity:true, code, city, airports, country}));
  // Individual airports
  const airports = AIRPORTS.filter(([iata,city,name,country]) =>
    iata.toLowerCase().startsWith(lq)||city.toLowerCase().includes(lq)||
    name.toLowerCase().includes(lq)||country.toLowerCase().includes(lq)
  ).sort((a,b) => {
    const ai=a[0].toLowerCase()===lq?0:1, bi=b[0].toLowerCase()===lq?0:1;
    if(ai!==bi) return ai-bi;
    return (a[1].toLowerCase().startsWith(lq)?0:1)-(b[1].toLowerCase().startsWith(lq)?0:1);
  }).slice(0,8);
  return [...cities, ...airports];
}

function initAC(root) {
  if(root.dataset.acReady) return;
  root.dataset.acReady="1";
  const display=root.querySelector(".ac-display"), hidden=root.querySelector(".ac-value");
  const clearBtn=root.querySelector(".ac-clear"), list=root.querySelector(".ac-list");
  let focusedIdx=-1;
  function getItems(){ return list.querySelectorAll(".ac-item"); }
  function close(){ list.style.display="none"; focusedIdx=-1; }
  function select(iata,label){ hidden.value=iata; display.value=label; clearBtn.style.display="block"; close(); }
  function renderResults(q){
    const results=searchAirports(q); focusedIdx=-1;
    if(!results.length){ list.innerHTML=`<div class="ac-hint">Nessun aeroporto trovato per "${q}"</div>`; list.style.display="block"; return; }
    list.innerHTML=results.map(r=>{
      if(r.isCity){
        const sub=r.airports.join(", ");
        return `<div class="ac-item ac-item-city" data-iata="${r.code}" data-label="${r.code} – ${r.city} (tutti)">
          <span class="ac-iata-tag ac-city-tag">${r.code}</span>
          <span class="ac-label"><strong>${highlight(r.city,q)}</strong> <span class="ac-all-badge">tutti gli aeroporti</span><br><span style="font-size:10px;color:var(--muted);">${sub}</span></span>
          <span class="ac-country-tag">${r.country}</span>
        </div>`;
      }
      const[iata,city,name,country]=r;
      return `<div class="ac-item" data-iata="${iata}" data-label="${iata} – ${city} ${name}">
        <span class="ac-iata-tag">${iata}</span>
        <span class="ac-label">${highlight(city,q)} ${highlight(name,q)}</span>
        <span class="ac-country-tag">${country}</span>
      </div>`;
    }).join("");
    list.style.display="block";
  }
  display.addEventListener("input",()=>{ const q=display.value.trim(); hidden.value=""; clearBtn.style.display=q?"block":"none"; if(q.length<1){close();return;} renderResults(q); });
  display.addEventListener("keydown",e=>{
    const items=getItems(); if(!items.length) return;
    if(e.key==="ArrowDown"){e.preventDefault();items[focusedIdx]?.classList.remove("focused");focusedIdx=Math.min(focusedIdx+1,items.length-1);items[focusedIdx]?.classList.add("focused");items[focusedIdx]?.scrollIntoView({block:"nearest"});}
    else if(e.key==="ArrowUp"){e.preventDefault();items[focusedIdx]?.classList.remove("focused");focusedIdx=Math.max(focusedIdx-1,0);items[focusedIdx]?.classList.add("focused");items[focusedIdx]?.scrollIntoView({block:"nearest"});}
    else if(e.key==="Enter"&&focusedIdx>=0){e.preventDefault();const item=items[focusedIdx];select(item.dataset.iata,item.dataset.label);}
    else if(e.key==="Escape") close();
  });
  display.addEventListener("focus",()=>{ if(display.value.trim()) renderResults(display.value.trim()); });
  list.addEventListener("mousedown",e=>{ const item=e.target.closest(".ac-item"); if(!item) return; e.preventDefault(); select(item.dataset.iata,item.dataset.label); });
  clearBtn.addEventListener("click",()=>{ display.value=""; hidden.value=""; clearBtn.style.display="none"; close(); display.focus(); });
  document.addEventListener("click",e=>{ if(!root.contains(e.target)) close(); });
}

function initAllAC(){ document.querySelectorAll(".ac-root").forEach(initAC); }

/* ════════════════════════════════════════════════
   APP
   ════════════════════════════════════════════════ */
const $ = id => document.getElementById(id);
let legCount = 0;

function esc(v){ return String(v??"").replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;"); }
function money(v){ if(v==null) return "—"; return new Intl.NumberFormat("it-IT",{style:"currency",currency:"EUR",maximumFractionDigits:0}).format(Number(v)); }
function fmtTime(iso){ if(!iso) return "—"; return new Date(iso).toLocaleTimeString("it-IT",{hour:"2-digit",minute:"2-digit"}); }
function fmtDate(iso){ if(!iso) return ""; return new Date(iso).toLocaleDateString("it-IT",{day:"2-digit",month:"short"}); }
function fmtDt(iso){ if(!iso) return "—"; return new Intl.DateTimeFormat("it-IT",{dateStyle:"short",timeStyle:"short"}).format(new Date(iso)); }
function dur(m){ return Math.floor(m/60)+"h "+String(m%60).padStart(2,"0")+"m"; }
function stopsLabel(n){ if(n===0) return "nonstop"; return n===1?"1 scalo":n+" scali"; }

function toast(msg){
  $("toast").textContent=msg; $("toast").style.display="block";
  clearTimeout(window._t);
  window._t=setTimeout(()=>{ $("toast").style.display="none"; },3200);
}

async function api(path,opts={}){
  const r=await fetch(path,opts);
  if(!r.ok) throw new Error(await r.text());
  return r.json();
}

async function refreshHealth(){
  try{
    const h=await api("/health");
    $("healthDot").classList.add("ok");
    $("healthText").textContent=h.status+" · "+h.env;
  }catch{
    $("healthDot").classList.remove("ok");
    $("healthText").textContent="offline";
  }
}

function airlineBadge(code){
  if(!code) return "";
  const logo=`https://pics.avs.io/36/36/${esc(code)}.png`;
  return `<div class="bp-airline"><img src="${logo}" alt="${esc(code)}" width="36" height="36" onerror="this.style.display='none';this.nextSibling.style.display='inline'"><span style="display:none;font-size:11px;font-weight:700;color:var(--gold);">${esc(code)}</span></div>`;
}

function makeBoardingPass(d){
  const f=d.flight;
  if(!f) return `<div class="bp-card"><div style="padding:12px 16px;color:var(--muted);">Nessun dato volo.</div></div>`;
  const notif=d.is_notified
    ?`<span style="font-size:10px;color:var(--ok);">● notificato</span>`
    :`<span style="font-size:10px;color:var(--muted);">○ non inviato</span>`;
  return `<div class="bp-card">
    <div class="bp-body">
      <div class="bp-airport">
        <div class="bp-iata">${esc(f.origin)}</div>
        <div class="bp-time">${fmtTime(f.departure_datetime)}</div>
        <div class="bp-date-label">${fmtDate(f.departure_datetime)}</div>
      </div>
      <div class="bp-route">
        ${airlineBadge(f.airline)}
        <div class="bp-line"><div class="bp-dash"></div><span class="bp-plane-icon">✈</span><div class="bp-dash"></div></div>
        <div class="bp-dur">${dur(f.duration_minutes)} · ${stopsLabel(f.stops)}</div>
      </div>
      <div class="bp-airport right">
        <div class="bp-iata">${esc(f.destination)}</div>
        <div class="bp-time">${fmtTime(f.arrival_datetime)}</div>
        <div class="bp-date-label">${fmtDate(f.arrival_datetime)}</div>
      </div>
    </div>
    <div class="bp-footer-strip">
      <div>
        <div class="bp-price-big">${money(d.total_estimated_price)}</div>
        <div style="font-size:10px;color:var(--muted);margin-top:1px;">${fmtDt(d.created_at)}</div>
      </div>
      <div class="bp-meta-right">
        <div class="bp-score" title="Punteggio 0–100 calcolato su prezzo, scali, durata e fascia oraria preferita">★ ${Math.round(d.score)}</div>
        ${notif}
        <a class="bp-book" href="${esc(f.booking_url)}" target="_blank" rel="noreferrer" title="Apre una ricerca su Kayak per questa rotta e data — seleziona il volo manualmente">Cerca →</a>
      </div>
    </div>
  </div>`;
}

async function loadDeals(searchId){
  const deals=await api(`/deals/${searchId}`);
  if(!deals.length) return `<div class="deals"><span class="muted" style="font-size:12px;color:var(--muted);">Nessuna offerta salvata ancora.</span></div>`;
  return `<div class="deals">${deals.map(makeBoardingPass).join("")}</div>`;
}

async function render(){
  await refreshHealth();
  const chatId=getChatId();
  const url=chatId?`/searches?telegram_chat_id=${chatId}`:"/searches";
  const searches=await api(url);
  $("count").textContent=searches.length+" tratt"+(searches.length===1?"a":"e");
  if(!searches.length){
    $("searches").innerHTML=`<div class="empty">Nessuna tratta monitorata. Aggiungine una dalla barra laterale.</div>`;
    return;
  }
  const rows=await Promise.all(searches.map(async s=>{
    const dealsHtml=await loadDeals(s.id);
    const stopsText=s.max_stops===0?"nonstop":s.max_stops===-1?"qualsiasi":`max ${s.max_stops} scal${s.max_stops===1?"o":"i"}`;
    return `<div class="search-row" data-id="${s.id}">
      <div class="search-row-head">
        <div>
          <h3>${esc(s.name)}</h3>
          <div class="meta">
            <span class="pill ${s.is_active?"active":"paused"}">${s.is_active?"live":"pausa"}</span>
            ${s.trip_id?`<span class="pill trip">viaggio #${s.trip_id}</span>`:""}
            <span class="meta-item" style="font-weight:600;color:var(--ink);">${esc(s.origin)} → ${esc(s.destination)}</span>
            <span class="meta-item">✈ ${s.date_from}${s.date_to&&s.date_to!==s.date_from?` → ${s.date_to}`:""}</span>
            <span class="meta-item">${stopsText}</span>
            <span class="meta-item">${money(s.max_budget_total)}</span>
            <span class="meta-item" style="font-size:10px;" title="Con questa frequenza il sistema cerca nuovi voli in automatico">ogni ${s.check_frequency_minutes} min</span>
          </div>
        </div>
        <div class="toolbar">
          <button data-action="check" style="font-size:11px;">Check</button>
          <button data-action="${s.is_active?"disable":"enable"}" style="font-size:11px;">${s.is_active?"Pausa":"Attiva"}</button>
          <button class="danger" data-action="delete" style="font-size:11px;">✕</button>
        </div>
      </div>
      ${dealsHtml}
    </div>`;
  }));
  $("searches").innerHTML=rows.join("");
}

$("searches").addEventListener("click",async e=>{
  const btn=e.target.closest("button[data-action]"); if(!btn) return;
  const id=btn.closest("[data-id]").dataset.id;
  const action=btn.dataset.action;
  try{
    if(action==="delete"){ if(!confirm("Eliminare questa tratta?")) return; await api(`/searches/${id}`,{method:"DELETE"}); }
    else{ await api(`/searches/${id}/${action}`,{method:"POST"}); }
    toast(action==="check"?"Controllo completato.":"Aggiornato.");
    await render();
  }catch(err){ toast("Errore: "+err.message); }
});

$("refreshBtn").addEventListener("click",render);

$("searchForm").addEventListener("submit",async e=>{
  e.preventDefault();
  const form=e.currentTarget;
  const data=Object.fromEntries(new FormData(form).entries());
  if(!data.origin){ toast("Seleziona un aeroporto di partenza."); return; }
  if(!data.destination){ toast("Seleziona un aeroporto di arrivo."); return; }
  const chatId=getChatId();
  if(!chatId){ toast("Imposta il tuo Telegram Chat ID prima."); return; }
  data.name=`${data.origin.toUpperCase()} → ${data.destination.toUpperCase()}`;
  data.telegram_chat_id=Number(chatId);
  data.adults=Number(data.adults);
  data.flexible_days=Number(data.flexible_days);
  data.max_stops=Number(data.max_stops);
  data.max_budget_total=Number(data.max_budget_total);
  data.max_flight_price=data.max_flight_price?Number(data.max_flight_price):null;
  data.trip_id=data.trip_id?Number(data.trip_id):null;
  try{
    await api("/searches",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(data)});
    form.reset();
    form.querySelectorAll(".ac-display").forEach(el=>el.value="");
    form.querySelectorAll(".ac-clear").forEach(el=>el.style.display="none");
    toast("Tratta aggiunta.");
    await render();
  }catch(err){ toast("Errore: "+err.message); }
});

/* ── Multi-leg builder ── */
function acHtml(name,placeholder){
  return `<div class="ac-root"><input type="text" class="ac-display" placeholder="${placeholder}" autocomplete="off"><input type="hidden" name="${name}" class="ac-value"><button type="button" class="ac-clear">×</button><div class="ac-list"></div></div>`;
}

function makeLegHtml(idx){
  return `<div class="leg-group" id="leg-${idx}">
    <h4>Tratta ${idx+1}<button type="button" class="ghost" onclick="document.getElementById('leg-${idx}').remove()" style="font-size:10px;">Rimuovi</button></h4>
    <div class="grid-2">
      <label>Da ${acHtml("legs["+idx+"][origin]","Roma, FCO…")}</label>
      <label>A ${acHtml("legs["+idx+"][destination]","Londra, LHR…")}</label>
    </div>
    <div class="grid-2">
      <label>Giorno partenza<input name="legs[${idx}][departure_date]" required type="date"></label>
      <label>Scali<select name="legs[${idx}][max_stops]"><option value="0" selected>Nonstop</option><option value="1">Max 1</option><option value="-1">Qualsiasi</option></select></label>
    </div>
    <div class="grid-2">
      <label>Budget (€)<input name="legs[${idx}][max_budget_total]" required type="number" min="1" placeholder="400"></label>
      <label>Fascia oraria<span class="tip" data-tip="Formato HH-HH. Es: 07-11 preferisce voli tra le 7 e le 11. Influenza il punteggio, non filtra.">i</span><input name="legs[${idx}][preferred_departure_time_window]" type="text" placeholder="07-11" value="07-11" maxlength="5"></label>
    </div>
    <input type="hidden" name="legs[${idx}][adults]" value="2">
    <input type="hidden" name="legs[${idx}][children]" value="0">
  </div>`;
}

function addLeg(){ $("legsContainer").insertAdjacentHTML("beforeend",makeLegHtml(legCount++)); initAllAC(); }

$("addLegBtn").addEventListener("click",addLeg);
addLeg();

$("tripForm").addEventListener("submit",async e=>{
  e.preventDefault();
  const form=e.currentTarget;
  const chatId=getChatId();
  if(!chatId){ toast("Imposta il tuo Telegram Chat ID prima."); return; }
  const fd=new FormData(form);
  const legs=[];
  let i=0;
  while(fd.has(`legs[${i}][departure_date]`)){
    const origin=fd.get(`legs[${i}][origin]`);
    const dest=fd.get(`legs[${i}][destination]`);
    if(!origin||!dest){ toast(`Seleziona aeroporti per la tratta ${i+1}.`); return; }
    legs.push({
      name:`${origin.toUpperCase()} → ${dest.toUpperCase()}`,
      origin:origin.toUpperCase(), destination:dest.toUpperCase(),
      departure_date:fd.get(`legs[${i}][departure_date]`),
      adults:Number(fd.get(`legs[${i}][adults]`))||2,
      children:Number(fd.get(`legs[${i}][children]`))||0,
      max_budget_total:Number(fd.get(`legs[${i}][max_budget_total]`)),
      max_stops:Number(fd.get(`legs[${i}][max_stops]`)),
      preferred_departure_time_window:fd.get(`legs[${i}][preferred_departure_time_window]`)||"07-11",
    });
    i++;
  }
  if(!legs.length){ toast("Aggiungi almeno una tratta."); return; }
  const tripName=`${legs[0].origin} → ${legs[legs.length-1].destination}`;
  const body={telegram_chat_id:Number(chatId),name:tripName,legs};
  try{
    const trip=await api("/trips",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});
    form.reset();
    legCount=0; $("legsContainer").innerHTML=""; addLeg();
    toast(`Viaggio "${trip.name}" creato – ${trip.legs.length} tratt${trip.legs.length===1?"a":"e"}.`);
    await render();
  }catch(err){ toast("Errore: "+err.message); }
});

/* ── Mode tabs ── */
document.querySelectorAll(".mode-tab").forEach(btn=>{
  btn.addEventListener("click",()=>{
    document.querySelectorAll(".mode-tab").forEach(t=>t.classList.remove("active"));
    document.querySelectorAll(".mode-pane").forEach(p=>p.classList.remove("visible"));
    btn.classList.add("active");
    $("pane-"+btn.dataset.tab).classList.add("visible");
    initAllAC();
  });
});

/* ── Log panel ── */
let logOpen = false;
let logSince = 0;
let logTotal = 0;

function fmtLogTime(ms) {
  return new Date(ms).toLocaleTimeString("it-IT",{hour:"2-digit",minute:"2-digit",second:"2-digit"});
}

document.getElementById("logHeader").addEventListener("click", () => {
  logOpen = !logOpen;
  document.getElementById("logBody").classList.toggle("open", logOpen);
  document.getElementById("logToggleArrow").classList.toggle("open", logOpen);
  if(logOpen) scrollLogToBottom();
});

function scrollLogToBottom() {
  const b = document.getElementById("logBody");
  b.scrollTop = b.scrollHeight;
}

async function pollLogs() {
  try {
    const entries = await api(`/logs?since=${logSince}`);
    if(!entries.length) return;
    logTotal += entries.length;
    logSince = entries[entries.length - 1].t;
    document.getElementById("logBadge").textContent = logTotal;
    const body = document.getElementById("logBody");
    const wasAtBottom = body.scrollHeight - body.scrollTop - body.clientHeight < 40;
    entries.forEach(e => {
      const row = document.createElement("div");
      row.className = "log-row";
      row.innerHTML = `<span class="log-t">${fmtLogTime(e.t)}</span><span class="log-level ${esc(e.level)}">${esc(e.level)}</span><span class="log-logger">${esc(e.logger)}</span><span class="log-msg">${esc(e.msg)}</span>`;
      body.appendChild(row);
    });
    // Keep at most 300 rows in DOM
    while(body.children.length > 300) body.removeChild(body.firstChild);
    if(logOpen && wasAtBottom) scrollLogToBottom();
  } catch { /* silently ignore */ }
}

setInterval(pollLogs, 3000);
pollLogs();

/* ── Fare Calendar ── */
document.getElementById("calToggle").addEventListener("click",()=>{
  const body=document.getElementById("calBody");
  const arrow=document.getElementById("calArrow");
  const header=document.getElementById("calToggle");
  const isOpen=body.classList.toggle("open");
  arrow.classList.toggle("open",isOpen);
  header.classList.toggle("open",isOpen);
  if(isOpen) initAllAC();
});

document.getElementById("calSearchBtn").addEventListener("click",async()=>{
  const origin=document.getElementById("calOrigin").value;
  const dest=document.getElementById("calDest").value;
  const month=document.getElementById("calMonth").value;
  if(!origin||!dest||!month){ toast("Compila tutti i campi: partenza, arrivo e mese."); return; }
  const result=document.getElementById("calResult");
  result.innerHTML='<div style="padding:24px;text-align:center;color:var(--muted);font-size:13px;">Caricamento tariffe…</div>';
  try{
    const data=await api(`/fares/calendar?origin=${origin}&destination=${dest}&month=${month}`);
    renderCalendar(data,result);
  }catch(err){ result.innerHTML=`<div style="padding:20px;color:var(--danger);">Errore: ${esc(err.message)}</div>`; }
});

function renderCalendar(data,container){
  const{origin,destination,month,days}=data;
  if(!days.length){
    container.innerHTML='<div style="padding:24px;text-align:center;color:var(--muted);">Nessuna tariffa trovata per questo mese. Prova con un altro mese o rotta.</div>';
    return;
  }
  const priceMap={};
  const prices=days.filter(d=>d.price!=null).map(d=>d.price);
  const minPrice=Math.min(...prices), maxPrice=Math.max(...prices);
  days.forEach(d=>{ if(d.price!=null) priceMap[d.date]=d; });
  const[year,mon]=month.split("-").map(Number);
  const firstDow=new Date(year,mon-1,1).getDay();
  const offset=(firstDow+6)%7; // Monday-first
  const daysInMonth=new Date(year,mon,0).getDate();
  function priceColor(price){
    if(price==null) return null;
    const pct=maxPrice===minPrice?0:(price-minPrice)/(maxPrice-minPrice);
    if(pct<0.5){
      const r=Math.round(pct*2*200);
      const g=Math.round(180-pct*30);
      return `rgb(${r},${g},60)`;
    }else{
      const g=Math.round((1-(pct-0.5)*2)*160);
      return `rgb(220,${g},40)`;
    }
  }
  function textColor(price){
    if(price==null) return "var(--ink)";
    const pct=maxPrice===minPrice?0:(price-minPrice)/(maxPrice-minPrice);
    return pct>0.65?"#fff":"#0f172a";
  }
  const weekDays=["Lun","Mar","Mer","Gio","Ven","Sab","Dom"];
  const monitorKey=`cal-monitor-${origin}-${destination}-${month}`;
  let html=`<div class="cal-result-header">
    <div class="cal-month-title">${esc(origin)} → ${esc(destination)} · ${month}</div>
    <button class="cal-monitor-btn" onclick="prefillSearchFromCalendar('${esc(origin)}','${esc(destination)}','${month}')">+ Monitora questa tratta</button>
  </div>
  <div class="cal-grid">`;
  html+=weekDays.map(d=>`<div class="cal-day-hdr">${d}</div>`).join("");
  for(let i=0;i<offset;i++) html+=`<div class="cal-day-cell empty"></div>`;
  for(let day=1;day<=daysInMonth;day++){
    const dateStr=`${month}-${String(day).padStart(2,"0")}`;
    const info=priceMap[dateStr];
    if(info&&info.price!=null){
      const bg=priceColor(info.price);
      const tc=textColor(info.price);
      const dd=String(day).padStart(2,"0");
      const mm=String(mon).padStart(2,"0");
      const url=`https://www.aviasales.com/search/${esc(origin)}${dd}${mm}${esc(destination)}2`;
      html+=`<div class="cal-day-cell has-price" style="background:${bg};border-color:transparent;" onclick="window.open('${url}','_blank')" title="${dateStr} — clicca per cercare su Aviasales">
        <span class="cal-day-num" style="color:${tc};opacity:.75;">${day}</span>
        <span class="cal-day-price" style="color:${tc};">€${info.price}</span>
        ${info.airline?`<span class="cal-day-airline" style="color:${tc};">${esc(info.airline)}</span>`:""}
      </div>`;
    }else{
      html+=`<div class="cal-day-cell"><span class="cal-day-num">${day}</span></div>`;
    }
  }
  html+=`</div><div class="cal-legend"><span>Economico</span><div class="cal-legend-bar"></div><span>Caro</span></div>`;
  container.innerHTML=html;
}

function prefillSearchFromCalendar(origin, destination, month){
  // Switch to single-search tab
  document.querySelectorAll(".mode-tab").forEach(t=>t.classList.remove("active"));
  document.querySelectorAll(".mode-pane").forEach(p=>p.classList.remove("visible"));
  document.querySelector(".mode-tab[data-tab='single']").classList.add("active");
  $("pane-single").classList.add("visible");

  // Set dates: first and last day of the month
  const[year,mon]=month.split("-").map(Number);
  const firstDay=`${month}-01`;
  const lastDay=`${month}-${String(new Date(year,mon,0).getDate()).padStart(2,"0")}`;
  $("searchForm").querySelector("input[name='date_from']").value=firstDay;
  $("searchForm").querySelector("input[name='date_to']").value=lastDay;

  // Set airport autocomplete fields
  function setAC(formName, iata){
    const input=$("searchForm").querySelector(`input[name='${formName}']`);
    if(!input) return;
    const root=input.closest(".ac-root");
    const display=root.querySelector(".ac-display");
    const clearBtn=root.querySelector(".ac-clear");
    const airport=AIRPORTS.find(a=>a[0]===iata);
    input.value=iata;
    display.value=airport?`${iata} – ${airport[1]} ${airport[2]}`:iata;
    if(clearBtn) clearBtn.style.display="block";
  }
  setAC("origin", origin);
  setAC("destination", destination);

  // Scroll to form and focus budget
  $("pane-single").scrollIntoView({behavior:"smooth",block:"start"});
  setTimeout(()=>{ $("searchForm").querySelector("input[name='max_budget_total']").focus(); }, 400);
  toast(`Rotta ${origin} → ${destination} pre-compilata. Imposta il budget e premi Aggiungi.`);
}

/* ── Guide toggle ── */
document.getElementById("guideToggle").addEventListener("click",()=>{
  const body=document.getElementById("guideBody");
  const toggle=document.getElementById("guideToggle");
  const open=body.classList.toggle("open");
  toggle.classList.toggle("open",open);
});

/* ── Init ── */
(()=>{
  const now=new Date();
  const m=`${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,"0")}`;
  document.getElementById("calMonth").value=m;
})();
updateChip();
if(!getChatId()){
  document.getElementById("setupOverlay").classList.remove("hidden");
} else {
  document.getElementById("setupOverlay").classList.add("hidden");
  render();
}
initAllAC();
</script>
</body>
</html>
"""
