(ns etzhayyim.states.procedures
  "Port of scripts/add-tier3-procedures.py.

  Adds 3 standard procedures (access-to-info / passport / civil registration)
  plus 1 document template to tier-3 countries (those with only minimal static
  data and no existing procedures). Countries in the RICH set are skipped."
  (:require [etzhayyim.states.profile :as profile]
            [clojure.string :as str]))

(defn standard-procs
  "Port of standard_procs(iso3, name)."
  [iso3 name]
  (let [iso (str/lower-case iso3)]
    [{"id" (str iso ".access_info")
      "title" "Access to Public Information / Right to Know"
      "authority" (str name " — each public authority")
      "basis" "Constitutional or administrative access-to-information provision"}
     {"id" (str iso ".passport")
      "title" "Passport Application / Renewal"
      "authority" (str name " — passport authority")
      "basis" "Immigration / nationality law"}
     {"id" (str iso ".civil_registration")
      "title" "Civil Registration — birth / marriage / death"
      "authority" (str name " — civil registry office")
      "basis" "Civil registration statute"}]))

(defn standard-doc
  "Port of standard_doc(iso3, name)."
  [iso3 name]
  [{"id" (str iso3 ".access_info_request.v1")
    "title" "Request for access to public information — template"
    "authority" name
    "basis" "Access-to-information statute"}])

(defn add-standard
  "Pure: add standard procs + doc to non-RICH entries that have no procedures.
  `rich` is a set of iso3 strings. Returns [data' touched-isos]."
  [data rich]
  (reduce
   (fn [[d touched] [iso3 entry]]
     (if (or (contains? rich iso3) (seq (get entry "procedures")))
       [d touched]
       (let [name (profile/display-name entry iso3)
             entry' (-> entry
                        (assoc "procedures" (standard-procs iso3 name))
                        (assoc "documentTemplates"
                               (into (vec (get entry "documentTemplates" []))
                                     (standard-doc iso3 name))))]
         [(assoc d iso3 entry') (conj touched iso3)])))
   [data []]
   data))

(defn -main
  [& args]
  (let [path (or (first args) "scripts/static-profile-data.json")
        rich (set (profile/load-data "rich.json"))
        [d touched] (add-standard (profile/read-json path) rich)]
    (profile/write-json! path d)
    (println (str "added standard procs/docs to " (count touched) " countries"))))
