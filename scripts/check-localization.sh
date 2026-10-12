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

for route in en br nl es de; do
  assert_status "/${route}" "200"
  assert_status "/${route}/methodology" "307"
  locale="${route}"
  [[ "${route}" != "br" ]] || locale="pt-BR"
  html="$(curl --fail --silent "${BASE_URL}/${route}")"
  [[ "${html}" == *"<html lang=\"${locale}\""* ]] || { echo "Incorrect document language: ${route}"; exit 1; }
  location="$(curl --silent --output /dev/null --dump-header - "${BASE_URL}/${route}/methodology" | awk 'BEGIN{IGNORECASE=1} /^location:/ {gsub("\r", ""); print $2}')"
  [[ "${location}" == "/${route}#methodology" || "${location}" == "${BASE_URL}/${route}#methodology" ]] || { echo "Incorrect methodology redirect: ${route}"; exit 1; }
  assert_redirect "/${route}" --header "Accept-Language: fr-FR" --header "Cookie: football-visualized-locale=${locale}"
  # A direct route wins over saved/browser preferences.
  direct="$(curl --fail --silent --header 'Cookie: football-visualized-locale=en' --header 'Accept-Language: en' "${BASE_URL}/${route}")"
  [[ "${direct}" == *"<html lang=\"${locale}\""* ]] || exit 1
done
assert_status "/fr/methodology" "404"
assert_status "/pt-BR" "404"
assert_status "/fr" "404"

assert_redirect "/br" --header "Accept-Language: pt-BR,pt;q=0.9,en;q=0.5"
assert_redirect "/de" --header "Accept-Language: de-DE,de;q=0.9"
assert_redirect "/nl" --header "Accept-Language: nl-NL,nl;q=0.9"
assert_redirect "/nl" --header "Accept-Language: nl-BE"
assert_redirect "/es" --header "Accept-Language: es-MX,es;q=0.9"
assert_redirect "/es" --header "Accept-Language: de;q=0.3,es;q=0.9"
assert_redirect "/en" --header "Accept-Language: fr-FR"
assert_redirect "/en" --header "Accept-Language: *"
assert_redirect "/en" --header "Accept-Language: not_a_tag"
assert_redirect "/en" --header "Accept-Language:"
assert_redirect "/en"   --header "Accept-Language: pt-BR,pt;q=0.9"   --header "Cookie: football-visualized-locale=en"
assert_redirect "/br"   --header "Accept-Language: en-US,en;q=0.9"   --header "Cookie: football-visualized-locale=pt-BR"
assert_redirect "/br"   --header "Accept-Language: pt-BR,pt;q=0.9"   --header "Cookie: football-visualized-locale=invalid"

python3 scripts/check_portfolio_metadata.py --base-url "${BASE_URL}"

echo "Localization smoke checks passed."
