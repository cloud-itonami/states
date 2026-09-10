(ns etzhayyim.states.extend-test
  (:require [clojure.test :refer [deftest is testing]]
            [etzhayyim.states.extend :as ext]))

(deftest build-final-test
  (let [e (ext/build-final ["Republic of Malta" "Valletta" "MT" "https://www.gov.mt/"])]
    (is (= "Republic of Malta" (get e "displayName")))
    (is (= "mt.access_info.v1" (get-in e ["documentTemplates" 0 "id"])) "doc id uses lowercased country")
    (is (= "rep.access_info" (get-in e ["procedures" 0 "id"])) "proc id uses name[:3].lower()")
    (is (= "Valletta" (get-in e ["addresses" 0 "addressLocality"])))))

(deftest build-ext-test
  (let [e (ext/build-ext ["State of Qatar" "Doha" "QA"
                          [["https://gco.gov.qa/" "Gov Comms"] ["https://hukoomi.gov.qa/" "Hukoomi"]]
                          nil])]
    (is (= "website" (get-in e ["contacts" 0 "kind"])))
    (is (= "portal" (get-in e ["contacts" 1 "kind"])) "non-first contacts are portals")
    (is (= [] (get e "desks")))))

(deftest build-tier3-test
  (let [e (ext/build-tier3 ["Georgia" "Tbilisi" "GE" "https://www.gov.ge/"])]
    (is (= "Government seat: Tbilisi" (get-in e ["addresses" 0 "label"])))
    (is (= 1 (count (get e "contacts"))))
    (is (nil? (get e "desks")))))

(deftest extend-with-test
  (testing "never overwrites an existing iso3"
    (let [data {"mlt" {"displayName" "PRE-EXISTING"}}
          entries {"mlt" ["Malta" "Valletta" "MT" "x"]
                   "smr" ["San Marino" "San Marino" "SM" "y"]}
          [d added] (ext/extend-with data entries ext/build-tier3)]
      (is (= ["smr"] added))
      (is (= "PRE-EXISTING" (get-in d ["mlt" "displayName"])))
      (is (= "San Marino" (get-in d ["smr" "displayName"]))))))
