#!/usr/bin/env sh
set -eu

if [ "$#" -lt 1 ]; then
  echo "usage: $0 BACKUP_FILE [NEW_DATABASE]" >&2
  exit 1
fi

dump_file=$1
NAMESPACE=${NAMESPACE:-brickline}
target_database=${2:-brickline_restore_$(date -u +%Y%m%d%H%M%S)}

if [ ! -f "$dump_file" ]; then
  echo "backup file not found: $dump_file" >&2
  exit 1
fi

case "$target_database" in
  brickline|postgres|template0|template1)
    echo "refusing to restore over $target_database; choose a disposable database" >&2
    exit 1
    ;;
  *[!a-zA-Z0-9_]*)
    echo "database name may only contain letters, numbers, and underscores" >&2
    exit 1
    ;;
esac

started=$(date +%s)
kubectl -n "$NAMESPACE" exec statefulset/brickline-postgres -- \
  createdb -U brickline "$target_database"
kubectl -n "$NAMESPACE" exec -i statefulset/brickline-postgres -- \
  pg_restore -U brickline -d "$target_database" --no-owner < "$dump_file"

counts=$(kubectl -n "$NAMESPACE" exec statefulset/brickline-postgres -- \
  psql -U brickline -d "$target_database" -Atc \
  "select json_build_object('sets',(select count(*) from lego_sets),'events',(select count(*) from release_events),'history',(select count(*) from set_changes));")
elapsed=$(($(date +%s) - started))

echo "restored to $target_database in ${elapsed}s"
echo "counts: $counts"

