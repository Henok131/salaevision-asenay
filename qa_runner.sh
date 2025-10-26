#!/usr/bin/env bash
set -euo pipefail

REPORT="qa_report.txt"
: > "$REPORT"

log() { echo "$1" | tee -a "$REPORT"; }
fail() { echo "❌ $1" | tee -a "$REPORT"; exit 1; }

echo "QA RUN START $(date)" | tee -a "$REPORT"

# Load .env if present
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs -d '\n' -I {} echo {}) || true
fi

# Required keys
REQUIRED=(VITE_SUPABASE_URL VITE_SUPABASE_ANON_KEY VITE_FRONTEND_URL)

for k in "${REQUIRED[@]}"; do
  if [ -z "${!k:-}" ]; then
    fail "Missing env key: $k"
  fi
  log "Env OK: $k=${!k}"
done

# Ping Supabase
if curl -sSfI "$VITE_SUPABASE_URL" >/dev/null; then
  log "Supabase ping: OK"
else
  log "Supabase ping: FAILED"
fi

# Frontend tests
pushd frontend >/dev/null

log "Running unit/component tests (Vitest)"
if [ ! -d node_modules ]; then npm ci --no-audit --no-fund; fi
npx vitest run --coverage | tee -a "../$REPORT" || fail "Vitest failed"

log "Building frontend for preview"
npm run build | tee -a "../$REPORT"

log "Starting preview server on http://localhost:5173"
npx vite preview --host 0.0.0.0 --port 5173 >/dev/null 2>&1 &
PREVIEW_PID=$!
sleep 2

# Wait for preview to be ready
ATTEMPTS=20
until curl -sSfI http://localhost:5173 >/dev/null; do
  ATTEMPTS=$((ATTEMPTS-1))
  [ $ATTEMPTS -le 0 ] && { echo "Preview server failed to start" | tee -a "../$REPORT"; kill $PREVIEW_PID || true; fail "Preview failed"; }
  sleep 1
done
log "Preview server is up"

log "Running E2E tests (Playwright)"
npx playwright install --with-deps >/dev/null 2>&1 || true
VITE_FRONTEND_URL=http://localhost:5173 npx playwright test tests/e2e --reporter=line | tee -a "../$REPORT" || { kill $PREVIEW_PID || true; fail "Playwright failed"; }

# Stop preview server
kill $PREVIEW_PID || true

popd >/dev/null

log "QA RUN COMPLETE $(date)"
exit 0
