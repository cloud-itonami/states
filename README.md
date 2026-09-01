# states — a corpus of the world's government organisations, plus the tooling that shapes it

`cloud-itonami/states` (west path `orgs/cloud-itonami/states`) is a **data-heavy
repository**, not a service. It holds:

- **`data/gov/`** — the ingested corpus: one directory per country (ISO-3166-1
  alpha-3, lowercase) holding NDJSON rows for ministries, offices, districts,
  municipalities, law-enforcement agencies and contracts, plus generated BPMN
  process definitions.
- **`clj/`** — a babashka/Clojure toolchain (`etzhayyim.states.*`) that builds
  and mutates `scripts/static-profile-data.json` and turns the corpus into
  `com.atproto.repo.putRecord` bodies.
- **`tools/`** — the Python generators that have **not** been ported to Clojure
  (BPMN generation, municipality/seed NDJSON generation, coverage evaluation).
- **`appview/`** — one directory per country holding a `kotodama.jsonld`
  manifest (and, for some, a `src/app.ts`) describing that country's AI-agent
  profile.
- **`reports/`** — dated audit reports written during the ADM2 expansion work.

The name is bare, so: **this repo is the *states* corpus — “state” as in
sovereign state, not as in program state.** Nothing here is a state machine.

> **Start here to actually run something:
> [`docs/operator-quickstart.md`](docs/operator-quickstart.md).**
> Every command in that document was executed against this tree before it was
> written, and the numbers below come from those runs.

## What is actually in the tree (measured 2026-09-01 at `15f6ffb`)

| | |
|---|---|
| country directories under `data/gov/` | 203 |
| NDJSON files | 856 |
| BPMN files | 3,287 |
| appview directories | 199 |
| `scripts/static-profile-data.json` | 330,249 bytes, 199 country entries |
| Clojure sources / tests | 8 `.cljc` in `clj/src`, 8 in `clj/test` |
| test suite | 26 tests / 88 assertions, green |

Rows per NDJSON kind:

| kind | rows | countries carrying the file |
|---|---:|---:|
| `district` | 1,507 | 179 |
| `office` | 1,039 | 60 |
| `municipality` | 527 | 177 |
| `lea` | 272 | 195 |
| `ministry` | 186 | 61 |
| `contract` | 181 | 181 |

Reproduce the census with the commands in
[`docs/operator-quickstart.md` §2](docs/operator-quickstart.md).

## Three things that are broken, and are load-bearing

These were found by running the code, not by reading it. Each has a
reproduction in the quickstart. **None of them is fixed** — they are recorded
here so the next person does not rediscover them.

1. **2,455 of the 3,287 committed BPMN files are not well-formed XML.**
   They contain a raw `&` in attribute values. `tools/gen-bpmn.py` learned to
   XML-escape at some point and nobody regenerated: running it today produces
   3,626 files, **all** well-formed. See quickstart §5.
2. **`bb -m etzhayyim.states.stubs` destroys the appview tree.**
   `existing-isos` reads the wrong `-`-separated segment, so it returns nanoids
   (`g0vjpn01`) instead of ISO codes (`jpn`) and every country looks missing.
   Running it against a copy of this tree overwrote **196 of 199** rich
   `kotodama.jsonld` files with minimal stubs. See quickstart §4.
   **Do not run it against the repository.**
3. **The emit → upload pipeline has no driver.**
   `scripts/upload-state-records.sh` POSTs `/tmp/state-records/{profile,procedure,document}/*.json`,
   and `etzhayyim.states.enrich/enrich-one` reads a `records-dir` of `{iso3}.json`
   bodies — but **nothing in this repository writes either directory.** The
   Python original (`scripts/emit-state-records.py`) was deleted when the Clojure
   port landed, and `emit_records.cljc` kept only the pure builders; its
   namespace docstring still claims “file/NDJSON I/O is isolated in `-main`”,
   and there is no `-main`. See quickstart §3.

## Provenance and naming

This repository was extracted from the `etzhayyim/root` monorepo
(`60-apps/etzhayyim-project-states`, source revision `601e2fc4`); `README.edn`
and `migration.edn` are the canonical records of that extraction and should not
be deleted.

**The extraction left stale paths behind.** `README.edn` still calls this repo
`com-etzhayyim-app-states`; `clj/README.md` tells you to `cd
60-apps/etzhayyim-project-states/clj`; `etzhayyim.states.stubs/-main` defaults
its app-root to `60-apps/etzhayyim-project-states` and therefore fails with
`FileNotFoundException` when run with no argument; every record emitted by
`emit-records` carries `dataSourceRef: 60-apps/etzhayyim-project-states/data/gov/<iso>/`,
a path that does not exist here; and `reports/` describes a `wasm/` tree of
2,759 components that was **not** extracted into this repository. Treat any
`60-apps/…` path in this repo as a reference to the pre-extraction monorepo.

## Licence

Apache License 2.0 with the etzhayyim Charter Compliance Rider v3.1 — see
`NOTICE`.
