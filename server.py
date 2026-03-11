<!DOCTYPE html>

<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="CC Screener">
<title>Covered Call Screener</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=DM+Sans:wght@300;400;600&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #09090f;
    --surface: #111118;
    --surface2: #16161f;
    --border: #22222e;
    --accent: #7c6af7;
    --green: #22d98a;
    --yellow: #f5c842;
    --red: #f25f5c;
    --text: #e2e2ee;
    --dim: #6b6b80;
    --mono: 'DM Mono', monospace;
    --sans: 'DM Sans', sans-serif;
  }

- { box-sizing: border-box; margin: 0; padding: 0; }

body {
background: var(–bg);
color: var(–text);
font-family: var(–sans);
min-height: 100vh;
}

body::before {
content: ‘’;
position: fixed;
inset: 0;
background:
radial-gradient(ellipse 80% 50% at 20% -10%, rgba(124,106,247,0.08) 0%, transparent 60%),
radial-gradient(ellipse 60% 40% at 80% 110%, rgba(34,217,138,0.05) 0%, transparent 60%);
pointer-events: none;
z-index: 0;
}

.container {
position: relative;
z-index: 1;
max-width: 900px;
margin: 0 auto;
padding: 28px 20px;
}

header {
display: flex;
align-items: center;
justify-content: space-between;
margin-bottom: 28px;
flex-wrap: wrap;
gap: 12px;
}

.header-left h1 {
font-family: var(–mono);
font-size: 1.2rem;
color: var(–text);
letter-spacing: 0.05em;
}

.header-left p {
font-size: 0.78rem;
color: var(–dim);
margin-top: 3px;
}

.live-status {
display: flex;
align-items: center;
gap: 7px;
background: var(–surface);
border: 1px solid var(–border);
border-radius: 20px;
padding: 5px 14px 5px 10px;
}

.status-dot {
width: 8px;
height: 8px;
border-radius: 50%;
background: var(–dim);
flex-shrink: 0;
transition: background 0.4s;
}

.status-dot.connecting { background: var(–accent); animation: pulse 1s infinite; }
.status-dot.live { background: var(–green); animation: pulse 2s infinite; box-shadow: 0 0 8px rgba(34,217,138,0.5); }
.status-dot.offline { background: var(–red); }

.status-text {
font-family: var(–mono);
font-size: 0.68rem;
color: var(–dim);
text-transform: uppercase;
letter-spacing: 0.08em;
}

.status-text.live { color: var(–green); }
.status-text.offline { color: var(–red); }

@keyframes pulse {
0%, 100% { opacity: 1; }
50% { opacity: 0.4; }
}

/* Criteria panel */
.criteria {
background: var(–surface);
border: 1px solid var(–border);
border-radius: 8px;
padding: 20px;
margin-bottom: 20px;
}

.criteria-grid {
display: grid;
grid-template-columns: 1fr 1fr;
gap: 14px;
margin-bottom: 16px;
}

.criteria-grid.three {
grid-template-columns: 1fr 1fr 1fr;
}

.field label {
display: block;
font-family: var(–mono);
font-size: 0.65rem;
color: var(–dim);
text-transform: uppercase;
letter-spacing: 0.12em;
margin-bottom: 6px;
}

input[type=“date”],
input[type=“number”],
input[type=“text”] {
width: 100%;
background: var(–bg);
border: 1px solid var(–border);
border-radius: 5px;
color: var(–text);
font-family: var(–mono);
font-size: 0.9rem;
padding: 9px 12px;
outline: none;
transition: border-color 0.2s;
color-scheme: dark;
-webkit-appearance: none;
}

input:focus { border-color: var(–accent); box-shadow: 0 0 0 2px rgba(124,106,247,0.15); }

.ticker-input-wrap {
position: relative;
}

.ticker-checkboxes {
display: flex;
flex-wrap: wrap;
gap: 8px;
margin-top: 2px;
}

.ticker-chip {
display: flex;
flex-direction: column;
align-items: center;
gap: 2px;
background: var(–bg);
border: 1px solid var(–border);
border-radius: 6px;
padding: 8px 14px;
cursor: pointer;
transition: all 0.15s;
min-width: 68px;
text-align: center;
user-select: none;
}

