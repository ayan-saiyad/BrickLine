# Kubernetes lab

Kubernetes is an optional operations lab. The application does not need it at this scale; Compose remains the shorter path for local use.

## Requirements

The tested tool versions are kind 0.33.0, kubectl 1.37.0, and Helm 4.3.0. The kind node image is pinned by digest. Docker should have at least 4 CPUs and 6 GB of memory available. The app usually fits well below 1 GB; the optional monitoring stack needs roughly another 2 GB and takes longer to start.

Create the three-node local cluster and deploy:

```sh
scripts/kind-up.sh
scripts/deploy-kind.sh
```

The deploy script builds images tagged with the current commit, loads them into kind, creates the disposable lab database, runs the migration hook, waits for both rollouts, and performs HTTP smoke checks. Results are written under the ignored `artifacts/deployments/` directory.

Open the application:

```sh
kubectl -n brickline port-forward service/brickline-web 3000:80
```

Then visit <http://localhost:3000>. There is deliberately no ingress controller in the local lab.

Load the fixture data manually:

```sh
kubectl -n brickline create job --from=cronjob/brickline-import import-manual-$(date +%s)
kubectl -n brickline logs -f job/import-manual-REPLACE_WITH_NAME
```

The CronJob runs at 06:00 in `America/Chicago`, forbids scheduler overlap, and keeps failed Jobs for inspection. Kubernetes scheduling is not an exactly-once guarantee, so the importer also uses a PostgreSQL advisory lock and idempotent upserts.

## Monitoring

Install the pinned `kube-prometheus-stack` 91.4.1 chart, then turn on Brickline's `ServiceMonitor`:

```sh
deploy/monitoring/install.sh
MONITORING_ENABLED=true scripts/deploy-kind.sh
```

Open the local UIs:

```sh
kubectl -n monitoring port-forward service/monitoring-grafana 3001:80
kubectl -n monitoring port-forward service/monitoring-kube-prometheus-prometheus 9090:9090
```

Grafana's lab login is `admin` / `brickline-lab-only`. The Brickline operations dashboard covers request volume, p95 latency, error ratio, healthy replicas, restarts, last successful import, rejected rows, and data age. Database-derived import gauges are reduced with `max by (source)` so replicas do not double-count one logical value.

The lab alerts are examples, not service guarantees. Alertmanager and external delivery are disabled. Check rule state in Prometheus before claiming an alert fired.

## Images and secrets

Local images stay inside kind. Hosted deployments should push both images, fill in `values-hosted.example.yaml` with immutable digests, and use an external PostgreSQL service. Create the named secret before installing the chart:

```sh
kubectl -n brickline create secret generic brickline-production-secrets \
  --from-literal=database-url='postgresql+psycopg://USER:PASSWORD@HOST:5432/brickline'
```

Do not commit the rendered Secret or a real values file. HTTPS and ingress depend on the chosen provider and are intentionally outside this local chart.

## Release behavior

Both Deployments use `maxUnavailable: 0`, `maxSurge: 1`, startup/readiness/liveness probes, graceful termination, requests and limits, read-only root filesystems, and no mounted service account token. Two replicas and a disruption budget help with a pod or voluntary node disruption; they do not protect this single host from failing.

The migration Job is a pre-install/pre-upgrade Helm hook. A failed hook or rollout leaves its logs available. `deploy-kind.sh` restores the exact previous Helm revision and reruns smoke checks when an upgrade or post-deploy check fails. A Kubernetes Deployment does not roll itself back.

Application rollback cannot undo a database migration. Keep schema changes additive and compatible with both the old and new application during this exercise.
