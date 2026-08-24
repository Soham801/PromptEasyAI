from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from .api import analyze_prompt, evaluate_prompt
from .llm import OfflineProvider
from .models import PromptAnalysis


app = FastAPI(title="PromptEasyAI")

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
        font-family: Arial, sans-serif;
        background: linear-gradient(180deg, #020817 0%, #0f172a 100%);
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
            <button type="button" class="secondary" id="copy-button">Copy optimized prompt</button>
          </div>
          <div id="analysis-output" class="empty">No analysis yet.</div>
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
          ['Original prompt', data.original_prompt || ''],
          ['Intent', data.intent || ''],
          ['Task', data.task || ''],
          ['Context', renderList(data.context)],
          ['Constraints', renderList(data.constraints)],
          ['Output requirements', renderList(data.output_requirements)],
          ['Ambiguities', renderList(data.ambiguities)],
          ['Missing information', renderList(data.missing_information)],
          ['Optimization opportunities', renderList(data.optimization_opportunities)],
          ['Optimized prompt', data.optimized_prompt || '']
        ];

        const blocks = sections.map(([label, value]) => {
          let markup = '';
          if (typeof value === 'string') {
            markup = value ? '<p>' + escapeHtml(value) + '</p>' : '<div class="empty">None provided.</div>';
          } else {
            markup = value;
          }

          return `
            <div class="result-block">
              <h3>${escapeHtml(label)}</h3>
              ${markup}
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
        if (!lastAnalysis || !lastAnalysis.optimized_prompt) {
          return;
        }

        try {
          await navigator.clipboard.writeText(lastAnalysis.optimized_prompt);
          setStatus('Prompt copied', 'success');
        } catch (error) {
          const textArea = document.createElement('textarea');
          textArea.value = lastAnalysis.optimized_prompt;
          document.body.appendChild(textArea);
          textArea.select();
          document.execCommand('copy');
          document.body.removeChild(textArea);
          setStatus('Prompt copied', 'success');
        }
      });

      copyButton.disabled = true;
    </script>
  </body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
def serve_ui() -> HTMLResponse:
    return HTMLResponse(INDEX_HTML)


class AnalyzeRequest(BaseModel):
    prompt: str


class EvaluateRequest(BaseModel):
    analysis: dict[str, Any]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/config")
def config() -> dict[str, str]:
    return {"provider": "offline", "model": "offline-model"}


@app.post("/api/analyze")
def analyze_endpoint(payload: AnalyzeRequest) -> dict[str, Any]:
    analysis = analyze_prompt(payload.prompt, provider=OfflineProvider())
    return analysis.model_dump(mode="json")


@app.post("/api/evaluate")
def evaluate_endpoint(payload: EvaluateRequest) -> dict[str, Any]:
    analysis = PromptAnalysis.model_validate(payload.analysis)
    result = evaluate_prompt(analysis)
    return {"valid": result.valid, "errors": result.errors}
