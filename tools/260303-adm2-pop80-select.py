#!/usr/bin/env python3
import argparse
import json
import re
import sys
import urllib.request
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WASM_ROOT = ROOT / "wasm"
ADM2_API = "https://www.geoboundaries.org/api/current/gbOpen/ALL/ADM2/"
WB_POP_API = "https://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL?format=json&per_page=20000"


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


def load_worldbank_population() -> tuple[dict[str, int], str]:
    with urllib.request.urlopen(WB_POP_API) as resp:
        body = json.load(resp)

    rows = body[1] if isinstance(body, list) and len(body) > 1 else []
    latest_by_iso: dict[str, tuple[int, int]] = {}
    max_year = 0
    for row in rows:
        iso = (row.get("countryiso3code") or "").upper()
        value = row.get("value")
        date = row.get("date")
        if not iso or iso == "" or iso == "WLD":
            continue
        if value is None:
            continue
        try:
            year = int(date)
            pop = int(value)
        except (TypeError, ValueError):
            continue
        max_year = max(max_year, year)
        old = latest_by_iso.get(iso)
        if old is None or year > old[0]:
            latest_by_iso[iso] = (year, pop)

    pop_map = {iso: year_pop[1] for iso, year_pop in latest_by_iso.items()}
    return pop_map, str(max_year)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--basis", choices=["population", "adm2"], default="population")
    p.add_argument("--threshold", type=float, default=0.8)
    p.add_argument("--target-jsonl", default="260303-adm2-pop80-targets.jsonl")
    p.add_argument("--report-md", default="260303-adm2-pop80-coverage-report.md")
    p.add_argument("--pilot-top-n", type=int, default=0)
    p.add_argument("--pilot-jsonl", default="260303-adm2-pop80-pilot-10-targets.jsonl")
    return p.parse_args()


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "unknown"


def fetch_candidate_feature(meta: dict, iso_l: str) -> dict | None:
    with urllib.request.urlopen(meta["simplifiedGeometryGeoJSON"]) as resp:
        gj = json.load(resp)
    features = gj.get("features", [])
    if not features:
        raise RuntimeError(f"No features found for {meta.get('boundaryISO', 'unknown')}")
    for feat in features:
        props = feat.get("properties", {})
        shape_name = props.get("shapeName", "unknown")
        shape_id = props.get("shapeID", "unknown")
        tail = re.sub(r"[^a-z0-9]", "", str(shape_id).lower())[-8:] or "00000000"
        local_name = slugify(str(shape_name))
        suggested_slug = f"org-gov-{iso_l}-dst-{tail}-{local_name}"
        candidate_dir = WASM_ROOT / f"etzhayyim-performer-sys-etzhayyim-actors-pba7d22f-{suggested_slug}"
        if candidate_dir.exists():
            continue
        return {
            "shapeName": shape_name,
            "shapeID": shape_id,
            "suggested_slug": suggested_slug,
        }
    return None


