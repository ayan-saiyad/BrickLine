# Local lab results

These checks were run on September 16, 2026, in a three-node kind cluster on one laptop. They show that the deployment and recovery scripts work; they are not evidence of host-level high availability or production capacity.

## Data jobs

The fixture import was run twice against PostgreSQL. Both runs succeeded, and the second run left the database at 12 sets, 24 events, and 12 history entries. An intentionally unreachable source then exhausted the Job backoff limit and recorded three failed attempts without changing those counts.

The backup script produced a 16,015-byte custom-format dump with SHA-256 `8b34546d2179490fa697395cd66644ffce338359473317e1349953803a15b817`. Restoring it to a separate database took one second and reproduced the same 12 sets, 24 events, and 12 history entries.

## Replica recovery

A 35-second k6 run held eight virtual users against the API while one of its two pods was deleted. The run completed 539 requests with no HTTP failures and a p95 request duration of 55.94 ms. Kubernetes made the replacement pod ready in seven seconds; the surviving replica continued serving during that window.

This is a small functional recovery check on a local machine, not a benchmark.

## Rollout and rollback

Revision 3 was used as the healthy baseline. Revision 4 deliberately pointed the readiness probe at a missing path. The upgrade timed out after 51 seconds, while the two old replicas still answered the health endpoint. Rolling back to revision 3 created revision 5, restored both Deployments, and passed the smoke checks in two seconds.

The first cluster bring-up also exposed two real packaging problems: the disposable PostgreSQL container needed permission to initialize its data directory, and the stock Caddy binary carried a file capability that conflicted with the pod security context. The manifests now account for both.

## Reproduce the checks

The commands and expected observations are in [failure-drills.md](failure-drills.md). Deployment result files, database dumps, and other local evidence are ignored by Git so a normal test run does not dirty the repository.
