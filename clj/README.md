# etzhayyim-project-states — clj/bb port (ADR-2606280030)

Idiomatic Clojure/babashka port of the app's standalone Python data-tooling.
This app is **not** a LangGraph StateGraph app — it is a set of pure-stdlib
data-generation scripts that build `scripts/static-profile-data.json` and the
per-country state records. There is no graph to port; each Python module is
ported faithfully to a plain `.cljc` namespace (pure fns + thin `-main`).

## Verify

```bash
cd 60-apps/etzhayyim-project-states/clj
bb test          # clojure.test suite (run_tests.clj) — 26 tests / 88 assertions
```

cheshire (JSON) and clojure.test are built into babashka, so this `bb.edn` has
no external deps. No httpx/FastAPI/numpy/RisingWave/LLM are involved.

## Ported namespaces (src/etzhayyim/states/)

| cljc ns | Python twin | notes |
|---|---|---|
| `profile`     | (shared) emit-state-records.slug/put_body + json helpers | core |
| `frameworks`  | scripts/add-generic-frameworks.py, scripts/add-constitutional-frameworks.py | data: resources/.../frameworks.json |
| `desks`       | scripts/add-generic-desks.py | |
| `procedures`  | scripts/add-tier3-procedures.py | RICH set: resources/.../rich.json |
| `extend`      | scripts/extend-static-{final,data,tier3}.py | data: final/ext/tier3.json |
| `stubs`       | scripts/create-missing-stubs.py | |
| `enrich`      | scripts/enrich-kotodama-profiles.py | id-merge semantics |
| `emit-records`| scripts/emit-state-records.py | COUNTRY map: resources/.../country.json |

The large Python dict literals (`COUNTRY`, `FRAMEWORKS`, `EXT`, `T3`, `FINAL`,
`RICH`) were extracted verbatim to JSON resources under
`resources/etzhayyim/states/data/` (zero-transcription faithfulness) and are
loaded with cheshire.

## Canonical (the clj twin replaces the ported Python)

The 10 ported `scripts/*.py` modules listed above were **deleted** — this clj
twin is now the canonical code (ADR-2606280030, founder "twin の py を削除").
The deletion is grep-confirmed safe: nothing outside this app imports them, and
no cron / `langgraph.json` / scheduler / `.sh` runner invokes them. The larger
`tools/*.py` generators (see "Not yet ported" below) have **no** clj twin yet and
are **kept**.

## Not yet ported (status: partial)

The larger `tools/*.py` generators remain Python (port candidates for a later
pass): `gen-municipality-ndjson.py` (2738 LoC), `codegen-wit-migrate.py`,
`gen-bpmn.py`, `260304-adm2-multi-agent-generate.py`, `gen-lea-stubs.py`,
`generate_missing_org_components.py`, `gen-seed-ndjson.py`,
`evaluate_implementation_coverage.py`, `260303-adm2-pilot-select.py`,
`260303-adm2-pop80-select.py`. Several use `urllib.request` (→ would move to
`babashka.http-client`) and are larger/codegen-heavy.
