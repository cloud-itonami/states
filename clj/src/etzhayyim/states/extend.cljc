(ns etzhayyim.states.extend
  "Port of scripts/extend-static-final.py, extend-static-data.py, extend-static-tier3.py.

  Each extends static-profile-data.json with a curated set of additional
  countries, never overwriting an existing iso3 entry. The three differ only
  in their per-country `build` function and their embedded data map:
    - final : 15 microstates -> rich entry (addresses/contacts/desks/procedures/docs)
    - ext   : tier-2 countries -> addresses + multi contacts + optional desks
    - tier3 : remaining countries -> addresses + 1 website contact"
  (:require [etzhayyim.states.profile :as profile]
            [clojure.string :as str]))

(defn- lower3 [name] (str/lower-case (subs name 0 (min 3 (count name)))))

(defn build-final
  "Port of extend-static-final.build([name capital country website])."
  [[name capital country website]]
  {"displayName" name
   "addresses" [{"kind" "headquarters" "label" (str "Capital: " capital)
                 "addressLocality" capital "country" country}]
   "contacts" [{"kind" "website" "uri" website "label" (str name " — official portal")}]
   "desks" [{"kind" "general_inquiry" "label" (str name " — citizen inquiry") "uri" website}]
   "procedures"
   [{"id" (str (lower3 name) ".access_info") "title" "Access to Public Information" "authority" name}
    {"id" (str (lower3 name) ".passport") "title" "Passport Application / Renewal"
     "authority" (str name " — passport authority")}]
   "documentTemplates"
   [{"id" (str (str/lower-case country) ".access_info.v1")
     "title" "Access to public information request — template" "authority" name}]})

(defn build-ext
  "Port of extend-static-data.build([name capital country contacts extra-desks]).
  `contacts` is a vector of [uri label]; `extra-desks` a vector of [kind label basis authority?] or nil."
  [[name capital country contacts extra-desks]]
  {"displayName" name
   "addresses" [{"kind" "headquarters" "label" (str "Capital: " capital)
                 "addressLocality" capital "country" country}]
   "contacts" (vec (map-indexed
                    (fn [i [uri label]]
                      {"kind" (if (zero? i) "website" "portal") "uri" uri "label" label})
                    contacts))
   "desks" (vec (for [dk (or extra-desks [])]
                  {"kind" (nth dk 0) "label" (nth dk 1) "basis" (nth dk 2)
                   "authority" (if (> (count dk) 3) (nth dk 3) "")}))})

(defn build-tier3
  "Port of extend-static-tier3.build([name capital country website])."
  [[name capital country website]]
  {"displayName" name
   "addresses" [{"kind" "headquarters" "label" (str "Government seat: " capital)
                 "addressLocality" capital "country" country}]
   "contacts" [{"kind" "website" "uri" website "label" (str name " — official portal")}]})

(defn extend-with
  "Pure: for each iso3 in `entries` not already in `data`, add (build entry).
  Returns [data' added-isos]."
  [data entries build]
  (reduce
   (fn [[d added] [iso3 entry]]
     (if (contains? d iso3)
       [d added]
       [(assoc d iso3 (build entry)) (conj added iso3)]))
   [data []]
   entries))

(defn -main
  "Apply ext, then tier3, then final extensions to static-profile-data.json."
  [& args]
  (let [path (or (first args) "scripts/static-profile-data.json")
        data (profile/read-json path)
        [d1 a1] (extend-with data (profile/load-data "ext.json") build-ext)
        [d2 a2] (extend-with d1 (profile/load-data "tier3.json") build-tier3)
        [d3 a3] (extend-with d2 (profile/load-data "final.json") build-final)]
    (profile/write-json! path d3)
    (println (str "ext: " (count a1) ", tier3: " (count a2) ", final: " (count a3)
                  " -> total " (count d3)))))
