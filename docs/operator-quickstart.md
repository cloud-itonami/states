# Operator quickstart

Every command below was run against this tree at `15f6ffb` on 2026-09-01 and
the output shown is the output observed. Where a command is **destructive**, it
is marked and given a scratch-copy form; run the scratch form.

Prerequisites: `bb` (babashka) and `python3`. No network, no credentials, and
no external Clojure dependencies are needed for §1–§5 — `cheshire` and
`clojure.test` are built into babashka. §6 needs credentials you probably do
not have; read it before trying.

---

## §1 — Verify the Clojure toolchain

```bash
cd clj
bb test
```

Expected, and observed:

```
Ran 26 tests containing 88 assertions.
0 failures, 0 errors.
```

Exit code 0. `clj/README.md` says to `cd 60-apps/etzhayyim-project-states/clj`
first — that path is from the pre-extraction monorepo and does not exist here.
`cd clj` from the repository root is correct.

---

## §2 — Census the corpus

From the repository root:

```bash
ls -d data/gov/*/ | wc -l                      # 203 country directories
find data/gov -name '*.ndjson' | wc -l         # 856
find data/gov -name '*.bpmn'   | wc -l         # 3287
ls -d appview/*/ | wc -l                       # 199
wc -c scripts/static-profile-data.json         # 330249
```

Rows per NDJSON kind:

```bash
for k in district office municipality lea ministry contract; do
  printf '%-14s %6s rows in %3s countries\n' "$k" \
    "$(cat data/gov/*/$k.ndjson 2>/dev/null | wc -l | tr -d ' ')" \
    "$(ls data/gov/*/$k.ndjson 2>/dev/null | wc -l | tr -d ' ')"
done
```

```
district        1507 rows in 179 countries
office          1039 rows in  60 countries
municipality     527 rows in 177 countries
lea              272 rows in 195 countries
ministry         186 rows in  61 countries
contract         181 rows in 181 countries
```

Two directory names under `data/gov/` are not ISO-3166 alpha-3 codes: `intl`
(international bodies, 32 ministry rows — deliberate) and **`0`**, whose rows
carry `"countryCode": "0"` and whose contents (`Supreme People's Assembly`,
`State Affairs Commission`, `Korean People's Army`) indicate DPRK. `0` looks
like an ingest defect, not a decision; it is left as found.

---

## §3 — Build putRecord bodies for one country (read-only)

The record builders are pure and work on the committed corpus. Save this as
`/tmp/probe-emit.clj` and run it **from `clj/`**:

```clojure
(require '[etzhayyim.states.profile :as profile]
         '[etzhayyim.states.emit-records :as emit])
(def root "..")
(def iso "jpn")
(def country    (profile/load-data "country.json"))
(def static     (profile/read-json (str root "/scripts/static-profile-data.json")))
(def ministries (emit/read-ndjson (slurp (str root "/data/gov/" iso "/ministry.ndjson"))))
(def contracts  (emit/read-ndjson (slurp (str root "/data/gov/" iso "/contract.ndjson"))))
(def bpmn (mapv #(.getName %)
                (.listFiles (clojure.java.io/file (str root "/data/gov/" iso "/bpmn")))))
(println "country-map entries:" (count country))
(println "static entries:" (count static))
(println "ministries:" (count ministries) " contracts:" (count contracts)
         " bpmn:" (count bpmn))
(let [out (emit/emit-country country static iso ministries contracts bpmn)]
  (println "profile rkey:"  (get (:profile out) "rkey")
           " collection:"   (get (:profile out) "collection"))
  (println "procedures:"    (count (:procedures out))
           " documents:"    (count (:documents out)))
  (println "dataSourceRef:" (get-in (:profile out) ["record" "dataSourceRef"])))
```

```bash
cd clj && bb /tmp/probe-emit.clj
```

Observed:

```
country-map entries: 195
static entries: 199
ministries: 42  contracts: 1  bpmn: 141
profile rkey: jpn  collection: com.etzhayyim.apps.states.stateProfile
procedures: 20  documents: 1
dataSourceRef: 60-apps/etzhayyim-project-states/data/gov/jpn/
```

Two things to notice.

**The `dataSourceRef` is wrong.** Every record this code emits today points at
`60-apps/etzhayyim-project-states/data/gov/<iso>/`, a monorepo path that does
not exist in this repository. The same stale prefix is baked into `bpmnRef` on
every procedure. It is a string literal in `clj/src/etzhayyim/states/emit_records.cljc`.

**There is no driver.** `emit-country` is pure — it returns the bodies, it does
not write them. `scripts/upload-state-records.sh` expects
`/tmp/state-records/{profile,procedure,document}/*.json`, and
`etzhayyim.states.enrich/enrich-one` expects a `records-dir` of `{iso3}.json`
bodies. **Nothing in this repository writes either.** The Python original
(`scripts/emit-state-records.py`) was deleted when the Clojure port landed
(ADR-2606280030), and the port kept only the pure builders. Confirm for
yourself:

