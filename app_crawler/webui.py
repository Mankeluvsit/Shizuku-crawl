from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from .cache import Cache
from .config import AppConfig
from .models import AppResult, ReviewState


HTML = """<!doctype html>
<html>
<head>
  <meta charset='utf-8'>
  <title>App Crawler Review UI</title>
  <style>
    body { font-family: sans-serif; margin: 0; }
    .bar { padding: 12px; border-bottom: 1px solid #ddd; display: flex; gap: 8px; position: sticky; top: 0; background: #fff; }
    .layout { display: grid; grid-template-columns: 38% 62%; min-height: calc(100vh - 50px); }
    .list { border-right: 1px solid #ddd; overflow: auto; }
    .detail { padding: 16px; overflow: auto; }
    .item { padding: 12px; border-bottom: 1px solid #eee; cursor: pointer; }
    .item:hover { background: #f8f8f8; }
    .muted { color: #666; font-size: 12px; }
    textarea { width: 100%; min-height: 120px; }
    select, input, button, textarea { font: inherit; padding: 8px; }
    pre { white-space: pre-wrap; word-break: break-word; background: #f7f7f7; padding: 12px; }
    .row { margin-bottom: 12px; }
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
    <div class='detail' id='detail'><div class='muted'>Select an entry.</div></div>
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
    if (next) renderDetail(next);
  }
}

function renderList() {
  const q = document.getElementById('search').value.trim().toLowerCase();
  const sf = document.getElementById('statusFilter').value;
  const list = document.getElementById('list');
  const filtered = allApps.filter(app => {
    const text = `${app.name} ${app.scanner} ${app.desc || ''}`.toLowerCase();
    const okQ = !q || text.includes(q);
    const okS = !sf || app.status === sf;
    return okQ && okS;
  });
  list.innerHTML = filtered.map(app => `
    <div class="item" data-key="${app.identity_key}">
      <div><strong>${escapeHtml(app.name)}</strong></div>
      <div class="muted">${escapeHtml(app.scanner)} • ${escapeHtml(app.status)} • ${escapeHtml(app.confidence)} / ${escapeHtml(app.usefulness)}</div>
      <div class="muted">${escapeHtml(app.desc || '')}</div>
    </div>
  `).join('');
  list.querySelectorAll('.item').forEach(el => el.onclick = () => {
    const app = filtered.find(a => a.identity_key === el.dataset.key);
    if (app) renderDetail(app);
  });
}

function renderDetail(app) {
  selected = app;
  const detail = document.getElementById('detail');
  detail.innerHTML = `
    <div class='row'><h2>${escapeHtml(app.name)}</h2></div>
    <div class='row'><a href='${escapeAttr(app.urls[0] || '#')}' target='_blank'>Open primary URL</a></div>
    <div class='row'><strong>Scanner:</strong> ${escapeHtml(app.scanner)}</div>
    <div class='row'><strong>Description:</strong> ${escapeHtml(app.desc || '')}</div>
    <div class='row'><strong>Artifact quality:</strong> ${escapeHtml(app.release_info.quality_label || 'unknown')}</div>
    <div class='row'><strong>Fork lineage:</strong> ${escapeHtml(app.fork_lineage.parent_full_name || '')}</div>
    <div class='row'><strong>Evidence:</strong><pre>${escapeHtml(JSON.stringify(app.evidence, null, 2))}</pre></div>
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
    <div class='row muted' id='saveStatus'></div>
  `;
  document.getElementById('saveBtn').onclick = async () => {
    const payload = {
      identity_key: app.identity_key,
      status: document.getElementById('status').value,
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
  };
}

function escapeHtml(s) {
  return String(s).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;');
}
function escapeAttr(s) { return escapeHtml(s).replaceAll("'", '&#39;'); }

document.getElementById('search').addEventListener('input', renderList);
document.getElementById('statusFilter').addEventListener('change', renderList);
document.getElementById('reload').addEventListener('click', loadApps);
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
