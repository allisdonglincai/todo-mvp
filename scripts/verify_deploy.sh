#!/usr/bin/env bash
# End-to-end deploy verification for todo-mvp, per v1-contract.md "Verify 用的完整流程".
# Exit 0 = full flow passed. Any failure aborts with a non-zero exit and a clear step label.
set -euo pipefail

IMAGE=todo-mvp
CONTAINER=todo-mvp-verify
PORT=18080
BASE="http://localhost:${PORT}"

TEST_SECRET_KEY="verify-secret-key-not-for-prod"
TEST_ADMIN_USERNAME="verify_admin"
TEST_ADMIN_PASSWORD="verify_admin_pw"
TEST_USERNAME="verify_user"
TEST_PASSWORD="verify_user_pw"
TEST_TODO_TITLE="verify todo item"

COOKIE_DIR="$(mktemp -d)"
USER_JAR="${COOKIE_DIR}/user.txt"
ADMIN_JAR="${COOKIE_DIR}/admin.txt"

cleanup() {
    docker rm -f "$CONTAINER" >/dev/null 2>&1 || true
    rm -rf "$COOKIE_DIR"
}
trap cleanup EXIT

step() { echo "==> $*"; }

# curl helper: POST form data, don't follow redirects, print http_code to stdout.
post() {
    local jar="$1" path="$2" data="$3"
    curl -s -o /dev/null -w '%{http_code}' -c "$jar" -b "$jar" -X POST --data "$data" "${BASE}${path}"
}

get_body() {
    local jar="$1" path="$2"
    curl -s -c "$jar" -b "$jar" "${BASE}${path}"
}

get_code() {
    local jar="$1" path="$2"
    curl -s -o /dev/null -w '%{http_code}' -c "$jar" -b "$jar" "${BASE}${path}"
}

require_code() {
    local got="$1" want="$2" label="$3"
    if [[ "$got" != "$want" ]]; then
        echo "FAIL: $label — expected HTTP $want, got $got"
        exit 1
    fi
}

require_body_contains() {
    local body="$1" needle="$2" label="$3"
    if [[ "$body" != *"$needle"* ]]; then
        echo "FAIL: $label — expected body to contain '$needle'"
        exit 1
    fi
}

require_body_not_contains() {
    local body="$1" needle="$2" label="$3"
    if [[ "$body" == *"$needle"* ]]; then
        echo "FAIL: $label — expected body NOT to contain '$needle'"
        exit 1
    fi
}

step "1/6 docker build -t $IMAGE ."
docker build -t "$IMAGE" .

step "2/6 start container, wait for readiness"
docker rm -f "$CONTAINER" >/dev/null 2>&1 || true
docker run -d --name "$CONTAINER" -p "${PORT}:5000" \
    -e SECRET_KEY="$TEST_SECRET_KEY" \
    -e ADMIN_USERNAME="$TEST_ADMIN_USERNAME" \
    -e ADMIN_PASSWORD="$TEST_ADMIN_PASSWORD" \
    "$IMAGE" >/dev/null

ready=""
for _ in $(seq 1 30); do
    code=$(curl -s -o /dev/null -w '%{http_code}' "${BASE}/" || true)
    if [[ "$code" != "000" ]]; then
        ready=1
        break
    fi
    sleep 1
done
if [[ -z "$ready" ]]; then
    echo "FAIL: container never accepted connections on port $PORT"
    docker logs "$CONTAINER" || true
    exit 1
fi

step "3/6 curl flow: register -> login -> add todo -> cycle status x3 -> logout"

code=$(post "$USER_JAR" "/register" "username=${TEST_USERNAME}&password=${TEST_PASSWORD}")
require_code "$code" "302" "POST /register"

code=$(post "$USER_JAR" "/login" "username=${TEST_USERNAME}&password=${TEST_PASSWORD}")
require_code "$code" "302" "POST /login (test user)"

code=$(get_code "$USER_JAR" "/")
require_code "$code" "200" "GET / after login"

code=$(post "$USER_JAR" "/add" "title=${TEST_TODO_TITLE}")
require_code "$code" "302" "POST /add"

body=$(get_body "$USER_JAR" "/")
require_body_contains "$body" "$TEST_TODO_TITLE" "GET / shows added todo"

todo_id=$(grep -oE '/status/[0-9]+' <<<"$body" | head -1 | grep -oE '[0-9]+')
if [[ -z "$todo_id" ]]; then
    echo "FAIL: could not find a /status/<id> action for the added todo in GET / response"
    exit 1
fi

# pending -> in_progress
code=$(post "$USER_JAR" "/status/${todo_id}" "")
require_code "$code" "302" "POST /status/${todo_id} (1st toggle)"
body=$(get_body "$USER_JAR" "/")
require_body_contains "$body" "in_progress" "status is in_progress after 1st toggle"

# in_progress -> done
code=$(post "$USER_JAR" "/status/${todo_id}" "")
require_code "$code" "302" "POST /status/${todo_id} (2nd toggle)"
body=$(get_body "$USER_JAR" "/")
require_body_contains "$body" "done" "status is done after 2nd toggle"

# done -> pending
code=$(post "$USER_JAR" "/status/${todo_id}" "")
require_code "$code" "302" "POST /status/${todo_id} (3rd toggle)"
body=$(get_body "$USER_JAR" "/")
require_body_not_contains "$body" "in_progress" "status back to pending after 3rd toggle (not in_progress)"
require_body_not_contains "$body" "done" "status back to pending after 3rd toggle (not done)"

code=$(post "$USER_JAR" "/logout" "")
require_code "$code" "302" "POST /logout"

step "4/6 admin login -> GET /admin shows test user + todo"

code=$(post "$ADMIN_JAR" "/login" "username=${TEST_ADMIN_USERNAME}&password=${TEST_ADMIN_PASSWORD}")
require_code "$code" "302" "POST /login (admin)"

admin_body=$(get_body "$ADMIN_JAR" "/admin")
require_body_contains "$admin_body" "$TEST_USERNAME" "GET /admin lists test username"
require_body_contains "$admin_body" "$TEST_TODO_TITLE" "GET /admin lists test todo"

step "5/6 docker restart -> re-login -> confirm data persisted"

docker restart "$CONTAINER" >/dev/null

ready=""
for _ in $(seq 1 30); do
    code=$(curl -s -o /dev/null -w '%{http_code}' "${BASE}/" || true)
    if [[ "$code" != "000" ]]; then
        ready=1
        break
    fi
    sleep 1
done
if [[ -z "$ready" ]]; then
    echo "FAIL: container never came back up after docker restart"
    docker logs "$CONTAINER" || true
    exit 1
fi

RESTART_JAR="${COOKIE_DIR}/user-after-restart.txt"
code=$(post "$RESTART_JAR" "/login" "username=${TEST_USERNAME}&password=${TEST_PASSWORD}")
require_code "$code" "302" "POST /login after restart"

body=$(get_body "$RESTART_JAR" "/")
require_body_contains "$body" "$TEST_TODO_TITLE" "todo still present after restart"

step "6/6 cleanup (handled by trap on exit)"

echo "PASS: full deploy verification flow succeeded"