```bash
grep -rn "defn -main" clj/src            # 5 hits: desks, stubs, frameworks, extend, procedures
grep -rn "read-ndjson" clj/src clj/test  # only its own definition and its own test
```

`emit_records.cljc`'s namespace docstring says “file/NDJSON I/O is isolated in
`-main`”. There is no `-main` in that file. **Writing that driver is the single
change that would make the pipeline runnable end to end.**

---

## §4 — The static-profile mutators (and the one you must not run)

Four of the five `-main`s rewrite `scripts/static-profile-data.json` in place.
Run them against a scratch copy:

```bash
rm -rf /tmp/states-dry && mkdir -p /tmp/states-dry/scripts
cp scripts/static-profile-data.json /tmp/states-dry/scripts/
cd clj
for ns in frameworks desks procedures extend; do
  printf '%-12s ' "$ns"
  bb -m etzhayyim.states.$ns /tmp/states-dry/scripts/static-profile-data.json | tail -1
done
```

Observed:

```
frameworks   constitutional frameworks: 46, generic frameworks: 0
desks        added generic desks to 0 countries
procedures   added standard procs/docs to 0 countries
extend       ext: 0, tier3: 0, final: 0 -> total 199
```

**The chain is saturated.** Every counter is 0 except `constitutional
frameworks: 46`, which counts countries *touched*, not countries *changed*.
Parsing both files and comparing confirms it:

```bash
cd clj && bb -e '(require (quote [cheshire.core :as json]))
(println (= (json/parse-string (slurp "../scripts/static-profile-data.json") false)
            (json/parse-string (slurp "/tmp/states-dry/scripts/static-profile-data.json") false)))'
# true
```

The rewritten file is 307,650 bytes against the committed 330,249 — that
difference is entirely cheshire's pretty-printer disagreeing with Python's
`json.dumps(indent=2)`. **Do not commit the reformatted file**: the diff would
be the whole file and would mean nothing.

### ⚠ `etzhayyim.states.stubs` is destructive. Do not run it against this repo.

With no argument it fails outright, because its app-root default is the
pre-extraction monorepo path:

```bash
cd clj && bb -m etzhayyim.states.stubs; echo "EXIT=$?"
# java.io.FileNotFoundException:
#   60-apps/etzhayyim-project-states/scripts/static-profile-data.json
# EXIT=1
```

Given a correct root it *succeeds*, and that is the problem. `existing-isos`
splits `etzhayyim-wasm-states-jpn-g0vjpn01` on `-` and takes segment **4**,
which is the nanoid `g0vjpn01`; the ISO code `jpn` is segment **3**. So the
returned set never contains an ISO code, `(contains? existing iso)` is always
false, and every one of the 199 countries is treated as missing. Verify:

```bash
cd clj && bb -e '(require (quote [etzhayyim.states.stubs :as s]))
(def e (s/existing-isos "../appview"))
(println (count e) (vec (take 3 (sort e))) (contains? e "jpn"))'
# 199 [d3yqp37e g0vafg01 g0vago01] false
```

Measure the blast radius on a copy — **never on the repository**:

```bash
rm -rf /tmp/states-stub && mkdir -p /tmp/states-stub
cp -R scripts appview /tmp/states-stub/
cd clj && bb -m etzhayyim.states.stubs /tmp/states-stub | tail -1
# created 199 stub kotodama.jsonld files
```

Then compare each committed manifest against its scratch counterpart:

```bash
same=0; over=0
for d in appview/*/; do b=$(basename "$d")
  if cmp -s "$d/kotodama.jsonld" "/tmp/states-stub/appview/$b/kotodama.jsonld"
  then same=$((same+1)); else over=$((over+1)); fi
done
echo "unchanged=$same overwritten=$over"
# unchanged=3 overwritten=196
```

**196 of 199 rich manifests were replaced by 1.9 KB stubs.** The three
survivors are the countries whose real directory nanoid is not `g0v{iso}01`;
for those, a *duplicate* directory is created instead. Japan's real manifest is
`appview/etzhayyim-wasm-states-jpn-d3yqp37e/kotodama.jsonld` (8,429 bytes,
`@id: did:web:jpn-state.etzhayyim.com`); the run additionally created
`appview/etzhayyim-wasm-states-jpn-g0vjpn01/kotodama.jsonld` claiming
`@id: did:web:jpn.state.etzhayyim.com` — **a second, conflicting DID for the
same country.**

