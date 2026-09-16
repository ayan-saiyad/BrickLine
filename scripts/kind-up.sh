#!/usr/bin/env sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
CLUSTER_NAME=${CLUSTER_NAME:-brickline}

for command in kind kubectl docker; do
  if ! command -v "$command" >/dev/null 2>&1; then
    echo "$command is required" >&2
    exit 1
  fi
done

for cluster in $(kind get clusters 2>/dev/null); do
  if [ "$cluster" = "$CLUSTER_NAME" ]; then
    echo "kind cluster $CLUSTER_NAME already exists"
    kubectl cluster-info --context "kind-$CLUSTER_NAME"
    exit 0
  fi
done

kind create cluster --name "$CLUSTER_NAME" --config "$ROOT/deploy/kind/cluster.yaml" --wait 120s
kubectl cluster-info --context "kind-$CLUSTER_NAME"

