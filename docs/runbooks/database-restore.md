# Database restore

The local script always restores into a new database. It refuses the live `brickline` name.

1. Check the backup timestamp, checksum, and row counts in its adjacent JSON file.
2. Run `scripts/restore-db.sh backups/FILE.dump`.
3. Compare its set, event, and history counts to the metadata.
4. Point a temporary API pod at the restored database and sample `/api/sets` before considering a cutover.
5. Record the backup age and measured restore time.

For hosted PostgreSQL, follow the provider's point-in-time recovery procedure instead. Test into an isolated database or instance and make the connection-string change separately. Do not overwrite the only working copy.

