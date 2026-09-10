(ns etzhayyim.states.desks
  "Port of scripts/add-generic-desks.py.

  For countries without desks, add a generic general_inquiry desk pointing to
  their primary website contact (first kind=website, else first contact)."
  (:require [etzhayyim.states.profile :as profile]))

(defn primary-contact
  "next((c for c in contacts if c.kind=='website'), contacts[0])"
  [contacts]
  (or (first (filter #(= "website" (get % "kind")) contacts))
      (first contacts)))

(defn add-generic
  "Pure: add a general_inquiry desk to every entry that has contacts but no
  desks. Returns [data' touched-count]."
  [data]
  (reduce
   (fn [[d touched] [iso3 entry]]
     (let [contacts (get entry "contacts")]
       (if (or (seq (get entry "desks")) (not (seq contacts)))
         [d touched]
         (let [primary (primary-contact contacts)
               desk {"kind" "general_inquiry"
                     "label" (str (profile/display-name entry iso3) " — citizen inquiry")
                     "uri" (get primary "uri" "")}]
           [(assoc-in d [iso3 "desks"] [desk]) (inc touched)]))))
   [data 0]
   data))

(defn -main
  [& args]
  (let [path (or (first args) "scripts/static-profile-data.json")
        [d c] (add-generic (profile/read-json path))]
    (profile/write-json! path d)
    (println (str "added generic desks to " c " countries"))))