.ticker-chip input[type=“checkbox”] {
display: none;
}

.ticker-chip span {
font-family: var(–mono);
font-size: 0.82rem;
color: var(–dim);
transition: color 0.15s;
}

.ticker-chip small {
font-family: var(–sans);
font-size: 0.6rem;
color: var(–dim);
opacity: 0.6;
transition: color 0.15s;
}

.ticker-chip:has(input:checked) {
background: rgba(124,106,247,0.1);
border-color: var(–accent);
}

.ticker-chip:has(input:checked) span {
color: var(–accent);
}

.ticker-chip:has(input:checked) small {
color: var(–accent);
opacity: 0.7;
}

.ticker-chip:active {
transform: scale(0.96);
}

.ticker-hint {
font-family: var(–mono);
font-size: 0.65rem;
color: var(–dim);
margin-top: 5px;
}

.rank-badge {
font-family: var(–mono);
font-size: 0.7rem;
color: var(–accent);
background: rgba(124,106,247,0.12);
border: 1px solid rgba(124,106,247,0.25);
border-radius: 4px;
padding: 3px 7px;
flex-shrink: 0;
}

.ticker-meta-row {
display: flex;
align-items: center;
gap: 8px;
flex-wrap: wrap;
margin-top: 4px;
}

.iv-badge {
font-family: var(–mono);
font-size: 0.65rem;
padding: 2px 7px;
border-radius: 3px;
border: 1px solid;
text-transform: uppercase;
letter-spacing: 0.06em;
}

