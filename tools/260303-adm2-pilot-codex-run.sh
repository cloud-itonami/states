#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TARGETS="$ROOT/tmp/260303-adm2-pilot-10-targets.jsonl"
OUT_DIR="$ROOT/reports/260303-adm2-pilot-codex-output"
SUMMARY="$ROOT/reports/260303-adm2-pilot-10-report.md"
MODEL="${MODEL:-gpt-5.3-spark}"
PARALLEL="${PARALLEL:-4}"

mkdir -p "$OUT_DIR"

if [[ ! -f "$TARGETS" ]]; then
  echo "targets file not found: $TARGETS" >&2
  echo "run: tools/260303-adm2-pilot-select.py" >&2
  exit 1
fi

run_one() {
  local payload="$1"

  local rank iso country adm2_total existing_adm2 gap shape_name shape_id suggested_slug
  rank="$(jq -r '.rank' <<<"$payload")"
  iso="$(jq -r '.iso' <<<"$payload")"
  country="$(jq -r '.country' <<<"$payload")"
  adm2_total="$(jq -r '.adm2_total' <<<"$payload")"
  existing_adm2="$(jq -r '.existing_adm2' <<<"$payload")"
  gap="$(jq -r '.gap' <<<"$payload")"
  shape_name="$(jq -r '.pilot_shape_name' <<<"$payload")"
  shape_id="$(jq -r '.pilot_shape_id' <<<"$payload")"
  suggested_slug="$(jq -r '.suggested_slug' <<<"$payload")"

  local outfile="$OUT_DIR/${rank}-${iso}-${suggested_slug}.md"
  local logfile="$OUT_DIR/${rank}-${iso}-${suggested_slug}.log"

  local prompt
  prompt=$(cat <<EOF
You are implementing an ADM2 pilot item for etzhayyim-project-states.
Return a compact implementation blueprint only.

Input:
- rank: ${rank}
- country: ${country} (${iso})
- adm2_total: ${adm2_total}
- existing_adm2_in_repo: ${existing_adm2}
- gap: ${gap}
- target_shape_name: ${shape_name}
- target_shape_id: ${shape_id}
- suggested_slug: ${suggested_slug}

Constraints:
- spinapp namespace must be spinkube
- Edge route namespace must be edge-router-performers
- image must use ghcr.io/etzhayyim/*
- metadata.name and image stem must match
- endpoint convention: https://{nanoid}.etzhayyim.com/api/grpc

Output sections:
1) slug validation
2) required files list
3) k8s manifest skeleton names
4) quality gates checklist
5) estimated risk
EOF
)

  {
    echo "start=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    codex exec "$prompt" \
      -m "$MODEL" \
      --sandbox read-only \
      --skip-git-repo-check \
      --ephemeral \
      -C "$ROOT" \
      -o "$outfile"
    echo "end=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "status=ok"
  } >"$logfile" 2>&1 || {
    echo "status=ng" >>"$logfile"
  }
}

export ROOT OUT_DIR MODEL
export -f run_one

while IFS= read -r payload; do
  run_one "$payload" &
  while [[ "$(jobs -rp | wc -l | tr -d ' ')" -ge "$PARALLEL" ]]; do
    sleep 0.2
  done
done <"$TARGETS"
wait

ROOT_FOR_PY="$ROOT" MODEL_FOR_PY="$MODEL" PARALLEL_FOR_PY="$PARALLEL" python3 - <<'PY'
import json
import os
from pathlib import Path

root = Path(os.environ["ROOT_FOR_PY"])
model = os.environ["MODEL_FOR_PY"]
parallel = os.environ["PARALLEL_FOR_PY"]
out_dir = root / "reports" / "260303-adm2-pilot-codex-output"
summary = root / "reports" / "260303-adm2-pilot-10-report.md"
targets_path = root / "tmp" / "260303-adm2-pilot-10-targets.jsonl"

targets = [json.loads(line) for line in targets_path.read_text(encoding="utf-8").splitlines() if line.strip()]

rows = []
ok = 0
ng = 0
for t in targets:
    stem = f"{t['rank']}-{t['iso']}-{t['suggested_slug']}"
    md = out_dir / f"{stem}.md"
    log = out_dir / f"{stem}.log"
    success = md.exists() and md.stat().st_size > 0
    if success:
        ok += 1
    else:
        ng += 1
    rows.append((t, success, md, log))

lines = []
lines.append("# ADM2 Pilot Verification (10 items)")
lines.append("")
lines.append("- Date: 2026-03-03")
lines.append(f"- Model: {model} (codex exec)")
lines.append(f"- Parallel workers: {parallel}")
lines.append(f"- Total: {len(targets)}")
lines.append(f"- Success: {ok}")
lines.append(f"- Failed: {ng}")
lines.append("")
lines.append("## Results")
for t, success, md, log in rows:
    status = "OK" if success else "NG"
    lines.append(
        f"- [{status}] rank={t['rank']} iso={t['iso']} country={t['country']} "
        f"target={t['pilot_shape_name']} slug={t['suggested_slug']} "
        f"output={md.name} log={log.name}"
    )

summary.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(summary)
PY
