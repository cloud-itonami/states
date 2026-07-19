# ADM2 Coverage Improvement Plan (Codex Exec 5.3 Spark + kotodama runtime)

## 1. Baseline (2026-03-03)
- Current municipal-like entities in repo: `752`
- ADM2 global denominator (geoBoundaries): `49,363`
- Current ADM2 coverage: `1.5234%`

## 2. Target
- Phase 1 (30 days): `5%` (`~2,468` entities)
- Phase 2 (60 days): `12%` (`~5,924` entities)
- Phase 3 (90 days): `20%` (`~9,873` entities)

## 3. Core Strategy
Use `codex exec 5.3 spark` as a parallel generation engine to produce ADM2 performer packages, then validate and deploy on kotodama runtime in controlled batches.

Pipeline:
1. ADM2 source ingest (country → ADM2 list)
2. Canonical slug generation (`org-gov-{iso}-...-dst-{code}-{name}`)
3. Artifact generation (Go/WIT/App/K8s/JSON-LD)
4. Static validation (schema, naming, image/name consistency)
5. Batch deploy to `kotodama-runtime`
6. Route/health verification
7. Coverage recompute and report

## 4. kotodama runtime Parallel Architecture
- `planner` component: creates country/ADM2 work items
- `generator` workers (N-way): run `codex exec 5.3 spark` prompts for scaffold generation
- `validator` workers: lint + policy checks + duplicate detection
- `deployer` worker: single-writer apply policy per app family
- `auditor` worker: coverage metrics + drift/noise scan

Queue model:
- Partition by ISO country code
- Limit concurrent generators per country (avoid naming collision)
- Global concurrency cap (e.g. `32` workers) with retry/backoff

## 5. LLM Prompt Contract (Codex Exec 5.3 Spark)
Each task must produce:
- `main.go`, `go.mod`, `kotodama.toml`
- `deploy config` (`namespace: kotodama-runtime`, GHCR image)
- optional `k8s/http-routes.yaml` (`namespace: edge-router-performers`)
- `<entity>.jsonld` metadata

Hard constraints:
- `metadata.name` and `spec.image` stem must match
- image registry: `ghcr.io/etzhayyim/*`
- API endpoint convention: `https://{nanoid}.etzhayyim.com/xrpc`

## 6. Quality Gates
- Gate A: file completeness (required files present)
- Gate B: policy compliance (namespace, image registry, naming)
- Gate C: semantic consistency (`name` ↔ `image` ↔ directory slug)
- Gate D: deploy health (`App` phase, service readiness)

Reject and requeue on any failed gate.

## 7. Batch Rollout Plan
- Batch size: `100` ADM2 entities
- Cadence: `2` batches/day
- Daily potential: `200`
- To reach +1,716 entities (5% target): `~9 days` at full throughput

Safety:
- One deploy writer per target segment
- Canary first 10 entities of each batch
- Auto rollback if failure rate > `5%`

## 8. Coverage KPI / SLO
- Primary KPI: `adm2_coverage = generated_adm2 / 49,363`
- Secondary KPI:
  - `name-image mismatch rate` < `0.1%`
  - `duplicate metadata.name` = `0`
  - `App apply success` >= `99%`
  - `ready within 10m` >= `95%`

## 9. Immediate Implementation Backlog
1. Add `adm2-source-ingest` job (geoBoundaries pull + normalized task file)
2. Add `states-generator-orchestrator` (queue + worker control)
3. Add `App quality check` script (mismatch/duplicate guard)
4. Add daily coverage report output (`YYMMDD-adm2-coverage-report.md`)
5. Start pilot with 3 countries, then scale globally