The fix is one character (`(nth parts 4)` → `(nth parts 3)` in
`clj/src/etzhayyim/states/stubs.cljc`) plus a test that pins
`(contains? (existing-isos "appview") "jpn")`. That has not been done here, on
purpose: this pass changed documentation only, and a behaviour fix belongs with
the test that proves it.

---

## §5 — Regenerate the BPMN and see the drift

`tools/gen-bpmn.py` reads `data/gov/*/*.ndjson` and writes
`data/gov/<iso>/bpmn/*.bpmn`, relative to the working directory. Run it on a
copy:

```bash
rm -rf /tmp/states-bpmn && mkdir -p /tmp/states-bpmn
cp -R data tools /tmp/states-bpmn/
cd /tmp/states-bpmn && find data/gov -name '*.bpmn' -delete
python3 tools/gen-bpmn.py | tail -2
# Created: 3626  Skipped (existing): 0
# Total BPMN files: 3626
```

The repository has **3,287**. The generator produces **3,626** — and of the
3,287 committed files, only **832** are byte-identical to their regenerated
counterpart:

Then, from the repository root:

```bash
same=0; drift=0
while IFS= read -r f; do
  if cmp -s "$f" "/tmp/states-bpmn/$f"; then same=$((same+1)); else drift=$((drift+1)); fi
done < <(find data/gov -name '*.bpmn' | sort)
echo "identical=$same drift=$drift"
# identical=832 drift=2455
```

The drift is not nondeterminism. It is a single, checkable defect:

```bash
python3 - <<'EOF'
import xml.etree.ElementTree as ET, pathlib
files = sorted(pathlib.Path("data/gov").rglob("*.bpmn")); bad = 0
for p in files:
    try: ET.parse(p)
    except ET.ParseError: bad += 1
print(f"scanned={len(files)} MALFORMED={bad}")
EOF
# scanned=3287 MALFORMED=2455
```

Run the same check inside `/tmp/states-bpmn` and it reports
`scanned=3626 MALFORMED=0`.

**2,455 committed BPMN files are not well-formed XML.** They carry a raw `&`
inside an attribute value (`name="… & Logistics"`); `gen-bpmn.py` imports
`xml.sax.saxutils.escape` and emits `&amp;`. *Inference, not measurement*: the
escaping most likely postdates the committed corpus and nobody regenerated —
this repository has a single commit, so its history cannot confirm that.
What **is** measured is the current state: generator escapes, corpus does not.
Regenerating in place would fix all 2,455 and add the 339 files the generator
produces that are not committed (3,626 − 832 − 2,455 = 339), but that is a
~3,600-file commit and belongs in its own change with its own review.

**This check is a usable gate**: it separates a good tree from a bad one and it
has shown both answers — 2,455 malformed on the committed tree, 0 on the
regenerated one.

---

## §6 — Publishing (needs credentials this repo does not carry)

`scripts/upload-state-records.sh` POSTs record bodies to
`https://atproto.etzhayyim.com/xrpc/com.atproto.repo.putRecord`, minting a
bearer token per request with `etzhayyim agent-token --lxm
com.atproto.repo.putRecord`. It needs the `etzhayyim` CLI, a PDS credential,
and an input directory.

**You cannot run it from this repository today**, because of §3: nothing here
produces `/tmp/state-records`. Write the emit driver first. The script itself
is resumable — it keeps `.uploaded.log` and `.failed.log` in the input
directory and skips what it has already sent, so a re-run retries only
failures.

---

## What this document does not cover

- **`appview/*/src/app.ts`** — 140 of the 199 appview directories have one
  (plus a single `src/bpmn-index.ts` under `etzhayyim-wasm-states-ind-hs54vjd0`).
  There is no build, deploy, or test path for them in this repository.
- **The `wasm/` tree.** `reports/260311-implementation-coverage-audit.md`
  audits 2,759 WebAssembly components under
  `60-apps/etzhayyim-project-states/wasm`. **That tree was not extracted into
  this repository.** The reports are historical records of a tree that lives
  elsewhere; do not read their percentages as describing this repo.
- **The unported Python generators** other than `gen-bpmn.py`
  (`gen-municipality-ndjson.py`, `gen-seed-ndjson.py`, `gen-lea-stubs.py`,
  `evaluate_implementation_coverage.py`, the two ADM2 selectors). Several use
  `urllib.request` and reach the network. They were not run here.
- **`tools/260303-adm2-pilot-codex-run.sh`** shells out to an external `codex`
  CLI with `MODEL=gpt-5.3-spark` and reads `tmp/260303-adm2-pilot-10-targets.jsonl`,
  which is not in the tree.

## Suggested next change

Fix `existing-isos` (§4) and pin it with a test. It is the smallest change with
the largest consequence: until it is fixed, the repository contains a command
that silently destroys 196 of its own 199 manifests.
