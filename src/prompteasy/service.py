from __future__ import annotations

from datetime import datetime, timezone
from collections import defaultdict, deque
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from .api import analyze_prompt, evaluate_prompt
from .llm import OfflineProvider
from .models import PromptAnalysis


app = FastAPI(title="PromptEasyAI")

RATE_LIMIT = 60
RATE_WINDOW_SECONDS = 60
_request_counts: dict[str, int] = defaultdict(int)
_request_times: dict[str, deque[datetime]] = defaultdict(deque)
_metrics: dict[str, int] = defaultdict(int)


@app.middleware("http")
async def request_observability(request: Request, call_next):
  request_id = request.headers.get("X-Request-ID") or str(uuid4())
  client_key = request.client.host if request.client else "unknown"
  now = datetime.now(timezone.utc)
  request_times = _request_times[client_key]

  while request_times and (now - request_times[0]).total_seconds() >= RATE_WINDOW_SECONDS:
    request_times.popleft()

  if len(request_times) >= RATE_LIMIT:
    _metrics["rate_limited_requests"] += 1
    return JSONResponse(
      status_code=429,
      content={"detail": "Request rate limit exceeded.", "request_id": request_id},
      headers={"X-Request-ID": request_id, "Retry-After": "60"},
    )

  request_times.append(now)
  _request_counts[request.method] += 1
  _metrics["requests"] += 1

  try:
    response = await call_next(request)
  except Exception:
    _metrics["errors"] += 1
    raise

  _metrics[f"status_{response.status_code}"] += 1
  response.headers["X-Request-ID"] = request_id
  return response

_history_store: list[dict[str, Any]] = []
_preferences_store: dict[str, Any] = {
    "tone": "neutral",
    "audience": "general",
    "domain": "general",
}

