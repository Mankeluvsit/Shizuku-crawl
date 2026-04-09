from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .cache import Cache
from .config import AppConfig
from .models import ReviewState


HTML = """<!doctype html>
<html>
<head>
  <meta charset='utf-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1, viewport-fit=cover'>
  <title>App Crawler Review UI</title>
  <style>
    :root {
      --bg: #0f1115;
      --panel: #171a21;
      --panel-2: #1d2230;
      --border: #2a3142;
      --text: #eef2ff;
      --muted: #9aa4bf;
      --accent: #7aa2ff;
      --good: #35c48b;
      --warn: #ffb84d;
      --bad: #ff6b6b;
      --shadow: 0 10px 30px rgba(0, 0, 0, 0.28);
      --radius: 16px;
    }
    * { box-sizing: border-box; }
    html, body { margin: 0; background: var(--bg); color: var(--text); font-family: Inter, system-ui, sans-serif; }
    a { color: var(--accent); }
    body { min-height: 100vh; }
    .bar {
      padding: 12px;
      border-bottom: 1px solid var(--border);
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      position: sticky;
      top: 0;
      z-index: 20;
      background: rgba(15, 17, 21, 0.92);
      backdrop-filter: blur(12px);
    }
    .layout {
      display: grid;
      grid-template-columns: minmax(300px, 36%) minmax(0, 1fr);
      min-height: calc(100vh - 74px);
    }
    .list {
      overflow: auto;
      border-right: 1px solid var(--border);
      background: linear-gradient(180deg, rgba(23,26,33,0.96), rgba(15,17,21,0.98));
    }
    .detail {
      padding: 18px;
      overflow: auto;
      background: radial-gradient(circle at top right, rgba(122,162,255,0.08), transparent 28%), var(--bg);
    }
    .empty {
      border: 1px dashed var(--border);
      background: var(--panel);
      border-radius: var(--radius);
      padding: 18px;
      color: var(--muted);
    }
    .item {
      margin: 10px;
      padding: 14px;
      border: 1px solid var(--border);
      border-radius: 14px;
      cursor: pointer;
      background: var(--panel);
      box-shadow: var(--shadow);
      transition: transform 0.15s ease, border-color 0.15s ease, background 0.15s ease;
    }
    .item:hover { transform: translateY(-1px); border-color: var(--accent); }
    .item.selected {
      border-color: var(--accent);
      background: linear-gradient(180deg, rgba(122,162,255,0.12), rgba(23,26,33,0.96));
    }
    .item-title { font-size: 15px; font-weight: 700; line-height: 1.35; margin-bottom: 6px; }
    .muted { color: var(--muted); font-size: 12px; line-height: 1.45; }
    textarea, select, input, button {
      font: inherit;
      color: var(--text);
      background: var(--panel-2);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 12px 14px;
    }
    textarea {
      width: 100%;
      min-height: 140px;
      resize: vertical;
    }
    input, select { min-height: 46px; }
    button {
      min-height: 46px;
      cursor: pointer;
      transition: transform 0.15s ease, border-color 0.15s ease, background 0.15s ease;
    }
    button:hover { transform: translateY(-1px); border-color: var(--accent); }
    .button-row button { flex: 1 1 160px; }
    .button-confirm { border-color: rgba(53,196,139,0.5); }
    .button-reviewed { border-color: rgba(122,162,255,0.5); }
    .button-false { border-color: rgba(255,184,77,0.5); }
    .button-archive { border-color: rgba(255,107,107,0.45); }
    .button-translate { border-color: rgba(122,162,255,0.55); }
    pre {
      white-space: pre-wrap;
      word-break: break-word;
      background: #11151d;
      border: 1px solid var(--border);
      padding: 14px;
      border-radius: 14px;
      overflow: auto;
    }
    .row { margin-bottom: 14px; }
    .actions, .button-row { display: flex; gap: 10px; flex-wrap: wrap; }
    .detail-card {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 18px;
      box-shadow: var(--shadow);
    }
    .headline { margin: 0 0 8px; font-size: 24px; line-height: 1.2; }
    .subgrid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px;
      margin-bottom: 14px;
    }
    .chip {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 6px 10px;
      border-radius: 999px;
      border: 1px solid var(--border);
      background: rgba(122,162,255,0.08);
      color: var(--muted);
      font-size: 12px;
      margin-right: 8px;
      margin-bottom: 8px;
    }
    .save-status { min-height: 20px; }
    @media (max-width: 900px) {
      .layout {
        grid-template-columns: 1fr;
        min-height: auto;
      }
      .list {
        border-right: none;
        border-bottom: 1px solid var(--border);
        max-height: 42vh;
      }
      .detail {
        padding: 12px;
      }
      .subgrid {
        grid-template-columns: 1fr;
      }
      .headline {
        font-size: 22px;
      }
    }
    @media (max-width: 640px) {
      .bar {
        padding: 10px;
        gap: 8px;
      }
      .bar input, .bar select, .bar button {
        width: 100%;
      }
      .item {
        margin: 8px;
        padding: 12px;
      }
      .detail-card {
        padding: 14px;
        border-radius: 14px;
      }
      .button-row button, .actions button, #saveBtn {
        width: 100%;
      }
      textarea {
        min-height: 160px;
      }
      .detail { padding-bottom: 28px; }
    }
  </style>
</head>
<body>
  <div class='bar'>
    <input id='search' placeholder='Search name or scanner'>
    <select id='statusFilter'>
      <option value=''>All status</option>
      <option value='new'>new</option>
      <option value='confirmed'>confirmed</option>
      <option value='reviewed'>reviewed</option>
      <option value='false_positive'>false_positive</option>
      <option value='archived'>archived</option>
    </select>
    <button id='reload'>Reload</button>
  </div>
  <div class='layout'>
    <div class='list' id='list'></div>
    <div class='detail' id='detail'><div class='empty'>Select an entry to review.</div></div>
  </div>
<script>
let allApps = [];
let selected = null;

async function loadApps() {
  const res = await fetch('/api/apps');
  allApps = await res.json();
  renderList();
  if (selected) {
    const next = allApps.find(a => a.identity_key === selected.identity_key);
    if (next) renderDetail(next, false);
  }
}

function isMobileLayout() {
  return window.matchMedia('(max-width: 900px)').matches;
}

function htmlToText(value) {
  const raw = String(value || '');
  if (!raw) return '';
  const wrapper = document.createElement('div');
  wrapper.innerHTML = raw;
  const text = (wrapper.textContent || wrapper.innerText || '').replace(/\s+/g, ' ').trim();
  return text;
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

function openTranslate(text) {
  const value = String(text || '').trim();
  if (!value) return;
  const url = 'https://translate.google.com/?sl=auto&tl=en&text=' + encodeURIComponent(value) + '&op=translate';
  window.open(url, '_blank', 'noopener,noreferrer');
}

function renderList() {
  const q = document.getElementById('search').value.trim().toLowerCase();
  const sf = document.getElementById('statusFilter').value;
  const list = document.getElementById('list');
  const filtered = allApps.filter(app => {
    const descriptionText = htmlToText(app.desc || '');
    const text = `${app.name} ${app.scanner} ${descriptionText}`.toLowerCase();
    const okQ = !q || text.includes(q);
    const okS = !sf || app.status === sf;
    return okQ && okS;
  });
  if (!filtered.length) {
    list.innerHTML = `<div class="empty" style="margin:12px;">No entries match the current filter.</div>`;
    return;
  }
  list.innerHTML = filtered.map(app => {
    const descriptionText = htmlToText(app.desc || '');
    const language = detectOriginalLanguage(descriptionText || app.name || '');
    return `
      <div class="item ${selected && selected.identity_key === app.identity_key ? 'selected' : ''}" data-key="${app.identity_key}">
        <div class="item-title">${escapeHtml(app.name)}</div>
        <div class="muted">${escapeHtml(app.scanner)} • ${escapeHtml(app.status)} • ${escapeHtml(app.confidence)} / ${escapeHtml(app.usefulness)}</div>
        <div class="muted" style="margin-top:6px;">${escapeHtml(descriptionText || '')}</div>
        ${language ? `<div class="muted" style="margin-top:8px;">Original language: ${escapeHtml(language.label)}</div>` : ''}
      </div>
    `;
  }).join('');
  list.querySelectorAll('.item').forEach(el => el.onclick = () => {
    const app = filtered.find(a => a.identity_key === el.dataset.key);
    if (app) renderDetail(app, true);
  });
}

async function saveReview(app, statusOverride=null) {
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
  await loadApps();
}

function renderDetail(app, scrollOnMobile=true) {
  selected = app;
  renderList();
  const detail = document.getElementById('detail');
  const primaryUrl = app.urls[0] || '#';
  const descriptionText = htmlToText(app.desc || '');
  const originalLanguage = detectOriginalLanguage(descriptionText || app.name || '');
  detail.innerHTML = `
    <div class='detail-card'>
      <div class='row'>
        <h2 class='headline'>${escapeHtml(app.name)}</h2>
        <div class='chip'>${escapeHtml(app.scanner)}</div>
        <div class='chip'>status: ${escapeHtml(app.status)}</div>
        <div class='chip'>confidence: ${escapeHtml(app.confidence)}</div>
        <div class='chip'>usefulness: ${escapeHtml(app.usefulness)}</div>
        ${originalLanguage ? `<div class='chip'>original language: ${escapeHtml(originalLanguage.label)}</div>` : ''}
      </div>
      <div class='row'><a href='${escapeAttr(primaryUrl)}' target='_blank'>Open primary URL</a></div>
      <div class='subgrid'>
        <div><strong>Artifact quality</strong><div class='muted'>${escapeHtml(app.release_info.quality_label || 'unknown')}</div></div>
        <div><strong>Fork lineage</strong><div class='muted'>${escapeHtml(app.fork_lineage.parent_full_name || 'none')}</div></div>
      </div>
      <div class='row'><strong>Description</strong><div class='muted' style='margin-top:6px;'>${escapeHtml(descriptionText || 'No description')}</div></div>
      ${originalLanguage ? `
      <div class='row'>
        <div class='button-row'>
          <button class='button-translate' id='translateBtn'>Translate description</button>
        </div>
      </div>` : ''}
      <div class='row'><strong>Evidence</strong><pre>${escapeHtml(JSON.stringify(app.evidence, null, 2))}</pre></div>
      <div class='row'>
        <div class='button-row'>
          <button class='button-confirm' id='confirmBtn'>Mark confirmed</button>
          <button class='button-reviewed' id='reviewedBtn'>Mark reviewed</button>
          <button class='button-false' id='falseBtn'>Mark false_positive</button>
          <button class='button-archive' id='archiveBtn'>Mark archived</button>
        </div>
      </div>
      <div class='row'>
        <label>Status</label><br>
        <select id='status'>
          ${['new','confirmed','reviewed','false_positive','archived'].map(s => `<option value="${s}" ${app.status===s?'selected':''}>${s}</option>`).join('')}
        </select>
      </div>
      <div class='row'>
        <label>Review notes</label><br>
        <textarea id='notes'>${escapeHtml(app.review_notes || '')}</textarea>
      </div>
      <div class='row'>
        <label>Reviewed by</label><br>
        <input id='reviewedBy' value='${escapeAttr(app.reviewed_by || '')}'>
      </div>
      <div class='row'><button id='saveBtn'>Save review</button></div>
      <div class='row muted save-status' id='saveStatus'></div>
    </div>
  `;
  const translateBtn = document.getElementById('translateBtn');
  if (translateBtn) {
    translateBtn.onclick = () => openTranslate(descriptionText || app.name || '');
  }
  document.getElementById('saveBtn').onclick = async () => saveReview(app);
  document.getElementById('confirmBtn').onclick = async () => saveReview(app, 'confirmed');
  document.getElementById('reviewedBtn').onclick = async () => saveReview(app, 'reviewed');
  document.getElementById('falseBtn').onclick = async () => saveReview(app, 'false_positive');
  document.getElementById('archiveBtn').onclick = async () => saveReview(app, 'archived');
  if (scrollOnMobile && isMobileLayout()) {
    detail.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
}

function escapeHtml(s) {
  return String(s).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;');
}
function escapeAttr(s) { return escapeHtml(s).replaceAll("'", '&#39;'); }

document.getElementById('search').addEventListener('input', renderList);
document.getElementById('statusFilter').addEventListener('change', renderList);
document.getElementById('reload').addEventListener('click', loadApps);
window.addEventListener('resize', () => { if (selected) renderDetail(selected, false); });
loadApps();
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
