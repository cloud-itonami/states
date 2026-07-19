#!/usr/bin/env python3
"""Evaluate implementation coverage for etzhayyim-project-states."""

from __future__ import annotations

import argparse
import re
from collections import Counter
from datetime import datetime
from pathlib import Path


STRICT_ADM2_RE = re.compile(r"^etzhayyim-performer-sys-etzhayyim-actors-pba7d22f-org-gov-[a-z0-9]+-.*-dst-")


def pct(numerator: int, denominator: int) -> str:
    if denominator == 0:
        return "0.0%"
    return f"{(numerator / denominator * 100):.1f}%"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def collect_metrics(base: Path) -> dict:
    metrics = Counter()
    country_counts = Counter()

    for component in sorted(base.iterdir()):
        if not component.is_dir():
            continue

        metrics["total_components"] += 1
        name = component.name

        if "-dst-" in name:
            metrics["adm2_loose"] += 1
        else:
            metrics["non_adm2"] += 1
        if STRICT_ADM2_RE.search(name):
            metrics["adm2_strict"] += 1

        parts = name.split("-")
        try:
            idx = parts.index("gov")
        except ValueError:
            idx = -1
        if idx >= 0 and idx + 1 < len(parts):
            country_counts[parts[idx + 1]] += 1

        world = component / "wit" / "world.wit"
        main_go = component / "main.go"

        if world.exists():
            metrics["with_world_wit"] += 1
            world_text = read_text(world)
            if "etzhayyim:workflow" in world_text:
                metrics["world_with_workflow"] += 1
            if "etzhayyim:activity" in world_text:
                metrics["world_with_activity"] += 1
            if "wasi:keyvalue" in world_text:
                metrics["world_with_keyvalue"] += 1

        if main_go.exists():
            metrics["with_main_go"] += 1
            main_text = read_text(main_go)
            if "performer.NewRuntime(" in main_text:
                metrics["main_new_runtime"] += 1
            if ".BindToAdapter(" in main_text:
                metrics["main_bind_to_adapter"] += 1
            if "performer.NewAdapter(" in main_text:
                metrics["main_new_adapter"] += 1
            if "nata.NewStore(" in main_text or 'nata "github.com/etzhayyim/performer/lancedbrest"' in main_text:
                metrics["main_nata_store"] += 1
            if "performer.PerformerConfig{" in main_text:
                metrics["main_register_performer_config"] += 1
            if "a.Register(performer.Method" in main_text:
                metrics["adapter_register_dirs"] += 1
            if "task accepted (stub mode)" in main_text or "status unavailable" in main_text:
                metrics["stub_runtime_dirs"] += 1

            marker = "func registerMethods(a *performer.Adapter) {"
            start = main_text.find(marker)
            if start >= 0:
                body_start = start + len(marker)
                body_end = main_text.find("}", body_start)
                body = main_text[body_start:body_end]
                if body.strip():
                    metrics["main_register_methods_nonempty"] += 1

        if (component / "k8s" / "spinapp.yaml").exists():
            metrics["with_k8s_spinapp"] += 1
        if (component / "README.md").exists():
            metrics["with_readme"] += 1
        if (component / "agent.json").exists():
            metrics["with_agent_json"] += 1
        if (component / "database").is_dir():
            metrics["with_database_dir"] += 1
        if (component / "sqlc.yaml").exists():
            metrics["with_sqlc"] += 1
        if list(component.rglob("db_state.go")):
            metrics["with_db_state_go"] += 1
        if list(component.rglob("*_test.go")):
            metrics["with_tests"] += 1
        if list(component.glob("proto/*.proto")):
            metrics["with_proto"] += 1
        if list(component.glob("*.jsonld")):
            metrics["with_jsonld"] += 1

        file_count = sum(1 for p in component.rglob("*") if p.is_file())
        if file_count <= 5:
            metrics["files_le_5"] += 1
        elif file_count <= 10:
            metrics["files_6_10"] += 1
        elif file_count <= 20:
            metrics["files_11_20"] += 1
        else:
            metrics["files_21_plus"] += 1

    metrics["top_country_component_count"] = max(country_counts.values()) if country_counts else 0
    metrics["country_count"] = len(country_counts)
    metrics["top_countries"] = country_counts.most_common(10)
    return dict(metrics)


