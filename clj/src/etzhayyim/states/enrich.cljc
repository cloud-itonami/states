(ns etzhayyim.states.enrich
  "Port of scripts/enrich-kotodama-profiles.py.

  Merge fields from a generated stateProfile record into a per-country
  kotodama.jsonld `profile` block:
    - scalar fields  : overwrite when different
    - list-fill      : set only when the profile field is empty (preserve rich edits)
    - list-id-merge  : keep existing, append new entries by `id`"
  (:require [etzhayyim.states.profile :as profile]
            [clojure.string :as str]
            #?(:clj [clojure.java.io :as io])))

(def scalar-fields ["ministryCount" "contractCount" "bpmnCount" "dataSourceRef"])
(def list-id-fields ["procedures" "documentTemplates"])
(def list-fill-fields ["addresses" "contacts" "desks" "complianceFrameworks"])

(defn- id-merge
  "Keep `existing`, append items from `new-items` whose 'id' is not already present."
  [existing new-items]
  (let [existing (vec existing)
        existing-ids (set (keep #(when (map? %) (get % "id")) existing))]
    (loop [acc existing, ids existing-ids, items new-items]
      (if-let [item (first items)]
        (let [id (and (map? item) (get item "id"))]
          (if (and id (not (contains? ids id)))
            (recur (conj acc item) (conj ids id) (rest items))
            (recur acc ids (rest items))))
        acc))))

(defn merge-profile
  "Pure: merge stateProfile `rec` into kotodama `prof` map.
  Returns [prof' changed-count]."
  [prof rec]
  (let [step (fn [[p changed] field]
               ;; scalar
               (cond
                 (and (some #{field} scalar-fields)
                      (contains? rec field) (not= (get p field) (get rec field)))
                 [(assoc p field (get rec field)) (inc changed)]

                 (and (some #{field} list-fill-fields)
                      (seq (get rec field)) (not (seq (get p field))))
                 [(assoc p field (get rec field)) (inc changed)]

                 (some #{field} list-id-fields)
                 (let [new-items (get rec field)]
                   (if-not (seq new-items)
                     [p changed]
                     (let [existing (vec (get p field))
                           merged (id-merge existing new-items)]
                       (if (not= merged existing)
                         [(assoc p field merged) (inc changed)]
                         [p changed]))))

                 :else [p changed]))]
    (reduce step [prof 0]
            (concat scalar-fields list-fill-fields list-id-fields))))

#?(:clj
   (defn find-kotodama
     "First existing kotodama.jsonld under appview/etzhayyim-wasm-states-{iso3}-*."
     [appview-dir iso3]
     (->> (.listFiles (io/file appview-dir))
          (filter #(and (.isDirectory %)
                        (str/starts-with? (.getName %) (str "etzhayyim-wasm-states-" iso3 "-"))))
          (map #(io/file % "kotodama.jsonld"))
          (filter #(.exists %))
          first)))

#?(:clj
   (defn enrich-one
     "[iso3 status changed]. records-dir holds {iso3}.json putRecord bodies."
     [appview-dir records-dir iso3 dry-run?]
     (let [rec-file (io/file records-dir (str iso3 ".json"))]
       (if-not (.exists rec-file)
         [iso3 "skip-no-record" 0]
         (let [rec (get (profile/read-json rec-file) "record" {})
               mj-path (find-kotodama appview-dir iso3)]
           (if-not mj-path
             [iso3 "skip-no-appview" 0]
             (let [mj (profile/read-json mj-path)
                   prof (get mj "profile" {})
                   [prof' changed] (merge-profile prof rec)]
               (cond
                 (zero? changed) [iso3 "unchanged" 0]
                 dry-run? [iso3 "would-write" changed]
                 :else (do (profile/write-json! mj-path (assoc mj "profile" prof'))
                           [iso3 "written" changed])))))))))