INDEX_HTML = """
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>PromptEasyAI</title>
    <style>
      :root {
        --bg: #0f172a;
        --panel: #111827;
        --panel-alt: #1f2937;
        --text: #e5e7eb;
        --muted: #9ca3af;
        --accent: #38bdf8;
        --accent-strong: #0ea5e9;
        --border: #334155;
        --success: #22c55e;
        --warning: #f59e0b;
        --error: #ef4444;
      }
      * { box-sizing: border-box; }
      body {
        margin: 0;
        font-family: "Trebuchet MS", sans-serif;
        background: radial-gradient(circle at top right, #164e63 0%, transparent 34%), linear-gradient(180deg, #07111f 0%, #10253a 100%);
        color: var(--text);
      }
      .shell {
        max-width: 1200px;
        margin: 0 auto;
        padding: 32px 16px 64px;
      }
      h1 {
        margin: 0 0 8px;
        font-size: clamp(2rem, 4vw, 3rem);
      }
      .subtitle {
        margin: 0 0 24px;
        color: var(--muted);
      }
      .layout {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 24px;
      }
      .panel {
        background: rgba(17, 24, 39, 0.9);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.5);
      }
      textarea {
        width: 100%;
        min-height: 220px;
        resize: vertical;
        border-radius: 12px;
        background: var(--panel-alt);
        border: 1px solid var(--border);
        color: var(--text);
        padding: 14px;
        font-size: 1rem;
      }
      button {
        background: linear-gradient(135deg, var(--accent), var(--accent-strong));
        border: none;
        border-radius: 10px;
        padding: 12px 18px;
        color: #082f49;
        font-weight: 700;
        cursor: pointer;
      }
      button.secondary {
        background: transparent;
        border: 1px solid var(--border);
        color: var(--text);
      }
      button:disabled {
        opacity: 0.6;
        cursor: wait;
      }
      .meta {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        margin-bottom: 16px;
      }
      .status {
        color: var(--muted);
        font-size: 0.92rem;
      }
      .actions {
        display: flex;
        justify-content: flex-end;
        gap: 12px;
        margin-top: 16px;
        flex-wrap: wrap;
      }
      .feedback-row {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        margin-top: 16px;
      }
      .feedback-row button {
        font-size: 0.9rem;
        padding: 10px 12px;
      }
      .result-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 16px;
      }
      .result-block {
        background: rgba(15, 23, 42, 0.9);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 14px;
        min-width: 0;
      }
      .result-block h3 {
        margin: 0 0 12px;
        font-size: 1rem;
      }
      .result-block p,
      .result-block pre {
        margin: 0;
        white-space: pre-wrap;
        word-break: break-word;
        font-family: inherit;
      }
      .result-block.featured {
        grid-column: 1 / -1;
        border-color: var(--accent-strong);
      }
      .optimized-editor {
        width: 100%;
        min-height: 150px;
        resize: vertical;
        border-radius: 8px;
        background: #0b1d2d;
        border: 1px solid var(--accent-strong);
        color: var(--text);
        padding: 12px;
        font: inherit;
        line-height: 1.5;
      }
      .quality-badge {
        display: inline-flex;
        margin-top: 12px;
        padding: 6px 10px;
        border-radius: 999px;
        color: #052e16;
        background: var(--success);
        font-size: 0.82rem;
        font-weight: 700;
      }
      ul {
        margin: 0;
        padding-left: 18px;
      }
      li + li {
        margin-top: 8px;
      }
      .empty {
        color: var(--muted);
        font-style: italic;
      }
      .error {
        color: var(--error);
      }
      .success {
        color: var(--success);
      }
      .hidden {
        display: none;
      }
      @media (max-width: 800px) {
        .layout, .result-grid {
          grid-template-columns: 1fr;
        }
      }
    </style>
  </head>
  <body>
    <div class="shell">
      <h1>PromptEasyAI</h1>
      <p class="subtitle">Turn vague prompts into precise, reusable instructions.</p>

      <div class="layout">
        <section class="panel">
          <div class="meta">
            <h2>Prompt input</h2>
            <span id="status" class="status" aria-live="polite">Ready</span>
          </div>
          <form id="prompt-form">
            <label for="prompt" class="hidden">Prompt</label>
            <textarea id="prompt" placeholder="Describe the task, audience, constraints, and desired output..."></textarea>
            <div class="actions">
              <button type="button" class="secondary" id="reset-button">Reset</button>
              <button type="submit" id="analyze-button">Analyze</button>
            </div>
          </form>
        </section>

        <section class="panel">
          <div class="meta">
            <h2>Analysis</h2>
            <div class="actions" style="margin-top: 0;">
              <button type="button" class="secondary" id="copy-button">Copy optimized prompt</button>
              <button type="button" class="secondary" id="export-button">Export JSON</button>
            </div>
          </div>
          <div id="analysis-output" class="empty" aria-live="polite">No analysis yet.</div>
          <div class="feedback-row" id="feedback-row">
            <button type="button" class="secondary" data-feedback="useful">Useful</button>
            <button type="button" class="secondary" data-feedback="needs-work">Needs work</button>
          </div>
        </section>
      </div>
    </div>

    <script>
      const form = document.getElementById('prompt-form');
      const promptInput = document.getElementById('prompt');
      const statusEl = document.getElementById('status');
      const outputEl = document.getElementById('analysis-output');
      const analyzeButton = document.getElementById('analyze-button');
      const resetButton = document.getElementById('reset-button');
      const copyButton = document.getElementById('copy-button');
      const exportButton = document.getElementById('export-button');
      const feedbackRow = document.getElementById('feedback-row');
      let lastAnalysis = null;

      function escapeHtml(value) {
        return String(value)
          .replace(/&/g, '&amp;')
          .replace(/</g, '&lt;')
          .replace(/>/g, '&gt;')
          .replace(/"/g, '&quot;')
          .replace(/'/g, '&#039;');
      }

      function renderList(items) {
        if (!items || items.length === 0) {
          return '<div class="empty">None provided.</div>';
        }
        return '<ul>' + items.map((item) => '<li>' + escapeHtml(item) + '</li>').join('') + '</ul>';
      }

      function renderAnalysis(data) {
        const sections = [
          ['Original prompt', data.original_prompt || '', 'original'],
          ['Intent', data.intent || ''],
          ['Task', data.task || ''],
          ['Context', renderList(data.context)],
          ['Constraints', renderList(data.constraints)],
          ['Output requirements', renderList(data.output_requirements)],
          ['Ambiguities', renderList(data.ambiguities)],
          ['Missing information', renderList(data.missing_information)],
          ['Optimization opportunities', renderList(data.optimization_opportunities)],
          ['Optimized prompt', data.optimized_prompt || '', 'featured']
        ];

        const blocks = sections.map(([label, value, variant]) => {
          let markup = '';
          if (label === 'Optimized prompt') {
            markup = '<textarea id="optimized-editor" class="optimized-editor" aria-label="Editable optimized prompt">' + escapeHtml(value) + '</textarea>';
          } else if (typeof value === 'string') {
            markup = value ? '<p>' + escapeHtml(value) + '</p>' : '<div class="empty">None provided.</div>';
          } else {
            markup = value;
          }

          return `
            <div class="result-block ${variant || ''}">
              <h3>${escapeHtml(label)}</h3>
              ${markup}
              ${label === 'Optimized prompt' ? '<span class="quality-badge" id="quality-badge">Validated for intent and unsupported details</span>' : ''}
            </div>
          `;
        }).join('');

        return '<div class="result-grid">' + blocks + '</div>';
      }

      function setStatus(message, tone = 'default') {
        statusEl.textContent = message;
        statusEl.className = 'status';
        if (tone === 'error') {
          statusEl.classList.add('error');
        } else if (tone === 'success') {
          statusEl.classList.add('success');
        }
      }

      function resetView() {
        promptInput.value = '';
        outputEl.className = 'empty';
        outputEl.textContent = 'No analysis yet.';
        lastAnalysis = null;
        copyButton.disabled = true;
        exportButton.disabled = true;
        feedbackRow.style.opacity = '0.5';
        setStatus('Ready');
      }

      form.addEventListener('submit', async (event) => {
        event.preventDefault();
        const prompt = promptInput.value.trim();
        if (!prompt) {
          setStatus('Enter a prompt first', 'error');
          return;
        }

        setStatus('Analyzing...', 'default');
        analyzeButton.disabled = true;
        copyButton.disabled = true;

        try {
          const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt })
          });

          if (!response.ok) {
            const payload = await response.json().catch(() => ({}));
            throw new Error(payload.detail || 'Analysis request failed');
          }

          const data = await response.json();
          lastAnalysis = data;
          outputEl.className = '';
          outputEl.innerHTML = renderAnalysis(data);
          copyButton.disabled = !data.optimized_prompt;
          exportButton.disabled = !data.optimized_prompt;
          feedbackRow.style.opacity = '1';
          setStatus('Analysis complete', 'success');
        } catch (error) {
          outputEl.className = 'error';
          outputEl.textContent = String(error.message || error);
          setStatus('Error', 'error');
        } finally {
          analyzeButton.disabled = false;
        }
      });

      resetButton.addEventListener('click', resetView);

      copyButton.addEventListener('click', async () => {
        const editor = document.getElementById('optimized-editor');
        const optimizedPrompt = editor ? editor.value.trim() : lastAnalysis && lastAnalysis.optimized_prompt;
        if (!optimizedPrompt) {
          return;
        }

        try {
          await navigator.clipboard.writeText(optimizedPrompt);
          setStatus('Prompt copied', 'success');
        } catch (error) {
          const textArea = document.createElement('textarea');
          textArea.value = optimizedPrompt;
          document.body.appendChild(textArea);
          textArea.select();
          document.execCommand('copy');
          document.body.removeChild(textArea);
          setStatus('Prompt copied', 'success');
        }
      });

      exportButton.addEventListener('click', () => {
        if (!lastAnalysis) {
          return;
        }

        const editor = document.getElementById('optimized-editor');
        const exportData = { ...lastAnalysis, optimized_prompt: editor ? editor.value : lastAnalysis.optimized_prompt };
        const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const anchor = document.createElement('a');
        anchor.href = url;
        anchor.download = 'prompteasy-analysis.json';
        document.body.appendChild(anchor);
        anchor.click();
        document.body.removeChild(anchor);
        URL.revokeObjectURL(url);
        setStatus('Analysis exported', 'success');
      });

      feedbackRow.querySelectorAll('button').forEach((button) => {
        button.addEventListener('click', () => {
          const label = button.dataset.feedback;
          setStatus(label === 'useful' ? 'Marked useful' : 'Feedback recorded', 'success');
        });
      });

      copyButton.disabled = true;
      exportButton.disabled = true;
      feedbackRow.style.opacity = '0.5';
    </script>
  </body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
def serve_ui() -> HTMLResponse:
    return HTMLResponse(INDEX_HTML)


class AnalyzeRequest(BaseModel):
    prompt: str


class HistoryEntryRequest(BaseModel):
    analysis: dict[str, Any]
    label: str | None = None


class PreferencesUpdate(BaseModel):
    tone: str | None = None
    audience: str | None = None
    domain: str | None = None


class EvaluateRequest(BaseModel):
    analysis: dict[str, Any]


@app.get("/health")
def health() -> dict[str, Any]:
  return {"status": "ok", "service": "prompteasyai", "version": "0.1.0"}


@app.get("/api/metrics")
def metrics() -> dict[str, Any]:
  return {
    "requests": dict(_metrics),
    "methods": dict(_request_counts),
    "history_entries": len(_history_store),
  }


@app.get("/api/config")
def config() -> dict[str, str]:
    return {"provider": "offline", "model": "offline-model"}


@app.post("/api/analyze")
def analyze_endpoint(payload: AnalyzeRequest) -> dict[str, Any]:
    try:
        analysis = analyze_prompt(payload.prompt, provider=OfflineProvider())
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return analysis.model_dump(mode="json")


@app.post("/api/evaluate")
def evaluate_endpoint(payload: EvaluateRequest) -> dict[str, Any]:
    try:
        analysis = PromptAnalysis.model_validate(payload.analysis)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="Invalid analysis payload.") from exc
    result = evaluate_prompt(analysis)
    return {"valid": result.valid, "errors": result.errors}


@app.get("/api/history")
def list_history() -> dict[str, Any]:
    return {"items": _history_store}


@app.post("/api/history")
def save_history(payload: HistoryEntryRequest) -> dict[str, Any]:
    analysis = PromptAnalysis.model_validate(payload.analysis)
    entry = {
        "id": len(_history_store) + 1,
        "label": payload.label or "untitled",
        "saved_at": datetime.now(timezone.utc).isoformat(),
        "analysis": analysis.model_dump(mode="json"),
    }
    _history_store.insert(0, entry)
    return {"count": len(_history_store), "items": _history_store}


@app.get("/api/preferences")
def get_preferences() -> dict[str, Any]:
    return {"preferences": _preferences_store}


@app.post("/api/preferences")
def update_preferences(payload: PreferencesUpdate) -> dict[str, Any]:
    for field, value in payload.model_dump(exclude_none=True).items():
        _preferences_store[field] = value
    return _preferences_store