.iv-badge.normal   { color: var(–green); border-color: rgba(34,217,138,0.3); background: rgba(34,217,138,0.08); }
.iv-badge.elevated { color: var(–yellow); border-color: rgba(245,200,66,0.3); background: rgba(245,200,66,0.08); }
.iv-badge.high     { color: #f59e0b; border-color: rgba(245,158,11,0.3); background: rgba(245,158,11,0.08); }
.iv-badge.extreme  { color: var(–red); border-color: rgba(242,95,92,0.3); background: rgba(242,95,92,0.08); }

/* ITM badge */
.itm-badge {
font-family: var(–mono);
font-size: 0.6rem;
font-weight: 700;
letter-spacing: 0.08em;
padding: 2px 6px;
border-radius: 3px;
background: rgba(242,95,92,0.15);
color: var(–red);
border: 1px solid rgba(242,95,92,0.35);
}

/* Distance tag */
.dist-tag {
font-family: var(–mono);
font-size: 0.65rem;
padding: 2px 7px;
border-radius: 3px;
}
.dist-tag.otm { color: #6ee7b7; border: 1px solid rgba(110,231,183,0.25); background: rgba(110,231,183,0.07); }
.dist-tag.itm { color: var(–red); border: 1px solid rgba(242,95,92,0.25); background: rgba(242,95,92,0.07); }

/* Premium row */
.premium-row {
display: flex;
justify-content: space-between;
align-items: center;
padding: 6px 0;
border-bottom: 1px solid var(–border);
margin-bottom: 4px;
}
.premium-label { font-family: var(–mono); font-size: 0.7rem; color: var(–dim); text-transform: uppercase; letter-spacing: 0.06em; }
.premium-val { font-family: var(–mono); font-size: 1rem; font-weight: 700; color: var(–text); }

/* Prob of profit row */
.prob-row {
display: flex;
justify-content: space-between;
align-items: center;
padding: 4px 0 6px;
border-bottom: 1px solid var(–border);
margin-bottom: 4px;
}
.prob-label { font-family: var(–mono); font-size: 0.7rem; color: var(–dim); text-transform: uppercase; letter-spacing: 0.06em; }
.prob-val { font-family: var(–mono); font-size: 0.9rem; font-weight: 600; color: #a78bfa; }

.return-actual { font-size: 0.65rem; color: var(–dim); font-weight: 400; letter-spacing: 0; text-transform: none; }
.dte-warn { color: #f59e0b; font-size: 0.7rem; font-weight: 600; }

.net-proceeds-row {
display: flex;
justify-content: space-between;
align-items: flex-start;
padding: 6px 0;
border-bottom: 1px solid var(–border);
margin-bottom: 4px;
}
.net-proceeds-val {
font-family: var(–mono);
font-size: 0.85rem;
font-weight: 700;
color: #4ade80;
text-align: right;
display: flex;
flex-direction: column;
align-items: flex-end;
gap: 2px;
}
.net-vs-price { font-size: 0.65rem; color: var(–dim); font-weight: 400; }
.net-gain { font-size: 0.8rem; color: #4ade80; font-weight: 700; }

/* ITM filter button */
.itm-filter-btn {
font-family: var(–mono);
font-size: 0.7rem;
letter-spacing: 0.06em;
text-transform: uppercase;
padding: 4px 12px;
border-radius: 4px;
border: 1px solid var(–border);
background: var(–surface2);
color: var(–dim);
cursor: pointer;
transition: all 0.15s;
}
.itm-filter-btn:hover { border-color: var(–red); color: var(–red); }
.itm-filter-btn.active { background: rgba(242,95,92,0.12); border-color: rgba(242,95,92,0.4); color: var(–red); }

/* Net proceeds row for ITM strikes */
.net-proceeds-row {
display: flex;
justify-content: space-between;
align-items: center;
padding: 5px 0;
border-bottom: 1px solid var(–border);
margin-bottom: 4px;
}
.net-proceeds { color: var(–red) !important; font-weight: 600; }
.net-vs-price { font-size: 0.7rem; color: var(–dim); font-weight: 400; }

/* Strike card top row */
.strike-card-top {
display: flex;
align-items: center;
gap: 8px;
margin-bottom: 8px;
flex-wrap: wrap;
}
.strike-tags { display: flex; gap: 5px; align-items: center; }

/* 52-week range bar */
.range-bar-wrap {
display: flex;
align-items: center;
gap: 6px;
margin-top: 6px;
}
.range-label { font-family: var(–mono); font-size: 0.6rem; color: var(–dim); text-transform: uppercase; letter-spacing: 0.06em; }
.range-val { font-family: var(–mono); font-size: 0.65rem; color: var(–dim); white-space: nowrap; }
.range-track {
position: relative;
flex: 1;
height: 4px;
background: var(–border);
border-radius: 2px;
min-width: 80px;
}
.range-fill {
position: absolute;
left: 0; top: 0; bottom: 0;
background: linear-gradient(90deg, #6366f1, #8b5cf6);
border-radius: 2px;
}
.range-dot {
position: absolute;
top: 50%;
transform: translate(-50%, -50%);
width: 8px;
height: 8px;
border-radius: 50%;
background: #fff;
border: 2px solid #8b5cf6;
}

.earnings-tag {
font-family: var(–mono);
font-size: 0.65rem;
color: var(–dim);
padding: 2px 7px;
border-radius: 3px;
border: 1px solid var(–border);
background: var(–surface2);
text-transform: uppercase;
letter-spacing: 0.06em;
}

.earnings-tag-warn {
color: var(–red) !important;
border-color: rgba(242,95,92,0.3) !important;
background: rgba(242,95,92,0.08) !important;
}

.earnings-warning-banner {
margin: 0 18px 14px;
padding: 10px 14px;
background: rgba(242,95,92,0.08);
border: 1px solid rgba(242,95,92,0.25);
border-radius: 6px;
font-family: var(–mono);
font-size: 0.72rem;
color: var(–red);
display: flex;
align-items: center;
gap: 8px;
}

.screen-btn-wrap {
position: sticky;
bottom: 0;
left: 0;
right: 0;
padding: 20px 0 36px;
background: linear-gradient(to bottom, transparent, var(–bg) 35%);
margin: 16px -20px -20px;
padding-left: 20px;
padding-right: 20px;
z-index: 10;
}

.screen-btn {
width: 100%;
padding: 24px;
background: linear-gradient(135deg, #7c6af7 0%, #5b4de0 50%, #8b5cf6 100%);
border: none;
border-radius: 16px;
color: white;
font-family: var(–mono);
font-size: 1.05rem;
font-weight: 500;
text-transform: uppercase;
letter-spacing: 0.22em;
cursor: pointer;
transition: all 0.2s;
position: relative;
overflow: hidden;
box-shadow:
0 0 0 1px rgba(255,255,255,0.08) inset,
0 8px 40px rgba(124,106,247,0.55),
0 2px 8px rgba(0,0,0,0.5);
}

.screen-btn::before {
content: ‘’;
position: absolute;
inset: 0;
background: linear-gradient(135deg, rgba(255,255,255,0.15) 0%, transparent 55%);
pointer-events: none;
}

.screen-btn::after {
content: ‘’;
position: absolute;
bottom: 0; left: 0; right: 0;
height: 1px;
background: rgba(255,255,255,0.1);
}

.screen-btn:hover {
transform: translateY(-2px);
box-shadow:
0 0 0 1px rgba(255,255,255,0.1) inset,
0 16px 48px rgba(124,106,247,0.65),
0 4px 16px rgba(0,0,0,0.5);
}

.screen-btn:active {
transform: translateY(1px);
box-shadow:
0 0 0 1px rgba(255,255,255,0.06) inset,
0 4px 20px rgba(124,106,247,0.4);
}

.screen-btn:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }

.screen-btn .spinner {
display: none;
width: 16px;
height: 16px;
border: 2px solid rgba(255,255,255,0.3);
border-top-color: white;
border-radius: 50%;
animation: spin 0.7s linear infinite;
margin-right: 10px;
vertical-align: middle;
}

@keyframes spin { to { transform: rotate(360deg); } }

.screen-btn.loading .spinner { display: inline-block; }

/* Results */
.results-header {
font-family: var(–mono);
font-size: 0.68rem;
color: var(–dim);
text-transform: uppercase;
letter-spacing: 0.12em;
margin-bottom: 12px;
display: flex;
align-items: center;
gap: 10px;
}

.results-count {
background: var(–accent);
color: white;
font-size: 0.6rem;
padding: 2px 7px;
border-radius: 10px;
}

.ticker-block {
background: var(–surface);
border: 1px solid var(–border);
border-radius: 8px;
margin-bottom: 14px;
overflow: hidden;
animation: fadeIn 0.3s ease;
}

@keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: none; } }

.ticker-header {
display: flex;
align-items: center;
justify-content: space-between;
padding: 14px 18px;
background: var(–surface2);
border-bottom: 1px solid var(–border);
flex-wrap: wrap;
gap: 8px;
}

.ticker-symbol {
font-family: var(–mono);
font-size: 1.1rem;
color: var(–accent);
font-weight: 500;
}

.ticker-name {
font-size: 0.78rem;
color: var(–dim);
margin-left: 8px;
}

.ticker-price {
font-family: var(–mono);
font-size: 0.9rem;
color: var(–text);
}

.ticker-exp {
font-family: var(–mono);
font-size: 0.72rem;
color: var(–dim);
}

.ticker-error {
padding: 14px 18px;
font-family: var(–mono);
font-size: 0.78rem;
color: var(–red);
}

/* Strike cards */
.strikes-grid {
display: grid;
grid-template-columns: repeat(3, 1fr);
gap: 0;
}

.strike-card {
padding: 16px 18px;
border-right: 1px solid var(–border);
position: relative;
}

.strike-card:last-child { border-right: none; }

.strike-card.best {
background: rgba(124,106,247,0.04);
}

.best-badge {
position: absolute;
top: 10px;
right: 10px;
font-family: var(–mono);
font-size: 0.55rem;
color: var(–accent);
background: rgba(124,106,247,0.15);
border: 1px solid rgba(124,106,247,0.3);
padding: 2px 6px;
border-radius: 3px;
text-transform: uppercase;
letter-spacing: 0.1em;
}

.strike-price {
font-family: var(–mono);
font-size: 1.3rem;
color: var(–text);
margin-bottom: 10px;
}

.return-row {
display: flex;
flex-direction: column;
gap: 6px;
margin-bottom: 12px;
padding-bottom: 12px;
border-bottom: 1px solid var(–border);
}

.return-item {
display: flex;
justify-content: space-between;
align-items: baseline;
}

.return-label {
font-family: var(–mono);
font-size: 0.6rem;
color: var(–dim);
text-transform: uppercase;
letter-spacing: 0.08em;
}

.return-val {
font-family: var(–mono);
font-size: 1rem;
color: var(–green);
font-weight: 500;
}

.return-val.called { color: var(–yellow); }

.detail-grid {
display: grid;
grid-template-columns: 1fr 1fr;
gap: 6px 12px;
}

.detail-item {
display: flex;
flex-direction: column;
gap: 2px;
}

.detail-label {
font-family: var(–mono);
font-size: 0.58rem;
color: var(–dim);
text-transform: uppercase;
letter-spacing: 0.08em;
}

.detail-val {
font-family: var(–mono);
font-size: 0.8rem;
color: var(–text);
}
.detail-val.itm-net { color: var(–red); }

.no-results {
text-align: center;
padding: 48px 20px;
font-family: var(–mono);
font-size: 0.8rem;
color: var(–dim);
}

.no-results span {
display: block;
font-size: 2rem;
margin-bottom: 12px;
}

.error-banner {
background: rgba(242,95,92,0.08);
border: 1px solid rgba(242,95,92,0.2);
border-radius: 6px;
padding: 12px 16px;
font-family: var(–mono);
font-size: 0.78rem;
color: var(–red);
margin-bottom: 16px;
}

@media (max-width: 600px) {
.criteria-grid { grid-template-columns: 1fr; }
.criteria-grid.three { grid-template-columns: 1fr 1fr; }
.strikes-grid { grid-template-columns: 1fr; }
.strike-card { border-right: none; border-bottom: 1px solid var(–border); }
.strike-card:last-child { border-bottom: none; }
}
</style>

</head>
<body>
<div class="container">

  <header>
    <div class="header-left">
      <h1>Covered Call Screener</h1>
      <p>Top 3 strikes per ticker · ranked by annualized return</p>
    </div>
    <div class="live-status">
      <span class="status-dot" id="status-dot"></span>
      <span class="status-text" id="status-text">Connecting...</span>
    </div>
  </header>

  <!-- Criteria -->

  <div class="criteria">
    <div class="criteria-grid">
      <div class="field">
        <label>Expiration Date</label>
        <input type="date" id="expDate" />
      </div>
      <div class="field">
        <label>Min Annualized Return (%)</label>
        <input type="number" id="minAnn" value="15" min="0" step="1" />
      </div>
    </div>
    <div class="criteria-grid" style="margin-bottom:16px;">
      <div class="field">
        <label>Min If-Called-Away Return (%)</label>
        <input type="number" id="minCalled" value="50" min="0" step="1" />
      </div>
      <div class="field" style="opacity:0.4;pointer-events:none;">
        <label>Strategy</label>
        <input type="text" value="Covered Call" readonly />
      </div>
    </div>
    <div class="field" style="margin-bottom:16px;">
      <label>Watchlist</label>
      <div class="ticker-checkboxes" id="ticker-checkboxes">
        <label class="ticker-chip"><input type="checkbox" value="NVDA" /><span>NVDA</span><small>NVIDIA</small></label>
        <label class="ticker-chip"><input type="checkbox" value="META" /><span>META</span><small>Meta</small></label>
        <label class="ticker-chip"><input type="checkbox" value="MSFT" /><span>MSFT</span><small>Microsoft</small></label>
        <label class="ticker-chip"><input type="checkbox" value="AAPL" /><span>AAPL</span><small>Apple</small></label>
        <label class="ticker-chip"><input type="checkbox" value="GOOGL" /><span>GOOGL</span><small>Google A</small></label>
        <label class="ticker-chip"><input type="checkbox" value="PLTR" /><span>PLTR</span><small>Palantir</small></label>
        <label class="ticker-chip"><input type="checkbox" value="ORCL" /><span>ORCL</span><small>Oracle</small></label>
      </div>
    </div>
    <div class="field" style="margin-bottom:16px;">
      <label>Additional Tickers (optional — comma separated)</label>
      <input type="text" id="tickers" placeholder="e.g. TSLA, AMD" />
      <div class="ticker-hint">Add any tickers here on top of your watchlist selections above</div>
    </div>
    <div class="screen-btn-wrap">
      <button class="screen-btn" id="screenBtn" onclick="runScreen()">
        <span class="spinner"></span>
        Run Screen
      </button>
    </div>
  </div>

  <!-- Results -->

  <div id="results-area"></div>

</div>

<script>
  const API = 'https://options-backend-v2-r27b.onrender.com';

  // Set default expiration to next Friday
  function setDefaultDate() {
    const d = new Date();
    d.setDate(d.getDate() + 1);
    while (d.getDay() !== 5) d.setDate(d.getDate() + 1);
    const yyyy = d.getFullYear();
    const mm = String(d.getMonth() + 1).padStart(2, '0');
    const dd = String(d.getDate()).padStart(2, '0');
    document.getElementById('expDate').value = `${yyyy}-${mm}-${dd}`;
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    document.getElementById('expDate').min = `${tomorrow.getFullYear()}-${String(tomorrow.getMonth()+1).padStart(2,'0')}-${String(tomorrow.getDate()).padStart(2,'0')}`;
  }

  function setStatus(state, text) {
    const dot = document.getElementById('status-dot');
    const txt = document.getElementById('status-text');
    dot.className = 'status-dot ' + state;
    txt.className = 'status-text ' + state;
    txt.textContent = text;
  }

  async function initServer() {
    setStatus('connecting', 'Connecting...');
    try {
      const res = await fetch(`${API}/health`, { signal: AbortSignal.timeout(35000) });
      if (res.ok) {
        setStatus('live', 'Live');
      } else {
        setStatus('offline', 'Offline');
      }
    } catch {
      setStatus('offline', 'Offline');
    }
  }

  async function runScreen() {
    const expDate = document.getElementById('expDate').value;
    const minAnn = parseFloat(document.getElementById('minAnn').value) || 0;
    const minCalled = parseFloat(document.getElementById('minCalled').value) || 0;
    if (!expDate) {
      showError('Please select an expiration date.');
      return;
    }

    // Collect checked watchlist tickers
    const checked = [...document.querySelectorAll('.ticker-chip input:checked')].map(el => el.value);

    // Collect any extras from text input
    const extrasRaw = document.getElementById('tickers').value;
    const extras = extrasRaw ? extrasRaw.split(',').map(t => t.trim().toUpperCase()).filter(Boolean) : [];

    // Combine, deduplicate
    const tickers = [...new Set([...checked, ...extras])];

    if (tickers.length === 0) {
      showError('Please select at least one ticker from your watchlist or enter one in the additional field.');
      return;
    }

    const btn = document.getElementById('screenBtn');
    btn.disabled = true;
    btn.classList.add('loading');
    btn.querySelector('.spinner').style.display = 'inline-block';

    document.getElementById('results-area').innerHTML = '';
    setStatus('connecting', 'Scanning...');

    try {
      const res = await fetch(`${API}/screen`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tickers,
          expiration: expDate,
          min_ann_return: minAnn,
          min_called_return: minCalled
        }),
        signal: AbortSignal.timeout(60000)
      });

      if (!res.ok) throw new Error('Server error');
      const data = await res.json();

      if (data.error) {
        showError(data.error);
        return;
      }

      setStatus('live', 'Live');
      renderResults(data.results, minAnn, minCalled);

    } catch (err) {
      showError('Could not reach server. Make sure Render is running and try again.');
      setStatus('offline', 'Offline');
    } finally {
      btn.disabled = false;
      btn.classList.remove('loading');
    }
  }

  let hideITM = false;
  let lastResults = null;
  let lastMinAnn = 0;
  let lastMinCalled = 0;

  function toggleITM() {
    hideITM = !hideITM;
    const btn = document.getElementById('itmFilterBtn');
    if (hideITM) {
      btn.classList.add('active');
      btn.textContent = 'Hiding ITM';
    } else {
      btn.classList.remove('active');
      btn.textContent = 'Hide ITM';
    }
    if (lastResults) renderResults(lastResults, lastMinAnn, lastMinCalled);
  }

  function renderResults(results, minAnn, minCalled) {
    lastResults = results;
    lastMinAnn = minAnn;
    lastMinCalled = minCalled;
    const area = document.getElementById('results-area');

    // Apply ITM filter to strikes if enabled
    const filtered = results.map(r => {
      if (!r.strikes) return r;
      const strikes = hideITM ? r.strikes.filter(s => !s.in_the_money) : r.strikes;
      return { ...r, strikes };
    });

    const withResults = filtered.filter(r => r.strikes && r.strikes.length > 0);
    const withErrors = filtered.filter(r => r.error && !r.strikes);
    const withNoMatch = filtered.filter(r => r.strikes && r.strikes.length === 0);

    // Sort matched tickers by their best strike's annualized return, descending
    withResults.sort((a, b) => b.strikes[0].ann_return - a.strikes[0].ann_return);

    const itmBtn = `<button id="itmFilterBtn" class="itm-filter-btn${hideITM ? ' active' : ''}" onclick="toggleITM()">${hideITM ? 'Hiding ITM' : 'Hide ITM'}</button>`;

    let html = `<div class="results-header">
      Results
      <span class="results-count">${withResults.length} of ${results.length} tickers matched</span>
      ${itmBtn}
    </div>`;

    if (withResults.length === 0) {
      html += `<div class="no-results">
        <span>🔍</span>
        No tickers matched your criteria.<br>Try lowering the minimum return thresholds or choosing a different expiration date.
      </div>`;
      area.innerHTML = html;
      return;
    }

    // Render matched tickers ranked by return
    withResults.forEach((r, idx) => {
      html += renderTickerBlock(r, idx + 1);
    });

    // Then show tickers with no matching strikes
    if (withNoMatch.length > 0) {
      html += `<div class="results-header" style="margin-top:20px;">No Strikes Met Criteria</div>`;
      for (const r of withNoMatch) {
        html += `<div class="ticker-block">
          <div class="ticker-header">
            <div><span class="ticker-symbol">${r.ticker}</span><span class="ticker-name">${r.name || ''}</span></div>
            <span class="ticker-price">$${r.price}</span>
          </div>
          <div class="ticker-error">No strikes found with ≥${minAnn}% annualized / ≥${minCalled}% if-called-away for ${r.expiration}</div>
        </div>`;
      }
    }

    // Errors last
    if (withErrors.length > 0) {
      html += `<div class="results-header" style="margin-top:20px;">Errors</div>`;
      for (const r of withErrors) {
        html += `<div class="ticker-block">
          <div class="ticker-header"><span class="ticker-symbol">${r.ticker}</span></div>
          <div class="ticker-error">✗ ${r.error}</div>
        </div>`;
      }
    }

    area.innerHTML = html;
  }

  function renderTickerBlock(r, rank) {
    const rankHtml = rank ? `<span class="rank-badge">#${rank}</span>` : '';

    // IV badge
    let ivBadge = '';
    if (r.iv_rank_label) {
      const cls = r.iv_rank_label.toLowerCase();
      ivBadge = `<span class="iv-badge ${cls}">IV ${r.iv_rank_label}${r.iv_rank_pct ? ' ' + r.iv_rank_pct + '%' : ''}</span>`;
    }

    // Earnings tags
    const lastEarningsTag = r.last_earnings_date
      ? `<span class="earnings-tag">Last Earnings ${r.last_earnings_date}</span>`
      : `<span class="earnings-tag">Last Earnings Unknown</span>`;
    let nextEarningsTag = '';
    if (r.earnings_date) {
      const tagClass = r.earnings_warning ? 'earnings-tag earnings-tag-warn' : 'earnings-tag';
      nextEarningsTag = `<span class="${tagClass}">Next Earnings ${r.earnings_date}</span>`;
    } else {
      nextEarningsTag = `<span class="earnings-tag">Next Earnings Unknown</span>`;
    }

    // Earnings warning banner
    const earningsBanner = r.earnings_warning
      ? `<div class="earnings-warning-banner">Earnings on ${r.earnings_date} fall before expiration — premiums are elevated but the trade carries event risk</div>`
      : '';

    // 52-week range bar
    let rangeBar = '';
    if (r.week_52_high && r.week_52_low && r.price) {
      const pct = Math.max(0, Math.min(100, (r.price - r.week_52_low) / (r.week_52_high - r.week_52_low) * 100));
      rangeBar = `
        <div class="range-bar-wrap">
          <span class="range-label">52W</span>
          <span class="range-val">$${r.week_52_low.toFixed(0)}</span>
          <div class="range-track">
            <div class="range-fill" style="width:${pct.toFixed(1)}%"></div>
            <div class="range-dot" style="left:${pct.toFixed(1)}%"></div>
          </div>
          <span class="range-val">$${r.week_52_high.toFixed(0)}</span>
        </div>`;
    }

    const currentPrice = r.price;
    const strikesHtml = r.strikes.map((s, i) => {
      const itmBadge = s.in_the_money ? '<span class="itm-badge">ITM</span>' : '';
      const distLabel = s.distance_pct >= 0
        ? `<span class="dist-tag otm">+${s.distance_pct.toFixed(1)}% OTM</span>`
        : `<span class="dist-tag itm">${s.distance_pct.toFixed(1)}% ITM</span>`;
      const probHtml = s.prob_profit != null
        ? `<div class="prob-row"><span class="prob-label">Prob. Profit</span><span class="prob-val">${s.prob_profit.toFixed(0)}%</span></div>`
        : '';
      return `
      <div class="strike-card ${i === 0 ? 'best' : ''}">
        <div class="strike-card-top">
          ${i === 0 ? '<span class="best-badge">Best</span>' : ''}
          ${itmBadge}
          <div class="strike-price">$${s.strike.toFixed(2)}</div>
          <div class="strike-tags">${distLabel}</div>
        </div>
        <div class="return-row">
          <div class="return-item">
            <span class="return-label">Ann. Return <span class="return-actual">(${s.trade_return.toFixed(2)}% actual)</span></span>
            <span class="return-val">${s.ann_return.toFixed(1)}%</span>
          </div>
          <div class="return-item">
            <span class="return-label">If Called Away <span class="return-actual">(${s.called_trade_return.toFixed(2)}% actual)</span></span>
            <span class="return-val called">${s.called_ann_return.toFixed(1)}%</span>
          </div>
        </div>
        <div class="premium-row">
          <span class="premium-label">Premium (Bid)</span>
          <span class="premium-val">$${s.premium.toFixed(2)}</span>
        </div>
        ${s.in_the_money ? `
        <div class="net-proceeds-row">
          <span class="detail-label">Net if Called Away</span>
          <span class="net-proceeds-val">
            $${(s.strike + s.premium).toFixed(2)}/sh
            <span class="net-vs-price">vs $${r.price.toFixed(2)} current</span>
            <span class="net-gain">+$${((s.strike + s.premium) - r.price).toFixed(2)}/sh</span>
          </span>
        </div>` : ''}
        ${probHtml}
        <div class="detail-grid">
          <div class="detail-item">
            <span class="detail-label">Break-Even</span>
            <span class="detail-val">$${s.breakeven.toFixed(2)}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Trade Return</span>
            <span class="detail-val">+${s.trade_return.toFixed(2)}%</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Volume</span>
            <span class="detail-val">${s.volume.toLocaleString()}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Open Int.</span>
            <span class="detail-val">${s.open_interest.toLocaleString()}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">IV</span>
            <span class="detail-val">${s.iv ? s.iv + '%' : '—'}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Capital</span>
            <span class="detail-val">$${s.capital.toLocaleString(undefined,{maximumFractionDigits:0})}</span>
          </div>
        </div>
      </div>`;
    }).join('');

    return `<div class="ticker-block">
      <div class="ticker-header">
        <div style="display:flex;align-items:center;gap:10px;">
          ${rankHtml}
          <div>
            <div><span class="ticker-symbol">${r.ticker}</span><span class="ticker-name">${r.name || ''}</span></div>
            <div class="ticker-meta-row">${ivBadge}${lastEarningsTag}${nextEarningsTag}</div>
          </div>
        </div>
        <div style="text-align:right;">
          <div style="display:flex;gap:16px;align-items:center;justify-content:flex-end;">
            <span class="ticker-price">$${r.price.toFixed(2)}</span>
            <span class="ticker-exp">Exp ${r.expiration} · ${r.dte}d${r.dte <= 7 ? ' <span class="dte-warn">! Short expiry</span>' : ''}</span>
          </div>
          ${rangeBar}
        </div>
      </div>
      ${earningsBanner}
      <div class="strikes-grid">${strikesHtml}</div>
    </div>`;
  }

  function showError(msg) {
    document.getElementById('results-area').innerHTML =
      `<div class="error-banner">✗ ${msg}</div>`;
  }

  setDefaultDate();
  initServer();
</script>

</body>
</html>
