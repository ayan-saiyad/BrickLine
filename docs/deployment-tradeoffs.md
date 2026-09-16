# Deployment tradeoffs

## Compose first

Compose is the default because Brickline is one small API, one static frontend, and one database. It is easier to understand, cheaper to run, and has fewer failure modes. The Kubernetes setup exists to practice release and recovery operations with a real application, not because the traffic calls for orchestration.

## Local Kubernetes

The kind cluster has a control plane and two workers, but all three are Docker containers on one machine. It can demonstrate pod replacement, scheduling, rolling releases, and disruption budgets. It cannot demonstrate survival of a host, network, or storage failure.

The included PostgreSQL StatefulSet has one replica and one local PVC. That is useful for disposable backup and restore drills, not production availability or a backup strategy. A hosted deployment should use a managed PostgreSQL service with provider-tested backups and point-in-time recovery.

## Hosted choices left open

The chart does not bundle ingress, certificates, registry credentials, or a cloud load balancer. Those choices are provider-specific. The example hosted values require immutable image digests and a precreated database secret. Terraform only makes sense after choosing a provider, budget, region, DNS name, and teardown plan.

Autoscaling is also off by default. The API has resource requests and an HPA template, but enabling it is only useful after metrics-server is installed and k6 results show a real scaling target. Scaling API pods does not scale PostgreSQL.

