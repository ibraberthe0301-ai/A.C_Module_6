from datetime import datetime, timezone
import os
import platform
import socket
import time

from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

# Keep Flask's JSON responses predictable and avoid exposing unnecessary details.
app.config.update(
    JSON_SORT_KEYS=False,
    MAX_CONTENT_LENGTH=1 * 1024 * 1024,  # 1 MiB request-body limit
)

STARTED_AT = time.monotonic()
APP_NAME = "Docker API Dashboard"
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
ENVIRONMENT = os.getenv("APP_ENV", "development")

DASHBOARD_HTML = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="dark">
  <title>Docker API Dashboard</title>
  <style>
    :root {
      color-scheme: dark;
      --bg: #0a0a0c;
      --panel: #121216;
      --surface: #1a1a20;
      --border: #2a2d3a;
      --cyan: #00d2ff;
      --blue: #38bdf8;
      --text: #e7edf5;
      --muted: #8b95a7;
      --green: #4ade80;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0; min-height: 100vh; background: var(--bg); color: var(--text);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    code, pre, .mono { font-family: "JetBrains Mono", ui-monospace, SFMono-Regular, Consolas, monospace; }
    .topbar {
      height: 66px; border-bottom: 1px solid var(--border); background: #0d0d11;
      display: flex; align-items: center; justify-content: space-between; padding: 0 5vw;
    }
    .brand { display: flex; gap: 12px; align-items: center; font-weight: 700; letter-spacing: .02em; }
    .mark { width: 10px; height: 10px; background: var(--cyan); box-shadow: 0 0 18px #00d2ff80; }
    .topmeta { color: var(--muted); font: 12px "JetBrains Mono", ui-monospace, monospace; }
    main { width: min(1100px, 90vw); margin: 42px auto 60px; }
    .eyebrow { color: var(--cyan); font: 11px ui-monospace, monospace; letter-spacing: .18em; text-transform: uppercase; }
    h1 { margin: 12px 0 8px; font-size: clamp(28px, 4vw, 42px); letter-spacing: -.04em; }
    .subtitle { color: var(--muted); margin: 0; line-height: 1.6; }
    .statusline { display: flex; flex-wrap: wrap; gap: 10px; margin: 26px 0; }
    .pill { border: 1px solid var(--border); background: var(--panel); padding: 9px 12px; color: var(--muted); font: 12px ui-monospace, monospace; }
    .dot { display: inline-block; width: 7px; height: 7px; border-radius: 50%; background: var(--green); margin-right: 8px; }
    .grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; }
    .card { border: 1px solid var(--border); background: var(--panel); padding: 20px; min-width: 0; }
    .label { color: var(--muted); font: 11px ui-monospace, monospace; letter-spacing: .1em; text-transform: uppercase; }
    .value { margin-top: 14px; font-size: 24px; font-weight: 650; overflow-wrap: anywhere; }
    .value.accent { color: var(--cyan); }
    .section { margin-top: 30px; }
    .sectionhead { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 12px; }
    h2 { font-size: 15px; margin: 0; letter-spacing: .01em; }
    .sectionhead a { color: var(--blue); text-decoration: none; font: 12px ui-monospace, monospace; }
    .endpoint { display: grid; grid-template-columns: 76px minmax(0, 1fr) auto; align-items: center; gap: 14px; border: 1px solid var(--border); border-bottom: 0; background: var(--panel); padding: 15px 18px; }
    .endpoint:last-child { border-bottom: 1px solid var(--border); }
    .method { color: var(--cyan); font: 11px ui-monospace, monospace; border: 1px solid #00d2ff50; padding: 5px 7px; width: fit-content; }
    .path { font: 13px ui-monospace, monospace; }
    .desc { color: var(--muted); font-size: 12px; margin-top: 5px; }
    .response { color: var(--green); font: 11px ui-monospace, monospace; }
    .jsonbox { border: 1px solid var(--border); background: #08080a; padding: 18px; overflow-x: auto; color: #b8e9f5; font-size: 12px; line-height: 1.7; }
    .actions { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 14px; }
    button { background: var(--surface); border: 1px solid var(--border); color: var(--text); padding: 10px 13px; cursor: pointer; font: 12px ui-monospace, monospace; }
    button:hover { border-color: var(--cyan); color: var(--cyan); }
    .foot { border-top: 1px solid var(--border); margin-top: 40px; padding-top: 18px; color: var(--muted); font: 11px ui-monospace, monospace; display: flex; justify-content: space-between; gap: 10px; flex-wrap: wrap; }
    @media (max-width: 720px) {
      .grid { grid-template-columns: 1fr; }
      .topbar { padding: 0 5vw; }
      .topmeta { display: none; }
      .endpoint { grid-template-columns: 65px minmax(0, 1fr); }
      .response { grid-column: 2; }
      main { margin-top: 30px; }
    }
  </style>
</head>
<body>
  <header class="topbar">
    <div class="brand"><span class="mark"></span><span>DOCKER / API</span></div>
    <div class="topmeta">LOCAL INSTANCE &nbsp;·&nbsp; PORT 5000</div>
  </header>
  <main>
    <div class="eyebrow">System overview / 001</div>
    <h1>API Dashboard</h1>
    <p class="subtitle">A minimal operational view of the Flask service running inside your Docker container.</p>

    <div class="statusline">
      <div class="pill"><span class="dot"></span>SERVICE OPERATIONAL</div>
      <div class="pill">HTTP / REST</div>
      <div class="pill">VERSION <span id="version">{{ version }}</span></div>
    </div>

    <section class="grid" aria-label="Service metrics">
      <article class="card"><div class="label">Health status</div><div class="value accent" id="health">Checking...</div></article>
      <article class="card"><div class="label">Uptime</div><div class="value" id="uptime">—</div></article>
      <article class="card"><div class="label">Environment</div><div class="value" id="environment">{{ environment }}</div></article>
    </section>

    <section class="section">
      <div class="sectionhead"><h2>Available endpoints</h2><span class="label">HTTP ROUTES</span></div>
      <div class="endpoint">
        <span class="method">GET</span><div><div class="path">/</div><div class="desc">Dashboard UI or JSON response, based on Accept header.</div></div><span class="response">200 OK</span>
      </div>
      <div class="endpoint">
        <span class="method">GET</span><div><div class="path">/health</div><div class="desc">Lightweight service health check.</div></div><span class="response">200 OK</span>
      </div>
      <div class="endpoint">
        <span class="method">GET</span><div><div class="path">/api/status</div><div class="desc">Runtime and application metadata in JSON format.</div></div><span class="response">200 OK</span>
      </div>
    </section>

    <section class="section">
      <div class="sectionhead"><h2>Live health response</h2><a href="/health" target="_blank" rel="noopener">OPEN JSON ↗</a></div>
      <pre class="jsonbox" id="healthJson">Loading health endpoint...</pre>
      <div class="actions"><button type="button" id="refresh">REFRESH STATUS</button><button type="button" id="copy">COPY JSON</button></div>
    </section>

    <footer class="foot"><span>FLASK SERVICE / DOCKER CONTAINER</span><span>NO EXTERNAL TRACKING</span></footer>
  </main>
  <script>
    const healthEl = document.getElementById('health');
    const uptimeEl = document.getElementById('uptime');
    const jsonEl = document.getElementById('healthJson');
    let latestJson = '';
    function formatUptime(seconds) {
      seconds = Math.max(0, Math.floor(seconds || 0));
      const days = Math.floor(seconds / 86400);
      const hours = Math.floor((seconds % 86400) / 3600);
      const minutes = Math.floor((seconds % 3600) / 60);
      const secs = seconds % 60;
      return (days ? days + 'd ' : '') + String(hours).padStart(2, '0') + ':' +
             String(minutes).padStart(2, '0') + ':' + String(secs).padStart(2, '0');
    }
    async function refreshStatus() {
      try {
        const response = await fetch('/api/status', { headers: { 'Accept': 'application/json' }, cache: 'no-store' });
        if (!response.ok) throw new Error('HTTP ' + response.status);
        const data = await response.json();
        healthEl.textContent = data.status.toUpperCase();
        uptimeEl.textContent = formatUptime(data.uptime_seconds);
        latestJson = JSON.stringify(data, null, 2);
        jsonEl.textContent = latestJson;
      } catch (error) {
        healthEl.textContent = 'UNAVAILABLE';
        jsonEl.textContent = 'Unable to retrieve service status.';
      }
    }
    document.getElementById('refresh').addEventListener('click', refreshStatus);
    document.getElementById('copy').addEventListener('click', async () => {
      if (!latestJson) return;
      try {
        await navigator.clipboard.writeText(latestJson);
        document.getElementById('copy').textContent = 'COPIED';
        setTimeout(() => document.getElementById('copy').textContent = 'COPY JSON', 1400);
      } catch (_) {
        document.getElementById('copy').textContent = 'COPY BLOCKED';
      }
    });
    refreshStatus();
    setInterval(refreshStatus, 15000);
  </script>
</body>
</html>"""


def wants_json():
    """Return True when the client explicitly prefers JSON."""
    if request.path == "/":
        accept = request.headers.get("Accept", "")
        return "application/json" in accept.lower()
    return True


@app.get("/")
def index():
    if wants_json():
        return jsonify(message="My Docker API is running")
    return render_template_string(
        DASHBOARD_HTML,
        version=APP_VERSION,
        environment=ENVIRONMENT,
    )


@app.get("/health")
def health():
    return jsonify(
        status="ok",
        service=APP_NAME,
        timestamp=datetime.now(timezone.utc).isoformat(),
    ), 200


@app.get("/api/status")
def api_status():
    return jsonify(
        status="ok",
        service=APP_NAME,
        version=APP_VERSION,
        environment=ENVIRONMENT,
        uptime_seconds=round(time.monotonic() - STARTED_AT, 2),
        python_version=platform.python_version(),
        hostname=socket.gethostname(),
        timestamp=datetime.now(timezone.utc).isoformat(),
    ), 200


@app.errorhandler(404)
def not_found(_error):
    return jsonify(error="not_found", message="The requested endpoint does not exist."), 404


@app.errorhandler(405)
def method_not_allowed(_error):
    return jsonify(error="method_not_allowed", message="The HTTP method is not supported for this endpoint."), 405


@app.errorhandler(413)
def payload_too_large(_error):
    return jsonify(error="payload_too_large", message="Request body exceeds the 1 MiB limit."), 413


if __name__ == "__main__":
    # The Dockerfile should run as a non-root user and publish port 5000.
    # Debug mode is intentionally disabled.
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False)
