from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .cache import Cache
from .config import AppConfig
from .models import ReviewState


HTML = r"""<!doctype html>
<html>
<head>
  <meta charset='utf-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1, viewport-fit=cover'>
  <title>App Crawler Dashboard</title>
  <style>
    :root {
      --bg: #08111f;
      --bg-2: #0b1527;
      --panel: rgba(14, 25, 44, 0.92);
      --panel-2: rgba(19, 33, 58, 0.98);
      --panel-3: rgba(11, 20, 36, 0.98);
      --border: rgba(130, 154, 198, 0.18);
      --text: #edf4ff;
      --muted: #97a6c6;
      --accent: #6fb1ff;
      --accent-2: #8c7cff;
      --good: #4ad39a;
      --warn: #ffb44c;
      --bad: #ff6f91;
      --chip: rgba(111, 177, 255, 0.12);
      --shadow: 0 20px 60px rgba(0, 0, 0, 0.32);
      --radius: 18px;
    }
    * { box-sizing: border-box; }
    html, body { margin: 0; min-height: 100%; background: radial-gradient(circle at top, rgba(88, 140, 255, 0.18), transparent 28%), linear-gradient(180deg, var(--bg), var(--bg-2)); color: var(--text); font-family: Inter, system-ui, sans-serif; }
    a { color: var(--accent); text-decoration: none; }
    body { min-height: 100vh; }
    .shell { max-width: 1600px; margin: 0 auto; padding: 18px; }
    .hero { display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; margin-bottom: 16px; }
    .hero h1 { margin: 0 0 8px; font-size: 30px; }
    .hero p { margin: 0; color: var(--muted); max-width: 820px; }
    .topbar { display: flex; flex-wrap: wrap; gap: 10px; padding: 14px; margin-bottom: 16px; border: 1px solid var(--border); border-radius: var(--radius); background: var(--panel); backdrop-filter: blur(14px); box-shadow: var(--shadow); }
    .topbar input, .topbar select, .topbar button, textarea, input, select { font: inherit; color: var(--text); background: var(--panel-2); border: 1px solid var(--border); border-radius: 12px; padding: 12px 14px; }
    .topbar input { flex: 1 1 240px; }
    .topbar select { min-width: 150px; }
    button { min-height: 46px; cursor: pointer; }
    .cards { display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 12px; margin-bottom: 16px; }
    .card { border: 1px solid var(--border); border-radius: var(--radius); background: var(--panel); box-shadow: var(--shadow); padding: 16px; }
    .card .label { color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em; }
    .card .value { font-size: 28px; font-weight: 800; margin-top: 8px; }
    .layout { display: grid; grid-template-columns: minmax(320px, 30%) minmax(0, 1fr) minmax(320px, 28%); gap: 16px; }
    .panel { border: 1px solid var(--border); border-radius: var(--radius); background: var(--panel); box-shadow: var(--shadow); min-height: 200px; overflow: hidden; }
    .panel-head { padding: 14px 16px; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; gap: 10px; background: rgba(255,255,255,0.02); }
    .panel-head h2, .panel-head h3 { margin: 0; font-size: 15px; }
    .list { max-height: calc(100vh - 320px); overflow: auto; padding: 10px; }
    .item { padding: 14px; border: 1px solid var(--border); border-radius: 14px; background: rgba(255,255,255,0.02); margin-bottom: 10px; cursor: pointer; transition: transform 0.15s ease, border-color 0.15s ease, background 0.15s ease; }
    .item:hover { transform: translateY(-1px); border-color: var(--accent); }
    .item.selected { border-color: var(--accent); background: linear-gradient(180deg, rgba(111,177,255,0.16), rgba(255,255,255,0.02)); }
    .item-title { font-weight: 700; font-size: 15px; margin-bottom: 6px; }
    .muted { color: var(--muted); font-size: 12px; line-height: 1.5; }
    .detail, .sidebar { padding: 16px; overflow: auto; max-height: calc(100vh - 320px); }
    .empty { border: 1px dashed var(--border); border-radius: 16px; padding: 18px; color: var(--muted); background: var(--panel-3); }
    .headline { margin: 0 0 8px; font-size: 26px; }
    .chip-row { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 14px; }
    .chip { display: inline-flex; align-items: center; gap: 6px; padding: 7px 11px; border-radius: 999px; border: 1px solid var(--border); background: var(--chip); color: var(--muted); font-size: 12px; }
    .grid-2 { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
    .section { padding: 14px; border: 1px solid var(--border); border-radius: 16px; background: var(--panel-3); margin-bottom: 14px; }
    .section h3 { margin: 0 0 10px; font-size: 14px; }
    .button-row { display: flex; flex-wrap: wrap; gap: 10px; }
    .button-row button { flex: 1 1 140px; }
    .primary { background: linear-gradient(135deg, rgba(111,177,255,0.22), rgba(140,124,255,0.18)); }
    .good { border-color: rgba(74,211,154,0.35); }
    .warn { border-color: rgba(255,180,76,0.35); }
    .bad { border-color: rgba(255,111,145,0.35); }
    textarea { width: 100%; min-height: 150px; resize: vertical; }
    .stack { display: grid; gap: 10px; }
    pre { white-space: pre-wrap; word-break: break-word; margin: 0; border: 1px solid var(--border); border-radius: 14px; background: #08111f; padding: 14px; overflow: auto; }
    iframe { width: 100%; min-height: 420px; border: 1px solid var(--border); border-radius: 14px; background: white; }
    .table-wrap { overflow: auto; }
    table { width: 100%; border-collapse: collapse; }
    th, td { text-align: left; padding: 10px; border-bottom: 1px solid var(--border); font-size: 13px; vertical-align: top; }
    th { color: var(--muted); font-weight: 600; }
    .toggle-row { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 10px; }
    .toggle-row button.active { border-color: var(--accent); background: rgba(111,177,255,0.14); }
    .sidebar .section:last-child { margin-bottom: 0; }
    @media (max-width: 1280px) {
      .cards { grid-template-columns: repeat(3, minmax(0, 1fr)); }
      .layout { grid-template-columns: minmax(280px, 34%) minmax(0, 1fr); }
      .sidebar-panel { grid-column: 1 / -1; }
      .sidebar { max-height: none; }
    }
    @media (max-width: 920px) {
      .cards { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .layout { grid-template-columns: 1fr; }
      .list, .detail, .sidebar { max-height: none; }
      .grid-2 { grid-template-columns: 1fr; }
    }
    @media (max-width: 640px) {
      .shell { padding: 12px; }
      .cards { grid-template-columns: 1fr; }
      .topbar input, .topbar select, .topbar button, .button-row button { width: 100%; }
      .hero { flex-direction: column; }
      .headline { font-size: 22px; }
    }
  </style>
</head>
<body>
<div class='shell'>
  <div class='hero'>
    <div>
      <h1>Shizuku Crawler Dashboard</h1>
      <p>Review findings, inspect evidence strength, preview source pages, translate non-English descriptions, and manage statuses without bouncing between multiple tools.</p>
    </div>
    <div class='chip'>In-app review workspace</div>
  </div>

  <div class='topbar'>
    <input id='search' placeholder='Search app, scanner, evidence, or description'>
    <select id='statusFilter'>
      <option value=''>All status</option>
      <option value='new'>new</option>
      <option value='confirmed'>confirmed</option>
      <option value='reviewed'>reviewed</option>
      <option value='false_positive'>false_positive</option>
      <option value='archived'>archived</option>
    </select>
    <select id='strengthFilter'>
      <option value=''>All evidence</option>
      <option value='strong'>strong</option>
      <option value='medium'>medium</option>
      <option value='weak'>weak</option>
    </select>
    <button id='reload' class='primary'>Reload</button>
  </div>

  <div class='cards' id='cards'></div>

  <div class='layout'>
    <div class='panel'>
      <div class='panel-head'><h2>Findings</h2><span class='muted' id='resultCount'></span></div>
      <div class='list' id='list'></div>
    </div>

    <div class='panel'>
      <div class='panel-head'><h2>Workspace</h2><span class='muted'>Review, preview, and inspect in one place</span></div>
      <div class='detail' id='detail'><div class='empty'>Select a result to open the workspace.</div></div>
    </div>

    <div class='panel sidebar-panel'>
      <div class='panel-head'><h2>Scanner observability</h2><span class='muted'>Live from scan_stats.json</span></div>
      <div class='sidebar' id='sidebar'></div>
    </div>
  </div>
</div>
<script>
let allApps = [];
let stats = {};
let selected = null;
let showReadable = true;
let showPreview = true;
let showTranslationPanel = false;

async function loadData() {
  const [appsRes, statsRes] = await Promise.all([
    fetch('/api/apps'),
    fetch('/api/stats')
  ]);
  allApps = await appsRes.json();
  stats = await statsRes.json();
  renderCards();
  renderSidebar();
  renderList();
  if (selected) {
    const next = allApps.find(a => a.identity_key === selected.identity_key);
    if (next) renderDetail(next, false);
  }
}

function isMobileLayout() {
  return window.matchMedia('(max-width: 920px)').matches;
}

function htmlToText(value) {
  const raw = String(value || '');
  if (!raw) return '';
  const wrapper = document.createElement('div');
  wrapper.innerHTML = raw;
  return (wrapper.textContent || wrapper.innerText || '').replace(/\s+/g, ' ').trim();
}

function detectOriginalLanguage(text) {
  const value = String(text || '').trim();
  if (!value) return null;
  if (/[\u3040-\u30ff]/.test(value)) return { code: 'ja', label: 'Japanese' };
  if (/[\u4e00-\u9fff]/.test(value)) return { code: 'zh', label: 'Chinese' };
  if (/[\uac00-\ud7af]/.test(value)) return { code: 'ko', label: 'Korean' };
  if (/[\u0400-\u04FF]/.test(value)) return { code: 'ru', label: 'Cyrillic' };
  if (/[\u0600-\u06FF]/.test(value)) return { code: 'ar', label: 'Arabic' };
  if (/[\u0590-\u05FF]/.test(value)) return { code: 'he', label: 'Hebrew' };
  if (/[\u0900-\u097F]/.test(value)) return { code: 'hi', label: 'Devanagari' };
  return null;
}

function escapeHtml(s) {
  return String(s || '').replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;');
}
function escapeAttr(s) { return escapeHtml(s).replaceAll("'", '&#39;'); }

function getFilteredApps() {
  const q = document.getElementById('search').value.trim().toLowerCase();
  const sf = document.getElementById('statusFilter').value;
  const ef = document.getElementById('strengthFilter').value;
  return allApps.filter(app => {
    const text = [
      app.name,
      app.scanner,
      htmlToText(app.desc || ''),
      app.strongest_evidence_strength || '',
      ...(app.match_reasons || []),
      ...((app.evidence || []).map(ev => `${ev.reason} ${ev.detail || ''} ${ev.file_path || ''}`)),
    ].join(' ').toLowerCase();
    const okQ = !q || text.includes(q);
    const okS = !sf || app.status === sf;
    const okE = !ef || (app.strongest_evidence_strength || 'weak') === ef;
    return okQ && okS && okE;
  });
}

function renderCards() {
  const strength = stats.evidence_strength || {};
  const cards = [
    ['Total findings', stats.total || 0],
    ['With downloads', stats.with_downloads || 0],
    ['Strong evidence', strength.strong || 0],
    ['Medium evidence', strength.medium || 0],
    ['Weak evidence', strength.weak || 0],
    ['Ahead forks', stats.meaningfully_ahead_forks || 0],
  ];
  document.getElementById('cards').innerHTML = cards.map(([label, value]) => `
    <div class='card'>
      <div class='label'>${escapeHtml(label)}</div>
      <div class='value'>${escapeHtml(String(value))}</div>
    </div>
  `).join('');
}

function renderSidebar() {
  const scannerMetrics = stats.scanner_metrics || {};
  const rows = Object.entries(scannerMetrics).map(([name, metric]) => `
    <tr>
      <td>${escapeHtml(name)}</td>
      <td>${escapeHtml(String(metric.items_found ?? ''))}</td>
      <td>${escapeHtml(String(metric.elapsed_ms ?? ''))}</td>
      <td>${escapeHtml(String(metric.request_count ?? ''))}</td>
      <td>${escapeHtml(String(metric.retry_count ?? ''))}</td>
      <td>${escapeHtml(String(metric.rate_limit_hits ?? ''))}</td>
      <td>${escapeHtml(String(metric.failed_requests ?? ''))}</td>
      <td>${escapeHtml(String(metric.ok ?? ''))}</td>
    </tr>
  `).join('');
  document.getElementById('sidebar').innerHTML = `
    <div class='section'>
      <h3>Evidence distribution</h3>
      <div class='chip-row'>
        <div class='chip'>strong: ${escapeHtml(String((stats.evidence_strength || {}).strong || 0))}</div>
        <div class='chip'>medium: ${escapeHtml(String((stats.evidence_strength || {}).medium || 0))}</div>
        <div class='chip'>weak: ${escapeHtml(String((stats.evidence_strength || {}).weak || 0))}</div>
      </div>
    </div>
    <div class='section table-wrap'>
      <h3>Per-scanner metrics</h3>
      <table>
        <thead><tr><th>Scanner</th><th>Items</th><th>ms</th><th>Req</th><th>Retry</th><th>429</th><th>Fail</th><th>OK</th></tr></thead>
        <tbody>${rows || '<tr><td colspan="8" class="muted">No scanner metrics yet.</td></tr>'}</tbody>
      </table>
    </div>
  `;
}

function renderList() {
  const filtered = getFilteredApps();
  document.getElementById('resultCount').textContent = `${filtered.length} shown`;
  const list = document.getElementById('list');
  if (!filtered.length) {
    list.innerHTML = `<div class='empty'>No entries match the current filters.</div>`;
    return;
  }
  list.innerHTML = filtered.map(app => {
    const desc = htmlToText(app.desc || '');
    const strength = app.strongest_evidence_strength || 'weak';
    return `
      <div class='item ${selected && selected.identity_key === app.identity_key ? 'selected' : ''}' data-key='${escapeAttr(app.identity_key)}'>
        <div class='item-title'>${escapeHtml(app.name)}</div>
        <div class='chip-row'>
          <div class='chip'>${escapeHtml(app.scanner)}</div>
          <div class='chip'>status: ${escapeHtml(app.status)}</div>
          <div class='chip'>evidence: ${escapeHtml(strength)}</div>
        </div>
        <div class='muted'>${escapeHtml(desc)}</div>
      </div>
    `;
  }).join('');
  list.querySelectorAll('.item').forEach(el => el.onclick = () => {
    const app = filtered.find(a => a.identity_key === el.dataset.key);
    if (app) renderDetail(app, true);
  });
}

async function saveReview(app, statusOverride = null) {
  const payload = {
    identity_key: app.identity_key,
    status: statusOverride || document.getElementById('status').value,
    review_notes: document.getElementById('notes').value,
    reviewed_by: document.getElementById('reviewedBy').value,
  };
  const res = await fetch('/api/review', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  const out = await res.json();
  document.getElementById('saveStatus').textContent = out.message || 'Saved';
  await loadData();
}

function renderDetail(app, scrollOnMobile = true) {
  selected = app;
  renderList();
  const detail = document.getElementById('detail');
  const descriptionText = htmlToText(app.desc || '');
  const rawDescription = String(app.desc || '');
  const primaryUrl = app.urls[0] || '#';
  const releaseUrl = app.release_info?.release_url || '';
  const originalLanguage = detectOriginalLanguage(descriptionText || app.name || '');
  const translateUrl = originalLanguage ? 'https://translate.google.com/?sl=auto&tl=en&text=' + encodeURIComponent(descriptionText || app.name || '') + '&op=translate' : '';
  const previewTarget = releaseUrl || primaryUrl;
  detail.innerHTML = `
    <div class='section'>
      <h2 class='headline'>${escapeHtml(app.name)}</h2>
      <div class='chip-row'>
        <div class='chip'>scanner: ${escapeHtml(app.scanner)}</div>
        <div class='chip'>status: ${escapeHtml(app.status)}</div>
        <div class='chip'>confidence: ${escapeHtml(app.confidence)}</div>
        <div class='chip'>usefulness: ${escapeHtml(app.usefulness)}</div>
        <div class='chip'>evidence: ${escapeHtml(app.strongest_evidence_strength || 'weak')}</div>
        ${originalLanguage ? `<div class='chip'>language: ${escapeHtml(originalLanguage.label)}</div>` : ''}
      </div>
      <div class='button-row'>
        <button class='primary' id='previewToggleBtn'>${showPreview ? 'Hide' : 'Show'} preview</button>
        <button id='descriptionToggleBtn'>${showReadable ? 'Show raw description' : 'Show cleaned description'}</button>
        ${originalLanguage ? `<button id='translationToggleBtn'>${showTranslationPanel ? 'Hide' : 'Show'} translation panel</button>` : ''}
        <a class='chip' href='${escapeAttr(primaryUrl)}' target='_blank'>Open source page</a>
        ${releaseUrl ? `<a class='chip' href='${escapeAttr(releaseUrl)}' target='_blank'>Open release</a>` : ''}
      </div>
    </div>

    <div class='grid-2'>
      <div class='section'>
        <h3>Overview</h3>
        <div class='stack'>
          <div><strong>Description</strong><div class='muted'>${escapeHtml(showReadable ? (descriptionText || 'No description') : (rawDescription || 'No description'))}</div></div>
          <div><strong>Artifact quality</strong><div class='muted'>${escapeHtml(app.release_info?.quality_label || 'unknown')}</div></div>
          <div><strong>Fork lineage</strong><div class='muted'>${escapeHtml(app.fork_lineage?.parent_full_name || 'none')}</div></div>
          <div><strong>Match reasons</strong><pre>${escapeHtml(JSON.stringify(app.match_reasons || [], null, 2))}</pre></div>
        </div>
      </div>
      <div class='section'>
        <h3>Review controls</h3>
        <div class='button-row'>
          <button class='good' id='confirmBtn'>Mark confirmed</button>
          <button class='primary' id='reviewedBtn'>Mark reviewed</button>
          <button class='warn' id='falseBtn'>Mark false_positive</button>
          <button class='bad' id='archiveBtn'>Mark archived</button>
        </div>
        <div class='stack' style='margin-top:12px;'>
          <label>Status<select id='status'>${['new','confirmed','reviewed','false_positive','archived'].map(s => `<option value="${s}" ${app.status===s?'selected':''}>${s}</option>`).join('')}</select></label>
          <label>Review notes<textarea id='notes'>${escapeHtml(app.review_notes || '')}</textarea></label>
          <label>Reviewed by<input id='reviewedBy' value='${escapeAttr(app.reviewed_by || '')}'></label>
          <button class='primary' id='saveBtn'>Save review</button>
          <div class='muted' id='saveStatus'></div>
        </div>
      </div>
    </div>

    ${showPreview ? `
    <div class='section'>
      <h3>In-app preview</h3>
      <div class='muted' style='margin-bottom:10px;'>The dashboard tries to preview the source or release page here. Some sites block embedding; if that happens, use the open buttons above.</div>
      <iframe src='${escapeAttr(previewTarget)}' loading='lazy'></iframe>
    </div>` : ''}

    ${showTranslationPanel && translateUrl ? `
    <div class='section'>
      <h3>Translation workspace</h3>
      <div class='muted' style='margin-bottom:10px;'>Embedded translation can be blocked by the remote site. If it does not render, use the open-source page and external translate links as fallback.</div>
      <iframe src='${escapeAttr(translateUrl)}' loading='lazy'></iframe>
    </div>` : ''}

    <div class='section'>
      <h3>Evidence</h3>
      <pre>${escapeHtml(JSON.stringify(app.evidence || [], null, 2))}</pre>
    </div>
  `;
  const previewToggleBtn = document.getElementById('previewToggleBtn');
  if (previewToggleBtn) previewToggleBtn.onclick = () => { showPreview = !showPreview; renderDetail(app, false); };
  const descriptionToggleBtn = document.getElementById('descriptionToggleBtn');
  if (descriptionToggleBtn) descriptionToggleBtn.onclick = () => { showReadable = !showReadable; renderDetail(app, false); };
  const translationToggleBtn = document.getElementById('translationToggleBtn');
  if (translationToggleBtn) translationToggleBtn.onclick = () => { showTranslationPanel = !showTranslationPanel; renderDetail(app, false); };
  document.getElementById('saveBtn').onclick = async () => saveReview(app);
  document.getElementById('confirmBtn').onclick = async () => saveReview(app, 'confirmed');
  document.getElementById('reviewedBtn').onclick = async () => saveReview(app, 'reviewed');
  document.getElementById('falseBtn').onclick = async () => saveReview(app, 'false_positive');
  document.getElementById('archiveBtn').onclick = async () => saveReview(app, 'archived');
  if (scrollOnMobile && isMobileLayout()) {
    detail.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
}

function bindFilters() {
  document.getElementById('search').addEventListener('input', renderList);
  document.getElementById('statusFilter').addEventListener('change', renderList);
  document.getElementById('strengthFilter').addEventListener('change', renderList);
  document.getElementById('reload').addEventListener('click', loadData);
  window.addEventListener('resize', () => { if (selected) renderDetail(selected, false); });
}

bindFilters();
loadData();
</script>
</body>
</html>
"""


