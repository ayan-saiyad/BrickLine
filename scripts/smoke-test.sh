#!/usr/bin/env sh
set -eu

NAMESPACE=${NAMESPACE:-brickline}
RELEASE=${RELEASE:-brickline}
WEB_URL=${WEB_URL:-}
web_forward_pid=""
api_forward_pid=""

cleanup() {
  if [ -n "$web_forward_pid" ]; then kill "$web_forward_pid" 2>/dev/null || true; fi
  if [ -n "$api_forward_pid" ]; then kill "$api_forward_pid" 2>/dev/null || true; fi
}
trap cleanup EXIT INT TERM

if [ -z "$WEB_URL" ]; then
  kubectl -n "$NAMESPACE" port-forward "service/${RELEASE}-web" 18080:80 >/tmp/brickline-web-forward.log 2>&1 &
  web_forward_pid=$!
  kubectl -n "$NAMESPACE" port-forward "service/${RELEASE}-api" 18081:8000 >/tmp/brickline-api-forward.log 2>&1 &
  api_forward_pid=$!
  WEB_URL=http://127.0.0.1:18080
  METRICS_URL=http://127.0.0.1:18081/metrics
else
  METRICS_URL=${METRICS_URL:-}
fi

attempt=0
until curl --fail --silent "$WEB_URL/api/health" >/dev/null; do
  attempt=$((attempt + 1))
  if [ "$attempt" -ge 30 ]; then
    echo "web health check timed out" >&2
    exit 1
  fi
  sleep 1
done

curl --fail --silent "$WEB_URL/" >/dev/null
curl --fail --silent "$WEB_URL/api/sets?page_size=1" | \
  python3 -c 'import json,sys; data=json.load(sys.stdin); assert "items" in data and "total" in data'
if [ -n "$METRICS_URL" ]; then
  curl --fail --silent "$METRICS_URL" | \
    python3 -c 'import sys; assert "brickline_http_requests_total" in sys.stdin.read()'
fi

echo "smoke checks passed for $WEB_URL"

