(ns etzhayyim.states.profile
  "Core helpers for the etzhayyim-project-states data tooling.

  Clojure/babashka port of the `scripts/*.py` family that builds and mutates
  `scripts/static-profile-data.json` plus the per-country state records.
  Pure transforms live in the sibling namespaces; this namespace holds the
  shared JSON / resource / slug / put-body helpers.

  Faithful to:
    - scripts/*.py (the static-profile-data.json mutation family)
    - scripts/emit-state-records.py (slug, put_body)

  Per ADR-2606280030 (60-apps python -> clj migration). JSON via cheshire,
  errors via ex-info, no RisingWave/heavy-numerics (none needed here)."
  (:require [cheshire.core :as json]
            [clojure.string :as str]
            #?(:clj [clojure.java.io :as io])))

;; ---------------------------------------------------------------------------
;; JSON I/O (mirrors `json.loads(path.read_text())` / `path.write_text(...)`)
;; ---------------------------------------------------------------------------

(defn read-json
  "Parse a JSON file into Clojure data with string keys (python dict parity)."
  [path]
  #?(:clj (-> (slurp path) (json/parse-string false))
     :cljs (throw (ex-info "read-json is JVM/bb only" {:path path}))))

(defn write-json!
  "Write `data` as pretty JSON + trailing newline (mirrors
  `json.dumps(data, indent=2, ensure_ascii=False) + \"\\n\"`)."
  [path data]
  #?(:clj (spit path (str (json/generate-string data {:pretty true}) "\n"))
     :cljs (throw (ex-info "write-json! is JVM/bb only" {:path path}))))

;; ---------------------------------------------------------------------------
;; Embedded reference data (faithfully extracted from the python dict literals)
;; ---------------------------------------------------------------------------

(defn load-data
  "Load one of the embedded reference data JSON resources (string-keyed),
  e.g. (load-data \"country.json\"). Throws ex-info if missing."
  [resource-name]
  #?(:clj (let [r (io/resource (str "etzhayyim/states/data/" resource-name))]
            (when-not r
              (throw (ex-info "missing data resource" {:resource resource-name})))
            (json/parse-string (slurp r) false))
     :cljs (throw (ex-info "load-data is JVM/bb only" {:resource resource-name}))))

;; ---------------------------------------------------------------------------
;; Pure string helpers
;; ---------------------------------------------------------------------------

(defn slug
  "Port of emit-state-records.slug(): lowercase, non-alnum runs -> '-',
  trim leading/trailing '-', cap at 48 chars, default 'x' when empty."
  [s]
  (let [s (-> (str s) str/lower-case)
        s (str/replace s #"[^a-z0-9]+" "-")
        s (str/replace s #"^-+|-+$" "")
        s (subs s 0 (min 48 (count s)))]
    (if (empty? s) "x" s)))

(defn put-body
  "Port of emit-state-records.put_body(): a ready-to-POST com.atproto.repo.putRecord body."
  [repo collection rkey record]
  {"repo" repo "collection" collection "rkey" rkey "record" record})

(defn display-name
  "entry.get('displayName') or iso.upper() — the recurring fallback in the scripts."
  [entry iso]
  (or (get entry "displayName")
      (str/upper-case iso)))
