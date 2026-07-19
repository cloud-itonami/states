# Implementation Coverage Audit

- Generated: 2026-03-11 19:29:12
- Scope: `60-apps/etzhayyim-project-states/wasm`
- Total top-level components: `2759`

## Findings

1. Structural scaffold coverage is effectively complete: `wit/world.wit`, `main.go`, and `deploy config` exist for `2759/2759`, `2759/2759`, and `2759/2759` components respectively.
2. Business interface depth is limited: only `170/2759` (6.2%) components ship a proto contract, `203/2759` (7.4%) register explicit adapter methods, and `150/2759` (5.4%) use `performer.NewRuntime` + `PerformerConfig`.
3. Durable workflow/state coverage is partial: `etzhayyim:workflow` and `etzhayyim:activity` appear in `761/2759` components each, `wasi:keyvalue` appears in `1083/2759`, `database/` exists in `85/2759`, and `db_state.go` exists in only `2/2759`.
4. Verification and documentation coverage are weak: `_test.go` files exist in `0/2759` components, README files in `92/2759`, while JSON-LD metadata exists in `1969/2759`.
5. ADM2 expansion is ahead of the last repo report but still sparse in global terms: current loose `-dst-` count is `1563`, strict canonical ADM2 count is `752`, versus the 2026-03-03 report baseline of `762` loose / `752` strict.

## Metric Summary

| Metric | Count | Share |
|---|---:|---:|
| `wit/world.wit` present | 2759 | 100.0% |
| `main.go` present | 2759 | 100.0% |
| `deploy config` present | 2759 | 100.0% |
| Proto contract present | 170 | 6.2% |
| JSON-LD metadata present | 1969 | 71.4% |
| README present | 92 | 3.3% |
| `agent.json` present | 196 | 7.1% |
| `sqlc.yaml` present | 166 | 6.0% |
| `database/` dir present | 85 | 3.1% |
| `db_state.go` present | 2 | 0.1% |
| `_test.go` present | 0 | 0.0% |
| `performer.NewRuntime` | 150 | 5.4% |
| `performer.NewAdapter` | 1836 | 66.5% |
| `BindToAdapter` | 150 | 5.4% |
| `performer.PerformerConfig` | 150 | 5.4% |
| Adapter method registration (`a.Register`) | 203 | 7.4% |
| Non-empty `registerMethods` body | 203 | 7.4% |
| `nata.NewStore` / performer nata store | 1420 | 51.5% |
| `etzhayyim:workflow` in `world.wit` | 761 | 27.6% |
| `etzhayyim:activity` in `world.wit` | 761 | 27.6% |
| `wasi:keyvalue` in `world.wit` | 1083 | 39.3% |

## Topology

- ADM2 loose count (`-dst-` in directory name): `1563`
- ADM2 strict canonical count: `752`
- Non-ADM2 components: `1196`
- Countries / buckets represented in directory names: `183`

## File Richness

- `6-10` files: `1728`
- `11-20` files: `778`
- `21+` files: `253`

## Largest Country Buckets

| ISO | Component Count |
|---|---:|
| `ind` | 783 |
| `jpn` | 129 |
| `chn` | 89 |
| `bra` | 83 |
| `col` | 83 |
| `mex` | 83 |
| `rus` | 83 |
| `tur` | 83 |
| `usa` | 83 |
| `tha` | 77 |

## Interpretation

- The repo has very high scaffold coverage, but only a small minority of components have rich service contracts, explicit performer runtime registration, or persistent schema-backed state.
- `etzhayyim-project-states` should be treated as a mixed estate: a broad generated shell with a narrower band of deeper implementations.
- The highest-risk gap is verification: there are no `_test.go` files under the component directories scanned here.