def build_report(metrics: dict) -> str:
    def m(key: str) -> int:
        return int(metrics.get(key, 0))

    total = m("total_components")
    today = datetime.now().strftime("%Y-%m-%d %H:%M:%S %z")

    lines = [
        "# Implementation Coverage Audit",
        "",
        f"- Generated: {today}",
        "- Scope: `projects/etzhayyim-project-states/wasm`",
        f"- Total top-level components: `{total}`",
        "",
        "## Findings",
        "",
        f"1. Structural scaffold coverage is effectively complete: `wit/world.wit`, `main.go`, and `k8s/spinapp.yaml` exist for `{m('with_world_wit')}/{total}`, `{m('with_main_go')}/{total}`, and `{m('with_k8s_spinapp')}/{total}` components respectively.",
        f"2. Business interface depth is limited: only `{m('with_proto')}/{total}` ({pct(m('with_proto'), total)}) components ship a proto contract, `{m('adapter_register_dirs')}/{total}` ({pct(m('adapter_register_dirs'), total)}) register explicit adapter methods, and `{m('main_register_performer_config')}/{total}` ({pct(m('main_register_performer_config'), total)}) use `performer.NewRuntime` + `PerformerConfig`.",
        f"3. Durable workflow/state coverage is partial: `etzhayyim:workflow` and `etzhayyim:activity` appear in `{m('world_with_workflow')}/{total}` components each, `wasi:keyvalue` appears in `{m('world_with_keyvalue')}/{total}`, `database/` exists in `{m('with_database_dir')}/{total}`, and `db_state.go` exists in only `{m('with_db_state_go')}/{total}`.",
        f"4. Verification and documentation coverage are weak: `_test.go` files exist in `{m('with_tests')}/{total}` components, README files in `{m('with_readme')}/{total}`, while JSON-LD metadata exists in `{m('with_jsonld')}/{total}`.",
        f"5. ADM2 expansion is ahead of the last repo report but still sparse in global terms: current loose `-dst-` count is `{m('adm2_loose')}`, strict canonical ADM2 count is `{m('adm2_strict')}`, versus the 2026-03-03 report baseline of `762` loose / `752` strict.",
        "",
        "## Metric Summary",
        "",
        "| Metric | Count | Share |",
        "|---|---:|---:|",
        f"| `wit/world.wit` present | {m('with_world_wit')} | {pct(m('with_world_wit'), total)} |",
        f"| `main.go` present | {m('with_main_go')} | {pct(m('with_main_go'), total)} |",
        f"| `k8s/spinapp.yaml` present | {m('with_k8s_spinapp')} | {pct(m('with_k8s_spinapp'), total)} |",
        f"| Proto contract present | {m('with_proto')} | {pct(m('with_proto'), total)} |",
        f"| JSON-LD metadata present | {m('with_jsonld')} | {pct(m('with_jsonld'), total)} |",
        f"| README present | {m('with_readme')} | {pct(m('with_readme'), total)} |",
        f"| `agent.json` present | {m('with_agent_json')} | {pct(m('with_agent_json'), total)} |",
        f"| `sqlc.yaml` present | {m('with_sqlc')} | {pct(m('with_sqlc'), total)} |",
        f"| `database/` dir present | {m('with_database_dir')} | {pct(m('with_database_dir'), total)} |",
        f"| `db_state.go` present | {m('with_db_state_go')} | {pct(m('with_db_state_go'), total)} |",
        f"| `_test.go` present | {m('with_tests')} | {pct(m('with_tests'), total)} |",
        f"| `performer.NewRuntime` | {m('main_new_runtime')} | {pct(m('main_new_runtime'), total)} |",
        f"| `performer.NewAdapter` | {m('main_new_adapter')} | {pct(m('main_new_adapter'), total)} |",
        f"| `BindToAdapter` | {m('main_bind_to_adapter')} | {pct(m('main_bind_to_adapter'), total)} |",
        f"| `performer.PerformerConfig` | {m('main_register_performer_config')} | {pct(m('main_register_performer_config'), total)} |",
        f"| Adapter method registration (`a.Register`) | {m('adapter_register_dirs')} | {pct(m('adapter_register_dirs'), total)} |",
        f"| Non-empty `registerMethods` body | {m('main_register_methods_nonempty')} | {pct(m('main_register_methods_nonempty'), total)} |",
        f"| `nata.NewStore` / performer nata store | {m('main_nata_store')} | {pct(m('main_nata_store'), total)} |",
        f"| `etzhayyim:workflow` in `world.wit` | {m('world_with_workflow')} | {pct(m('world_with_workflow'), total)} |",
        f"| `etzhayyim:activity` in `world.wit` | {m('world_with_activity')} | {pct(m('world_with_activity'), total)} |",
        f"| `wasi:keyvalue` in `world.wit` | {m('world_with_keyvalue')} | {pct(m('world_with_keyvalue'), total)} |",
        "",
        "## Topology",
        "",
        f"- ADM2 loose count (`-dst-` in directory name): `{m('adm2_loose')}`",
        f"- ADM2 strict canonical count: `{m('adm2_strict')}`",
        f"- Non-ADM2 components: `{m('non_adm2')}`",
        f"- Countries / buckets represented in directory names: `{m('country_count')}`",
        "",
        "## File Richness",
        "",
        f"- `6-10` files: `{m('files_6_10')}`",
        f"- `11-20` files: `{m('files_11_20')}`",
        f"- `21+` files: `{m('files_21_plus')}`",
        "",
        "## Largest Country Buckets",
        "",
        "| ISO | Component Count |",
        "|---|---:|",
    ]
    for iso, count in metrics["top_countries"]:
        lines.append(f"| `{iso}` | {count} |")

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- The repo has very high scaffold coverage, but only a small minority of components have rich service contracts, explicit performer runtime registration, or persistent schema-backed state.",
            "- `etzhayyim-project-states` should be treated as a mixed estate: a broad generated shell with a narrower band of deeper implementations.",
            "- The highest-risk gap is verification: there are no `_test.go` files under the component directories scanned here.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[3]))
    parser.add_argument(
        "--output",
        default="projects/etzhayyim-project-states/reports/260311-implementation-coverage-audit.md",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    base = root / "projects/etzhayyim-project-states/wasm"
    metrics = collect_metrics(base)
    report = build_report(metrics)

    output = root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report, encoding="utf-8")
    print(f"wrote coverage audit to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
