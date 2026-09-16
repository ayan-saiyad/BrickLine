#!/usr/bin/env sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
NAMESPACE=${NAMESPACE:-brickline}
timestamp=$(date -u +%Y%m%dT%H%M%SZ)
backup_dir=${BACKUP_DIR:-$ROOT/backups}
dump_file="$backup_dir/brickline-$timestamp.dump"
metadata_file="$dump_file.json"

mkdir -p "$backup_dir"
kubectl -n "$NAMESPACE" exec statefulset/brickline-postgres -- \
  pg_dump -U brickline -d brickline -Fc > "$dump_file"

counts=$(kubectl -n "$NAMESPACE" exec statefulset/brickline-postgres -- \
  psql -U brickline -d brickline -Atc \
  "select json_build_object('sets',(select count(*) from lego_sets),'events',(select count(*) from release_events),'history',(select count(*) from set_changes));")

python3 - "$dump_file" "$metadata_file" "$counts" <<'PY'
import hashlib
import json
import pathlib
import sys
from datetime import UTC, datetime

dump = pathlib.Path(sys.argv[1])
metadata = {
    "created_at": datetime.now(UTC).isoformat(),
    "file": dump.name,
    "bytes": dump.stat().st_size,
    "sha256": hashlib.sha256(dump.read_bytes()).hexdigest(),
    "counts": json.loads(sys.argv[3]),
}
pathlib.Path(sys.argv[2]).write_text(json.dumps(metadata, indent=2) + "\n")
PY

echo "backup saved to $dump_file"

