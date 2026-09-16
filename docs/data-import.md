# Data imports

Brickline imports releases from a CSV file or an HTTP URL. The same command is used locally, in Compose, and by the Kubernetes CronJob.

Required columns are `set_number`, `name`, `theme`, `release_date`, `retirement_date`, `status`, `date_confidence`, `source_url`, and `source_name`. Dates use `YYYY-MM-DD`. Retirement dates may be blank. Confidence is `confirmed` or `estimated`.

```sh
python -m app.cli import-data data/lego-releases.csv
```

Imports are transactional and keyed by set number. Running the same file twice updates the existing records instead of duplicating them. A database advisory lock prevents overlapping imports. If a fetch or validation fails, the previous good data stays in place and the failed run is recorded.

The included source is a fixture, not a live LEGO feed. Someone has to update it before the scheduled job can discover a new set. A hosted deployment should point `IMPORT_SOURCE_URL` at a maintained feed and supply any credentials through the environment or a secret.

