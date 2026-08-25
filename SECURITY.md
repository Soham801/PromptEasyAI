# Security And Release Checklist

PromptEasyAI is currently intended for local and controlled deployment. Complete this checklist before exposing it to public users.

## Current V0.1 Baseline

- Do not commit `.env` files, API keys, or provider responses containing sensitive prompts.
- Keep live provider probes opt-in with `PROMPTEASY_RUN_LIVE_GROQ=1`.
- Use the offline provider for tests and local verification.
- Treat prompt text and analysis results as user data; do not log them by default.
- Use the `X-Request-ID` response header to correlate errors without exposing prompt contents.
- Keep the current in-memory history store restricted to local or single-process use.

## Before Public Deployment

- Set `PROMPTEASY_ENV=production`; production startup rejects the offline provider.
- Set `PROMPTEASY_PROVIDER=groq` and `PROMPTEASY_MODEL` explicitly, with `GROQ_API_KEY` supplied by the deployment secret manager.
- Use the supplied `Dockerfile` or an equivalent pinned deployment image and expose only the service port through the ingress layer.
- Move history and preferences to authenticated, persistent storage with migrations and backups.
- Store provider secrets in a managed secret store and rotate them regularly.
- Add authentication, authorization, per-user quotas, and external rate limiting.
- Add dependency vulnerability scanning and container/image scanning in CI.
- Add prompt-injection, data-isolation, and request-size tests.
- Enable HTTPS, structured log redaction, monitoring, alerting, and rollback procedures.
- Load-test the service and confirm provider cost limits.