def _load_apps_for_ui(cache: Cache) -> list[dict[str, Any]]:
    apps = cache.load_all()
    review_state = cache.load_review_state()
    out: list[dict[str, Any]] = []
    for app in apps:
        app.apply_review_state(review_state.get(app.identity_key_str()))
        data = app.to_dict()
        data['identity_key'] = app.identity_key_str()
        out.append(data)
    out.sort(key=lambda item: str(item.get('name', '')).casefold())
    return out


def _load_stats_for_ui(stats_path: Path) -> dict[str, Any]:
    if not stats_path.exists():
        return {}
    try:
        return json.loads(stats_path.read_text(encoding='utf-8'))
    except Exception:
        return {}


def _save_review_update(cache: Cache, identity_key: str, status: str, review_notes: str | None, reviewed_by: str | None) -> None:
    review_state = cache.load_review_state()
    current = review_state.get(identity_key, ReviewState())
    current.status = status
    current.review_notes = review_notes or None
    current.reviewed_by = reviewed_by or None
    review_state[identity_key] = current
    cache.save_review_state(review_state)


def serve_webui(config: AppConfig) -> None:
    cache = Cache(Path.cwd() / 'cache')
    stats_path = Path.cwd() / config.stats_file

    class Handler(BaseHTTPRequestHandler):
        def _json(self, payload: Any, status: int = 200) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            parsed = urlparse(self.path)
            if parsed.path == '/':
                body = HTML.encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            if parsed.path == '/api/apps':
                self._json(_load_apps_for_ui(cache))
                return
            if parsed.path == '/api/stats':
                self._json(_load_stats_for_ui(stats_path))
                return
            self._json({'message': 'Not found'}, status=404)

        def do_POST(self):
            parsed = urlparse(self.path)
            if parsed.path != '/api/review':
                self._json({'message': 'Not found'}, status=404)
                return
            length = int(self.headers.get('Content-Length', '0') or 0)
            raw = self.rfile.read(length) if length else b'{}'
            try:
                data = json.loads(raw.decode('utf-8'))
            except Exception:
                self._json({'message': 'Invalid JSON'}, status=400)
                return
            identity_key = str(data.get('identity_key', ''))
            status = str(data.get('status', 'new'))
            if not identity_key:
                self._json({'message': 'identity_key is required'}, status=400)
                return
            _save_review_update(
                cache,
                identity_key=identity_key,
                status=status,
                review_notes=data.get('review_notes'),
                reviewed_by=data.get('reviewed_by'),
            )
            self._json({'message': 'Saved'})

        def log_message(self, format: str, *args: Any) -> None:
            return

    server = ThreadingHTTPServer((config.webui_host, config.webui_port), Handler)
    print(f'Web UI running on http://{config.webui_host}:{config.webui_port}')
    try:
        server.serve_forever()
    finally:
        server.server_close()
