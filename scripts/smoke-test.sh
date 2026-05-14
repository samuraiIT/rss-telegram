#!/bin/bash
# smoke-test.sh — AI Dev Samurai | Canon C11 Pre-Deploy Check
set -e
PASS=0; FAIL=0
pass() { echo "  ✅ $1"; ((PASS++)); }
fail() { echo "  ❌ $1"; ((FAIL++)); }

echo "=== ai-telegram-parser smoke test ==="
echo "--- Canon C3: .secrets.env not in git"
git ls-files .secrets.env 2>/dev/null | grep -q .secrets.env && fail ".secrets.env IN GIT!" || pass "C3 OK"

echo "--- Canon C9: sanitize_user_input present"
grep -qr 'sanitize_user_input' security.py && pass "C9 OK" || fail "sanitize_user_input MISSING"

echo "--- Canon C1: no direct api.openai.com / api.anthropic.com calls"
VIOLATIONS=$(grep -rn 'api\.openai\.com\|api\.anthropic\.com' . --include='*.py' | grep -v '.bak' | wc -l)
[ "$VIOLATIONS" -eq 0 ] && pass "C1 OK" || fail "C1 VIOLATION: $VIOLATIONS direct API calls found"

echo "--- Handlers present"
[ -f tgapi/handlers/guest_handler.py ]    && pass "guest_handler.py"    || fail "guest_handler.py MISSING"
[ -f tgapi/handlers/bot2bot.py ]          && pass "bot2bot.py"          || fail "bot2bot.py MISSING"
[ -f tgapi/handlers/streaming_profiler.py ] && pass "streaming_profiler.py" || fail "streaming_profiler.py MISSING"
[ -f tgapi/automation_responder.py ]      && pass "automation_responder.py" || fail "automation_responder.py MISSING"

echo "--- SQL migration"
[ -f sql/init.sql ] && grep -q 'dialogue_history' sql/init.sql && pass "dialogue_history migration OK" || fail "dialogue_history migration MISSING"

echo ""
echo "PASS=$PASS  FAIL=$FAIL"
[ "$FAIL" -eq 0 ] && echo "✅ READY — deploy allowed" && exit 0 || echo "🚫 FIX before deploy" && exit 1
