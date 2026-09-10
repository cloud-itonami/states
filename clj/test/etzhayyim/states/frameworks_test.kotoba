(ns etzhayyim.states.frameworks-test
  (:require [clojure.test :refer [deftest is testing]]
            [etzhayyim.states.frameworks :as fw]))

(deftest add-generic-test
  (testing "fills only entries lacking complianceFrameworks; uses displayName"
    (let [data {"jpn" {"displayName" "Japan"}
                "usa" {"complianceFrameworks" ["U.S. Constitution"]}}
          [d touched] (fw/add-generic data)]
      (is (= 1 touched))
      (is (= ["Japan — National Constitution / Basic Law"
              "Access-to-information statute (where enacted)"
              "Administrative procedure legislation"]
             (get-in d ["jpn" "complianceFrameworks"])))
      (is (= ["U.S. Constitution"] (get-in d ["usa" "complianceFrameworks"]))
          "existing list untouched"))))

(deftest apply-constitutional-test
  (testing "sets curated frameworks only for iso present in data"
    (let [data {"jpn" {"displayName" "Japan"}}
          frameworks {"jpn" ["Constitution of Japan"] "xxx" ["ghost"]}
          [d touched] (fw/apply-constitutional data frameworks)]
      (is (= 1 touched))
      (is (= ["Constitution of Japan"] (get-in d ["jpn" "complianceFrameworks"])))
      (is (not (contains? d "xxx"))))))
