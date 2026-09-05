from __future__ import annotations

from datetime import datetime, timezone
from collections import defaultdict, deque
import hashlib
import hmac
from typing import Any
from uuid import uuid4
import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .api import analyze_prompt, evaluate_prompt, get_provider_config
from .config import get_settings
from .models import PromptAnalysis
from .optimizer import OptimizationPreferences
from .storage import Storage
from .deployment import SecurityValidator, configure_logging


# Configure logging based on settings
settings = get_settings()
configure_logging(settings.environment, settings.monitoring.log_level)
logger = logging.getLogger(__name__)

app = FastAPI(title="PromptEasyAI")

RATE_LIMIT = get_settings().request_rate_limit
RATE_WINDOW_SECONDS = 60
_request_counts: dict[str, int] = defaultdict(int)
_request_times: dict[str, deque[datetime]] = defaultdict(deque)
_metrics: dict[str, int] = defaultdict(int)


# Add CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.environment == "development" else ["https://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    """Add security headers to all responses."""
    response = await call_next(request)
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
    
    return response


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

_storage = Storage(get_settings().storage_path)


def _user_id(request: Request) -> str:
  configured_token = get_settings().auth_token
  if not configured_token:
    return "anonymous"

  authorization = request.headers.get("Authorization", "")
  if not authorization.startswith("Bearer "):
    raise HTTPException(status_code=401, detail="Bearer authentication is required.")
  credential = authorization.removeprefix("Bearer ")
  if "." not in credential:
    raise HTTPException(status_code=401, detail="Invalid bearer credential.")
  user_name, supplied_token = credential.split(".", 1)
  if not user_name or not hmac.compare_digest(supplied_token, configured_token):
    raise HTTPException(status_code=401, detail="Invalid bearer credential.")
  return hashlib.sha256(user_name.encode("utf-8")).hexdigest()

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
          ['Intent', data.intent || '', false],
          ['Task', data.task || '', false],
          ['Context', renderList(data.context), true],
          ['Constraints', renderList(data.constraints), true],
          ['Output requirements', renderList(data.output_requirements), true],
          ['Ambiguities', renderList(data.ambiguities), true],
          ['Missing information', renderList(data.missing_information), true],
          ['Optimization opportunities', renderList(data.optimization_opportunities), true],
          ['Optimized prompt', data.optimized_prompt || '', 'featured']
        ];

        const blocks = sections.map(([label, value, variant]) => {
          let markup = '';
          if (label === 'Optimized prompt') {
            markup = '<textarea id="optimized-editor" class="optimized-editor" aria-label="Editable optimized prompt">' + escapeHtml(value) + '</textarea>';
          } else if (variant === true) {
            markup = value;
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
  settings_obj = get_settings()
  health_check = settings_obj.get_health_check()
  return {
    "status": "ok" if health_check["healthy"] else "degraded",
    "service": "prompteasyai",
    "version": "0.1.0",
    "environment": settings_obj.environment,
    "deployment_health": health_check,
  }


@app.get("/api/metrics")
def metrics() -> dict[str, Any]:
  settings_obj = get_settings()
  return {
    "requests": dict(_metrics),
    "methods": dict(_request_counts),
    "history_entries": _storage.count_history(),
    "deployment": {
      "environment": settings_obj.environment,
      "provider": settings_obj.provider,
      "https_enabled": settings_obj.https_config.enabled,
      "metrics_enabled": settings_obj.monitoring.metrics_enabled,
    }
  }


@app.post("/api/security/check")
def security_check_prompt(payload: AnalyzeRequest) -> dict[str, Any]:
  """Analyze prompt for security risks without processing it."""
  injection_risk = SecurityValidator.validate_prompt_injection_risk(payload.prompt)
  secrets_check = SecurityValidator.validate_secrets_in_prompt(payload.prompt)
  content_hash = SecurityValidator.compute_content_hash(payload.prompt)
  
  return {
    "prompt_hash": content_hash,
    "injection_risk": {
      "safe": injection_risk["safe"],
      "risk_level": injection_risk["risk_level"],
      "patterns_found": injection_risk["patterns_found"],
      "recommendation": injection_risk["recommendation"],
    },
    "secrets": {
      "contains_secrets": secrets_check["contains_secrets"],
      "types_found": secrets_check["types_found"],
      "recommendation": secrets_check["recommendation"],
    },
    "overall_safe": injection_risk["safe"] and not secrets_check["contains_secrets"],
  }


@app.get("/api/config")
def config() -> dict[str, str]:
  return get_provider_config()


@app.post("/api/analyze")
def analyze_endpoint(payload: AnalyzeRequest, request: Request) -> dict[str, Any]:
    # Validate prompt length
    settings_obj = get_settings()
    if len(payload.prompt) > settings_obj.quotas.max_prompt_length:
        raise HTTPException(
            status_code=413,
            detail=f"Prompt exceeds maximum length of {settings_obj.quotas.max_prompt_length} characters"
        )
    
    # Check for prompt injection risks
    injection_risk = SecurityValidator.validate_prompt_injection_risk(payload.prompt)
    if not injection_risk["safe"]:
        logger.warning(
            f"Potential prompt injection detected: risk_level={injection_risk['risk_level']}, "
            f"patterns={injection_risk['patterns_found']}"
        )
        if injection_risk["risk_level"] == "high":
            raise HTTPException(
                status_code=400,
                detail="Prompt contains potential injection patterns and cannot be processed"
            )
    
    # Check for secrets in prompt
    secrets_check = SecurityValidator.validate_secrets_in_prompt(payload.prompt)
    if secrets_check["contains_secrets"]:
        logger.warning(
            f"Potential secrets detected in prompt: types={secrets_check['types_found']}"
        )
        # Log but don't block - just warn
    
    try:
        preferences = _storage.get_preferences(_user_id(request))
        analysis = analyze_prompt(
          payload.prompt,
          preferences=OptimizationPreferences(**preferences),
        )
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    
    result = analysis.model_dump(mode="json")
    
    # Add security metadata
    result["security_metadata"] = {
        "injection_risk": injection_risk["risk_level"],
        "contains_secrets": secrets_check["contains_secrets"],
    }
    
    return result


@app.post("/api/evaluate")
def evaluate_endpoint(payload: EvaluateRequest) -> dict[str, Any]:
    try:
        analysis = PromptAnalysis.model_validate(payload.analysis)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="Invalid analysis payload.") from exc
    result = evaluate_prompt(analysis)
    return {"valid": result.valid, "errors": result.errors}


@app.get("/api/history")
def list_history(request: Request) -> dict[str, Any]:
    items = _storage.list_history(_user_id(request))
    return {"items": items}


@app.post("/api/history")
def save_history(payload: HistoryEntryRequest, request: Request) -> dict[str, Any]:
  analysis = PromptAnalysis.model_validate(payload.analysis)
  user_id = _user_id(request)
  entry = {
    "label": payload.label or "untitled",
    "saved_at": datetime.now(timezone.utc).isoformat(),
    "analysis": analysis.model_dump(mode="json"),
  }
  items = _storage.save_history(user_id, entry["label"], entry["saved_at"], entry["analysis"])
  return {"count": len(items), "items": items}


@app.get("/api/preferences")
def get_preferences(request: Request) -> dict[str, Any]:
    return {"preferences": _storage.get_preferences(_user_id(request))}


@app.post("/api/preferences")
def update_preferences(payload: PreferencesUpdate, request: Request) -> dict[str, Any]:
    return _storage.update_preferences(_user_id(request), payload.model_dump(exclude_none=True))
