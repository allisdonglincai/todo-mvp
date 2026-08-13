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

# curl helpers: never let a connection blip kill the script via set -e on the
# assignment — a failure here should surface as a labeled FAIL from
# require_code/require_body_contains below, not an unlabeled abort.
post() {
    local jar="$1" path="$2" data="$3" code
    code=$(curl -s -o /dev/null -w '%{http_code}' -c "$jar" -b "$jar" -X POST --data "$data" "${BASE}${path}") || code="000"
    echo "$code"
}

get_body() {
    local jar="$1" path="$2"
    curl -s -c "$jar" -b "$jar" "${BASE}${path}" || true
}

get_code() {
    local jar="$1" path="$2" code
    code=$(curl -s -o /dev/null -w '%{http_code}' -c "$jar" -b "$jar" "${BASE}${path}") || code="000"
    echo "$code"
}

# Read state directly from the container's sqlite db instead of grepping
# HTML, since templates/ belongs to a different lane and its markup (button
# labels, CSS classes, legends) can legitimately contain "pending"/"done"/
# "in_progress" outside of the actual status value.
db_todo_id() {
    docker exec "$CONTAINER" python -c \
        "import sqlite3,sys; row=sqlite3.connect('/app/todo.db').execute('select id from todos where title=? order by id desc limit 1', (sys.argv[1],)).fetchone(); print(row[0] if row else '')" \
        "$TEST_TODO_TITLE" 2>/dev/null || true
}

db_status() {
    local id="$1"
    docker exec "$CONTAINER" python -c \
        "import sqlite3,sys; row=sqlite3.connect('/app/todo.db').execute('select status from todos where id=?', (int(sys.argv[1]),)).fetchone(); print(row[0] if row else '')" \
        "$id" 2>/dev/null || echo "DB_QUERY_ERROR"
}

require_code() {
    local got="$1" want="$2" label="$3"
    if [[ "$got" != "$want" ]]; then
        echo "FAIL: $label — expected HTTP $want, got $got"
        exit 1
    fi
}

require_eq() {
    local got="$1" want="$2" label="$3"
    if [[ "$got" != "$want" ]]; then
        echo "FAIL: $label — expected '$want', got '$got'"
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

wait_ready() {
    local label="$1" ready=""
    for _ in $(seq 1 30); do
        local code
        code=$(curl -s -o /dev/null -w '%{http_code}' "${BASE}/" 2>/dev/null) || code="000"
        if [[ "$code" != "000" ]]; then
            ready=1
            break
        fi
        sleep 1
    done
    if [[ -z "$ready" ]]; then
        echo "FAIL: $label — container never accepted connections on port $PORT"
        docker logs "$CONTAINER" || true
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
wait_ready "startup"

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

todo_id=$(db_todo_id)
if [[ ! "$todo_id" =~ ^[0-9]+$ ]]; then
    echo "FAIL: could not find the added todo's id via sqlite (title='${TEST_TODO_TITLE}')"
    exit 1
fi

# pending -> in_progress
code=$(post "$USER_JAR" "/status/${todo_id}" "")
require_code "$code" "302" "POST /status/${todo_id} (1st toggle)"
require_eq "$(db_status "$todo_id")" "in_progress" "status after 1st toggle"

# in_progress -> done
code=$(post "$USER_JAR" "/status/${todo_id}" "")
require_code "$code" "302" "POST /status/${todo_id} (2nd toggle)"
require_eq "$(db_status "$todo_id")" "done" "status after 2nd toggle"

# done -> pending
code=$(post "$USER_JAR" "/status/${todo_id}" "")
require_code "$code" "302" "POST /status/${todo_id} (3rd toggle)"
require_eq "$(db_status "$todo_id")" "pending" "status after 3rd toggle"

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
wait_ready "restart"

RESTART_JAR="${COOKIE_DIR}/user-after-restart.txt"
code=$(post "$RESTART_JAR" "/login" "username=${TEST_USERNAME}&password=${TEST_PASSWORD}")
require_code "$code" "302" "POST /login after restart"

body=$(get_body "$RESTART_JAR" "/")
require_body_contains "$body" "$TEST_TODO_TITLE" "todo still present after restart"

step "6/6 cleanup (handled by trap on exit)"

echo "PASS: full deploy verification flow succeeded"
