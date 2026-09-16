# Failure drills

Run these against the disposable kind cluster. Save timestamps and command output under `artifacts/drills/`; do not describe an unmeasured result as a guarantee.

## Replica recovery

1. Port-forward the web service and start `k6 run load/k6.js`.
2. Record the current API pods with `kubectl -n brickline get pods -l app.kubernetes.io/component=api -o wide`.
3. Delete one API pod.
4. Record time to replacement readiness and the k6 error count.

The expected behavior is that the remaining replica serves requests while a replacement starts. A few client errors are still possible during connection changes; kind cannot test host failure.

## Failed rollout

1. Note `helm -n brickline history brickline` and begin a modest k6 run.
2. Set an impossible readiness path in a temporary chart copy or deploy a deliberately broken image tag.
3. Watch `kubectl -n brickline rollout status deployment/brickline-api --timeout=5m` stall.
4. Run `scripts/rollback.sh PREVIOUS_REVISION`.
5. Record rollback time and rerun the smoke test.

## Ingestion resilience

1. Run a manual import twice and compare set, event, and history counts.
2. Point a temporary Job at an unreachable URL and confirm the run is recorded as failed.
3. Check that the API still returns the prior data and its freshness status.
4. Restore the valid source and run it again.

## Backup recovery

1. Run `scripts/backup-db.sh`.
2. Run `scripts/restore-db.sh backups/FILE.dump` to create a separate database.
3. Compare the printed set, event, and history counts with the backup metadata.
4. Record backup age and restore time.

Never delete the working database to prove a restore.

