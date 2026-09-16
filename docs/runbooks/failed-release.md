# Failed release

1. Stop new release activity and get `helm -n brickline status brickline` plus Deployment events.
2. Read the migration hook logs with `kubectl -n brickline logs job/brickline-migrate`. If the Job did not start, inspect its pod events.
3. Find the last healthy revision in `helm -n brickline history brickline`.
4. Run `scripts/rollback.sh REVISION`. The script waits for both rollouts and runs smoke checks.
5. Confirm the home page and `/api/health`, then note the failure and recovery times.

Do not try to fix a release by repeatedly deleting pods. If a migration completed, confirm it was backward-compatible before rolling the application back.

