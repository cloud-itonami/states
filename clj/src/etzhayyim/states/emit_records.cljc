(ns etzhayyim.states.emit-records
  "Port of scripts/emit-state-records.py.

  Emit one stateProfile + N stateProcedure + N stateDocument putRecord bodies
  per country, ready for PDS bulk com.atproto.repo.putRecord. The record
  builders are pure (data in -> data out); file/NDJSON I/O is isolated in -main."
  (:require [etzhayyim.states.profile :as profile :refer [slug put-body]]
            [cheshire.core :as json]
            [clojure.string :as str]
            #?(:clj [clojure.java.io :as io])))

(def repo "states.etzhayyim.com")

(defn read-ndjson
  "Port of read_ndjson: parse each non-blank line as JSON, skipping bad lines."
  [text]
  (->> (str/split-lines (or text ""))
       (map str/trim)
       (remove str/blank?)
       (keep (fn [line] (try (json/parse-string line false) (catch #?(:clj Exception :cljs :default) _ nil))))
       vec))

(defn- bpmn-name [path] (str (str/replace path #":" "-") ".bpmn"))

(defn inline-procedures
  "Top-6 ministries -> inline procedure maps (emit_country)."
  [iso3 ministries bpmn-files]
  (let [bset (set bpmn-files)]
    (->> (take 6 ministries)
         (keep (fn [m]
                 (let [path (or (get m "path") (slug (get m "name" "")))]
                   (when (seq path)
                     (let [bn (bpmn-name path) has? (contains? bset bn)]
                       {"id" (str iso3 "." (slug path))
                        "title" (or (get m "nameEn") (get m "name" ""))
                        "titleLocal" (get m "name" "")
                        "authority" (get m "name" "")
                        "basis" (get m "contract" "")
                        "portalUri" (get m "website" "")
                        "bpmnRef" (when has?
                                    (str "60-apps/etzhayyim-project-states/data/gov/" iso3 "/bpmn/" bn))})))))
         vec)))

(defn inline-documents
  "Top-4 contracts -> inline document maps."
  [iso3 contracts]
  (->> (take 4 contracts)
       (keep (fn [c]
               (let [cslug (or (get c "contractSlug") (slug (get c "name" "")))]
                 (when (seq cslug)
                   {"id" (str iso3 "." (slug cslug))
                    "title" (or (get c "nameEn") (get c "name" ""))
                    "titleLocal" (get c "name" "")
                    "basis" (get c "legalBasis" "")
                    "uri" (get c "url" "")}))))
       vec))

(defn profile-record
  "Build the stateProfile record map (emit_country)."
  [iso3 name region static ministries contracts bpmn-files]
  {"$type" "com.etzhayyim.apps.states.stateProfile"
   "iso3" iso3 "name" name
   "displayName" (or (get static "displayName") (str "Government of " name))
   "description" (str name " government registry - path-based DID, administrative desks, procedures (BPMN), and document templates.")
   "region" region "status" "active"
   "addresses" (get static "addresses" [])
   "contacts" (get static "contacts" [])
   "desks" (get static "desks" [])
   "complianceFrameworks" (get static "complianceFrameworks" [])
   "procedures" (into (vec (get static "procedures" [])) (inline-procedures iso3 ministries bpmn-files))
   "documentTemplates" (into (vec (get static "documentTemplates" [])) (inline-documents iso3 contracts))
   "ministryCount" (count ministries)
   "contractCount" (count contracts)
   "bpmnCount" (count bpmn-files)
   "dataSourceRef" (str "60-apps/etzhayyim-project-states/data/gov/" iso3 "/")
   "createdAt" "2026-04-18T04:00:00Z"})

(defn procedure-records
  "Up to 20 ministries -> [rkey record] pairs for stateProcedure."
  [iso3 ministries bpmn-files]
  (let [bset (set bpmn-files)]
    (->> (take 20 ministries)
         (keep (fn [m]
                 (let [path (or (get m "path") (get m "slug") (slug (get m "name" "")))]
                   (when (seq path)
                     (let [rkey (subs (str iso3 "-" (slug path)) 0 (min 64 (count (str iso3 "-" (slug path)))))
                           bn (bpmn-name path) has? (contains? bset bn)]
                       [rkey {"$type" "com.etzhayyim.apps.states.stateProcedure"
                              "iso3" iso3 "path" path
                              "title" (or (get m "nameEn") (get m "name" ""))
                              "titleLocal" (get m "name" "")
                              "authority" (get m "name" "")
                              "basis" (get m "contract" "")
                              "portalUri" (get m "website" "")
                              "orgTier" (get m "orgTier" "ministry")
                              "tags" (get m "tags" [])
                              "bpmnRef" (when has?
                                          (str "60-apps/etzhayyim-project-states/data/gov/" iso3 "/bpmn/" bn))
                              "createdAt" "2026-04-18T03:30:00Z"}])))))
         vec)))

(defn document-records
  "Up to 15 contracts -> [rkey record] pairs for stateDocument."
  [iso3 contracts]
  (->> (take 15 contracts)
       (keep (fn [c]
               (let [cslug (or (get c "contractSlug") (slug (get c "name" "")))]
                 (when (seq cslug)
                   (let [base (str iso3 "-" (slug cslug))
                         rkey (subs base 0 (min 64 (count base)))]
                     [rkey {"$type" "com.etzhayyim.apps.states.stateDocument"
                            "iso3" iso3 "slug" cslug
                            "title" (or (get c "nameEn") (get c "name" ""))
                            "titleLocal" (get c "name" "")
                            "basis" (get c "legalBasis" "")
                            "effectiveDate" (get c "effectiveDate" "")
                            "uri" (get c "url" "")
                            "govLevel" (get c "govLevel" "")
                            "cofogCode" (get c "cofogCode" "")
                            "contractDid" (get c "contractDid" "")
                            "tags" (get c "tags" [])
                            "createdAt" "2026-04-18T03:30:00Z"}])))))
       vec))

(defn emit-country
  "Pure: build {:profile body :procedures [[rkey body]...] :documents [...]} for one country.
  `country-map` is the COUNTRY iso3->[name region] map; returns nil if iso3 unknown."
  [country-map static-map iso3 ministries contracts bpmn-files]
  (when-let [[name region] (get country-map iso3)]
    (let [static (get static-map iso3 {})]
      {:profile (put-body repo "com.etzhayyim.apps.states.stateProfile" iso3
                          (profile-record iso3 name region static ministries contracts bpmn-files))
       :procedures (mapv (fn [[rkey rec]] (put-body repo "com.etzhayyim.apps.states.stateProcedure" rkey rec))
                         (procedure-records iso3 ministries bpmn-files))
       :documents (mapv (fn [[rkey rec]] (put-body repo "com.etzhayyim.apps.states.stateDocument" rkey rec))
                        (document-records iso3 contracts))})))
