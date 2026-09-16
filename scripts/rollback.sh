#!/usr/bin/env sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
NAMESPACE=${NAMESPACE:-brickline}
RELEASE=${RELEASE:-brickline}
REVISION=${1:-0}

echo "rolling $RELEASE back to revision $REVISION"
helm -n "$NAMESPACE" rollback "$RELEASE" "$REVISION" --wait --timeout 5m
kubectl -n "$NAMESPACE" rollout status "deployment/${RELEASE}-api" --timeout=180s
kubectl -n "$NAMESPACE" rollout status "deployment/${RELEASE}-web" --timeout=180s
"$ROOT/scripts/smoke-test.sh"

