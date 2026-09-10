(ns etzhayyim.states.frameworks
  "Port of scripts/add-generic-frameworks.py + scripts/add-constitutional-frameworks.py.

  Both add a `complianceFrameworks` list to country profile entries in
  static-profile-data.json. `apply-constitutional` sets the rich, hand-curated
  per-country list (from frameworks.json); `add-generic` fills any still-empty
  entry with a placeholder triple so the gov tab shows >=1 framework."
  (:require [etzhayyim.states.profile :as profile]))

(defn generic-frameworks
  "The placeholder triple, parameterised on display name (add-generic-frameworks.py)."
  [name]
  [(str name " — National Constitution / Basic Law")
   "Access-to-information statute (where enacted)"
   "Administrative procedure legislation"])

(defn add-generic
  "Pure: for each entry lacking complianceFrameworks, attach the generic triple.
  Returns [data' touched-count]."
  [data]
  (reduce
   (fn [[d touched] [iso entry]]
     (if (seq (get entry "complianceFrameworks"))
       [d touched]
       (let [name (profile/display-name entry iso)]
         [(assoc-in d [iso "complianceFrameworks"] (generic-frameworks name))
          (inc touched)])))
   [data 0]
   data))

(defn apply-constitutional
  "Pure: set complianceFrameworks from the curated `frameworks` map for every
  iso present in both `frameworks` and `data`. Returns [data' touched-count].
  (add-constitutional-frameworks.py)"
  [data frameworks]
  (reduce
   (fn [[d touched] [iso fw]]
     (if (contains? d iso)
       [(assoc-in d [iso "complianceFrameworks"] fw) (inc touched)]
       [d touched]))
   [data 0]
   frameworks))

(defn -main
  "Apply constitutional then generic frameworks to static-profile-data.json."
  [& args]
  (let [path (or (first args) "scripts/static-profile-data.json")
        frameworks (profile/load-data "frameworks.json")
        [d1 c1] (apply-constitutional (profile/read-json path) frameworks)
        [d2 c2] (add-generic d1)]
    (profile/write-json! path d2)
    (println (str "constitutional frameworks: " c1 ", generic frameworks: " c2))))
