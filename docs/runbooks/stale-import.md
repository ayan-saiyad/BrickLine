# Stale import

1. Check `/api/imports/status` and the latest CronJob/Job status.
2. Read the failed Job logs and note whether the failure is download, validation, lock contention, or database access.
3. Confirm the API is still serving the last successful data and that the freshness warning is accurate.
4. Fix the source or credential. Never paste provider credentials into a Job manifest.
5. Create one Job from the CronJob and follow its logs.
6. Verify a new successful run, expected counts, and the Prometheus freshness gauge.

An active scheduled Job and a manually created Job can overlap; the database lock is the final guard.