def main() -> int:
    args = parse_args()
    if args.threshold <= 0 or args.threshold > 1:
        raise SystemExit("--threshold must be in (0, 1]")

    have_counts = existing_adm2_counts()
    catalog = load_adm2_catalog()
    pop_map: dict[str, int] = {}
    pop_year = "n/a"
    if args.basis == "population":
        pop_map, pop_year = load_worldbank_population()

    meta_by_iso = {}
    countries = []
    for item in catalog:
        iso = (item.get("boundaryISO") or "").upper()
        if not iso:
            continue
        meta_by_iso[iso] = item
        adm2_total = int(item.get("admUnitCount") or 0)
        pop = pop_map.get(iso)
        if args.basis == "population" and pop is None:
            continue
        have = have_counts.get(iso, 0)
        countries.append(
            {
                "iso": iso,
                "country": item.get("boundaryName") or iso,
                "population": pop,
                "adm2_total": adm2_total,
                "existing_adm2": have,
                "adm2_gap": max(adm2_total - have, 0),
                "adm2_coverage": (have / adm2_total) if adm2_total > 0 else 0.0,
            }
        )

    if args.basis == "population":
        countries.sort(key=lambda x: int(x["population"] or 0), reverse=True)
        basis_total = sum(int(c["population"] or 0) for c in countries)
        threshold_value = int(basis_total * args.threshold)
    else:
        countries.sort(key=lambda x: x["adm2_total"], reverse=True)
        basis_total = sum(c["adm2_total"] for c in countries)
        threshold_value = int(basis_total * args.threshold)

    selected = []
    running = 0
    for idx, c in enumerate(countries, start=1):
        running += int(c["population"] or 0) if args.basis == "population" else c["adm2_total"]
        row = dict(c)
        row["rank"] = idx
        row["cumulative_share"] = running / basis_total if basis_total else 0
        selected.append(row)
        if running >= threshold_value:
            break

    selected_adm2_total = sum(c["adm2_total"] for c in selected)
    selected_adm2_have = sum(c["existing_adm2"] for c in selected)
    selected_adm2_gap = sum(c["adm2_gap"] for c in selected)

    jsonl_path = ROOT / "tmp" / args.target_jsonl
    report_path = ROOT / "reports" / args.report_md
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with jsonl_path.open("w", encoding="utf-8") as f:
        for row in selected:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    pilot_path = None
    if args.pilot_top_n > 0:
        pilot_path = ROOT / "tmp" / args.pilot_jsonl
        pilot_path.parent.mkdir(parents=True, exist_ok=True)
        emitted = 0
        with pilot_path.open("w", encoding="utf-8") as f:
            for row in selected:
                if emitted >= args.pilot_top_n:
                    break
                if row["adm2_gap"] <= 0:
                    continue
                meta = meta_by_iso.get(row["iso"])
                if not meta:
                    continue
                feature = fetch_candidate_feature(meta, row["iso"].lower())
                if feature is None:
                    continue
                shape_name = feature["shapeName"]
                shape_id = feature["shapeID"]
                suggested_slug = feature["suggested_slug"]
                emitted += 1
                pilot = {
                    "rank": emitted,
                    "iso": row["iso"],
                    "country": row["country"],
                    "adm2_total": row["adm2_total"],
                    "existing_adm2": row["existing_adm2"],
                    "gap": row["adm2_gap"],
                    "pilot_shape_name": shape_name,
                    "pilot_shape_id": shape_id,
                    "suggested_slug": suggested_slug,
                    "basis": args.basis,
                    "basis_rank": row["rank"],
                    "population": row["population"],
                }
                f.write(json.dumps(pilot, ensure_ascii=False) + "\n")

    now = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
    basis_label = "Population" if args.basis == "population" else "Unit"
    lines = []
    lines.append(f"# ADM2 {basis_label} 80% Coverage Target Report")
    lines.append("")
    lines.append(f"- Generated: {now}")
    lines.append("- ADM2 source: geoBoundaries `gbOpen/ALL/ADM2`")
    if args.basis == "population":
        lines.append("- Population source: World Bank `SP.POP.TOTL`")
        lines.append(f"- Population reference year (max seen): `{pop_year}`")
    else:
        lines.append("- Basis source: geoBoundaries `admUnitCount`")
    lines.append(f"- Threshold: `{args.threshold * 100:.1f}%`")
    lines.append(f"- Basis: `{args.basis}`")
    lines.append("")
    lines.append("## Global Summary")
    lines.append("")
    lines.append(f"- Countries in basis universe: `{len(countries)}`")
    if args.basis == "population":
        lines.append(f"- Total population (join universe): `{basis_total:,}`")
        lines.append(f"- Threshold population: `{threshold_value:,}`")
        lines.append(f"- Actual covered population: `{running:,}` (`{(running / basis_total * 100):.2f}%`)")
    else:
        lines.append(f"- Global ADM2 denominator: `{basis_total:,}`")
        lines.append(f"- Threshold ADM2 units: `{threshold_value:,}`")
        lines.append(f"- Covered ADM2 units by selected set: `{running:,}` (`{(running / basis_total * 100):.2f}%`)")
    lines.append(f"- Countries needed for threshold: `{len(selected)}`")
    lines.append("")
    lines.append("## ADM2 Progress Inside Selected Set")
    lines.append("")
    lines.append(f"- ADM2 denominator (selected countries): `{selected_adm2_total:,}`")
    lines.append(f"- Implemented ADM2 (selected countries): `{selected_adm2_have:,}`")
    lines.append(f"- Remaining ADM2 gap (selected countries): `{selected_adm2_gap:,}`")
    lines.append(f"- ADM2 coverage in selected countries: `{(selected_adm2_have / selected_adm2_total * 100 if selected_adm2_total else 0):.4f}%`")
    lines.append("")
    lines.append(f"## Countries Included ({'Population' if args.basis == 'population' else 'ADM2 Total'} Desc)")
    lines.append("")
    lines.append("| Rank | ISO | Country | Population | CumShare | ADM2 Total | ADM2 Have | ADM2 Gap |")
    lines.append("|---:|---|---|---:|---:|---:|---:|---:|")
    for row in selected:
        pop_value = f"{int(row['population']):,}" if row["population"] is not None else "-"
        lines.append(
            "| {rank} | {iso} | {country} | {population} | {cum:.2f}% | {adm2_total:,} | {existing_adm2:,} | {adm2_gap:,} |".format(
                rank=row["rank"],
                iso=row["iso"],
                country=row["country"],
                population=pop_value,
                cum=row["cumulative_share"] * 100,
                adm2_total=row["adm2_total"],
                existing_adm2=row["existing_adm2"],
                adm2_gap=row["adm2_gap"],
            )
        )

    with report_path.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(str(jsonl_path))
    if pilot_path is not None:
        print(str(pilot_path))
    print(str(report_path))
    print(f"countries_total={len(countries)}")
    print(f"countries_selected={len(selected)}")
    print(f"{args.basis}_share={(running / basis_total * 100):.4f}")
    print(f"selected_adm2_have={selected_adm2_have}")
    print(f"selected_adm2_total={selected_adm2_total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
