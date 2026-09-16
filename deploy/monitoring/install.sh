#!/usr/bin/env sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
CHART_VERSION=91.4.1

helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update prometheus-community
helm upgrade --install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --version "$CHART_VERSION" \
  --values "$ROOT/deploy/monitoring/values.yaml" \
  --wait --timeout 10m

kubectl apply -f "$ROOT/deploy/monitoring/rules.yaml"
kubectl apply -f "$ROOT/deploy/monitoring/dashboard.yaml"

echo "monitoring installed; redeploy with MONITORING_ENABLED=true to add the ServiceMonitor"

