#!/usr/bin/env python3
import json
import argparse
import re
import sys
import urllib.request
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WASM_ROOT = ROOT / "wasm"
ADM2_API = "https://www.geoboundaries.org/api/current/gbOpen/ALL/ADM2/"


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "unknown"


def existing_adm2_counts() -> dict[str, int]:
    counts: dict[str, int] = {}
    if not WASM_ROOT.exists():
        return counts
    for path in WASM_ROOT.iterdir():
        if not path.is_dir():
            continue
        m = re.search(r"org-gov-([a-z0-9]{3})-dst-", path.name)
        if not m:
            continue
        iso = m.group(1).upper()
        counts[iso] = counts.get(iso, 0) + 1
    return counts


def load_adm2_catalog() -> list[dict]:
    with urllib.request.urlopen(ADM2_API) as resp:
        return json.load(resp)


def fetch_first_feature(meta: dict) -> dict:
    with urllib.request.urlopen(meta["simplifiedGeometryGeoJSON"]) as resp:
        gj = json.load(resp)
    features = gj.get("features", [])
    if not features:
        raise RuntimeError(f"No features found for {meta['boundaryISO']}")
    props = features[0].get("properties", {})
    return {
        "shapeName": props.get("shapeName", "unknown"),
        "shapeID": props.get("shapeID", "unknown"),
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--top-n", type=int, default=10)
    p.add_argument("--output", default="260303-adm2-pilot-10-targets.jsonl")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    out_path = ROOT / "tmp" / args.output

    have_counts = existing_adm2_counts()
    catalog = load_adm2_catalog()

    rows = []
    for item in catalog:
        iso = item["boundaryISO"].upper()
        denom = int(item.get("admUnitCount") or 0)
        have = have_counts.get(iso, 0)
        gap = denom - have
        rows.append(
            {
                "iso": iso,
                "country": item["boundaryName"],
                "denom": denom,
                "have": have,
                "gap": gap,
                "meta": item,
            }
        )

    rows.sort(key=lambda x: (x["gap"], x["denom"]), reverse=True)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        emitted = 0
        for row in rows:
            if emitted >= args.top_n:
                break
            feature = fetch_first_feature(row["meta"])
            iso_l = row["iso"].lower()
            local_name = slugify(feature["shapeName"])
            code_tail = re.sub(r"[^a-z0-9]", "", feature["shapeID"].lower())[-8:] or "00000000"
            suggestion = f"org-gov-{iso_l}-dst-{code_tail}-{local_name}"
            candidate_dir = WASM_ROOT / f"etzhayyim-performer-sys-etzhayyim-actors-pba7d22f-{suggestion}"
            if candidate_dir.exists():
                continue
            emitted += 1
            row_out = {
                "rank": emitted,
                "iso": row["iso"],
                "country": row["country"],
                "adm2_total": row["denom"],
                "existing_adm2": row["have"],
                "gap": row["gap"],
                "pilot_shape_name": feature["shapeName"],
                "pilot_shape_id": feature["shapeID"],
                "suggested_slug": suggestion,
            }
            f.write(json.dumps(row_out, ensure_ascii=False) + "\n")

    count = sum(1 for _ in out_path.open("r", encoding="utf-8"))
    print(str(out_path))
    print(f"selected={count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
