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
npx vitest run --coverage | tee -a "../$REPORT" || fail "Vitest failed"

log "Running E2E tests (Playwright)"
if [ ! -d node_modules ]; then npm ci --no-audit --no-fund; fi
npx playwright install --with-deps >/dev/null 2>&1 || true
npx playwright test tests/e2e --reporter=line | tee -a "../$REPORT" || fail "Playwright failed"

popd >/dev/null

log "QA RUN COMPLETE $(date)"
exit 0
