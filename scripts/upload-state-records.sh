#!/usr/bin/env bash
# Bulk upload stateProfile / stateProcedure / stateDocument records to PDS.
#
# Usage:
#   bash upload-state-records.sh [--in /tmp/state-records] [--only profile|procedure|document]
#                                [--limit N] [--timeout 90]
#
# Skips files already recorded as uploaded in $IN/.uploaded.log.
# Records failures in $IN/.failed.log for retry (just re-run the script).

set -u
IN="/tmp/state-records"
ONLY=""
LIMIT=0
TIMEOUT=90
SLEEP=3

while [[ $# -gt 0 ]]; do
  case "$1" in
    --in) IN="$2"; shift 2 ;;
    --only) ONLY="$2"; shift 2 ;;
    --limit) LIMIT="$2"; shift 2 ;;
    --timeout) TIMEOUT="$2"; shift 2 ;;
    --sleep) SLEEP="$2"; shift 2 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

UPLOADED="$IN/.uploaded.log"
FAILED="$IN/.failed.log"
touch "$UPLOADED" "$FAILED"

kinds="profile procedure document"
[[ -n "$ONLY" ]] && kinds="$ONLY"

ok=0; fail=0; skip=0
for kind in $kinds; do
  dir="$IN/$kind"
  [[ -d "$dir" ]] || continue
  files=("$dir"/*.json)
  for f in "${files[@]}"; do
    [[ -f "$f" ]] || continue
    key="$kind/$(basename "$f")"
    if grep -qxF "$key" "$UPLOADED"; then skip=$((skip+1)); continue; fi
    if (( LIMIT > 0 )) && (( ok + fail >= LIMIT )); then break 2; fi

    AT_TOKEN=$(etzhayyim agent-token --lxm com.atproto.repo.putRecord --ttl 60 2>/dev/null)
    http=$(curl -s -m "$TIMEOUT" -o /tmp/_up_body.json -w '%{http_code}' \
      -X POST https://atproto.etzhayyim.com/xrpc/com.atproto.repo.putRecord \
      -H "Authorization: Bearer $AT_TOKEN" -H "Content-Type: application/json" \
      --data-binary @"$f")

    if [[ "$http" = "200" ]]; then
      echo "$key" >> "$UPLOADED"
      ok=$((ok+1))
      printf '  OK   %s\n' "$key"
    else
      echo "$key http=$http $(head -c 120 /tmp/_up_body.json)" >> "$FAILED"
      fail=$((fail+1))
      printf '  FAIL %s http=%s\n' "$key" "$http"
    fi
    sleep "$SLEEP"
  done
done

echo
echo "Summary: ok=$ok fail=$fail skip=$skip"
echo "Uploaded log: $UPLOADED"
echo "Failed log:   $FAILED"
