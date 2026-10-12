#!/usr/bin/env bash
set -euo pipefail

PORT="${PORT:-3000}"
BASE_URL="http://127.0.0.1:${PORT}"
LOG_FILE="${TMPDIR:-/tmp}/sports-data-visualizer-next.log"

npm start -- --hostname 127.0.0.1 --port "${PORT}" >"${LOG_FILE}" 2>&1 &
APP_PID=$!

cleanup() {
  kill "${APP_PID}" 2>/dev/null || true
}
trap cleanup EXIT

for _ in {1..30}; do
  if curl --fail --silent "${BASE_URL}/en" >/dev/null; then
    break
  fi
  sleep 1
done

assert_status() {
  local path="$1"
  local expected="$2"
  local actual

  actual="$(curl --silent --output /dev/null --write-out "%{http_code}" "${BASE_URL}${path}")"
  if [[ "${actual}" != "${expected}" ]]; then
    echo "Expected ${path} to return ${expected}, got ${actual}"
    exit 1
  fi
}

assert_redirect() {
  local expected_path="$1"
  shift
  local location

  location="$(curl --silent --output /dev/null --dump-header - "$@" "${BASE_URL}/" |
    awk 'BEGIN{IGNORECASE=1} /^location:/ {gsub("\r", ""); print $2}')"

  if [[ "${location}" != "${expected_path}" && "${location}" != "${BASE_URL}${expected_path}" ]]; then
    echo "Expected redirect to ${expected_path} (relative or absolute), got ${location:-<none>}"
    exit 1
  fi
}

assert_status "/en" "200"
assert_status "/br" "200"
assert_status "/en/methodology" "307"
assert_status "/br/methodology" "307"
assert_status "/fr/methodology" "404"
assert_status "/pt-BR" "404"
assert_status "/fr" "404"

assert_redirect "/br" --header "Accept-Language: pt-BR,pt;q=0.9,en;q=0.5"
assert_redirect "/en" --header "Accept-Language: de-DE,de;q=0.9"
assert_redirect "/en"   --header "Accept-Language: pt-BR,pt;q=0.9"   --header "Cookie: football-visualized-locale=en"
assert_redirect "/br"   --header "Accept-Language: en-US,en;q=0.9"   --header "Cookie: football-visualized-locale=pt-BR"
assert_redirect "/br"   --header "Accept-Language: pt-BR,pt;q=0.9"   --header "Cookie: football-visualized-locale=invalid"

echo "Localization smoke checks passed."
