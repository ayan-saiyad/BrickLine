#!/usr/bin/env sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
NAMESPACE=${NAMESPACE:-brickline}
RELEASE=${RELEASE:-brickline}
CLUSTER_NAME=${CLUSTER_NAME:-brickline}
IMAGE_TAG=${IMAGE_TAG:-$(git -C "$ROOT" rev-parse --short HEAD)}
LAB_DB_PASSWORD=${LAB_DB_PASSWORD:-brickline-local-only}
MONITORING_ENABLED=${MONITORING_ENABLED:-false}

for command in docker kind kubectl helm python3 curl; do
  if ! command -v "$command" >/dev/null 2>&1; then
    echo "$command is required" >&2
    exit 1
  fi
done

kubectl config use-context "kind-$CLUSTER_NAME" >/dev/null
kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

database_url="postgresql+psycopg://brickline:${LAB_DB_PASSWORD}@brickline-postgres:5432/brickline"
kubectl -n "$NAMESPACE" create secret generic brickline-secrets \
  --from-literal="database-url=$database_url" \
  --from-literal="postgres-password=$LAB_DB_PASSWORD" \
  --dry-run=client -o yaml | kubectl apply -f -

docker build -t "brickline-api:$IMAGE_TAG" "$ROOT/api"
docker build -t "brickline-web:$IMAGE_TAG" "$ROOT/web"
kind load docker-image --name "$CLUSTER_NAME" "brickline-api:$IMAGE_TAG" "brickline-web:$IMAGE_TAG"

kubectl apply -f "$ROOT/deploy/lab-postgres"
kubectl -n "$NAMESPACE" rollout status statefulset/brickline-postgres --timeout=180s

previous_revision=0
if helm -n "$NAMESPACE" history "$RELEASE" >/dev/null 2>&1; then
  previous_revision=$(helm -n "$NAMESPACE" history "$RELEASE" -o json | \
    python3 -c 'import json,sys; rows=json.load(sys.stdin); print(max((int(row["revision"]) for row in rows if row["status"] == "deployed"), default=0))')
fi

rollback() {
  if [ "$previous_revision" -gt 0 ]; then
    "$ROOT/scripts/rollback.sh" "$previous_revision"
  else
    echo "no prior release is available to restore" >&2
  fi
}

if ! helm upgrade --install "$RELEASE" "$ROOT/deploy/helm/brickline" \
  --namespace "$NAMESPACE" \
  --values "$ROOT/deploy/helm/brickline/values-kind.yaml" \
  --set-string "api.image.tag=$IMAGE_TAG" \
  --set-string "web.image.tag=$IMAGE_TAG" \
  --set "monitoring.enabled=$MONITORING_ENABLED" \
  --wait --wait-for-jobs --timeout 5m --history-max 5; then
  kubectl -n "$NAMESPACE" logs "job/${RELEASE}-migrate" --all-containers=true || true
  rollback
  exit 1
fi

if ! "$ROOT/scripts/smoke-test.sh"; then
  rollback
  exit 1
fi

mkdir -p "$ROOT/artifacts/deployments"
result_file="$ROOT/artifacts/deployments/$(date -u +%Y%m%dT%H%M%SZ).txt"
{
  echo "release=$RELEASE"
  echo "revision=$(helm -n "$NAMESPACE" status "$RELEASE" -o json | python3 -c 'import json,sys; print(json.load(sys.stdin)["version"])')"
  echo "image_tag=$IMAGE_TAG"
  echo "result=passed"
} > "$result_file"

echo "deployment passed; result saved to $result_file"
