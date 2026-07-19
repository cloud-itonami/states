(ns etzhayyim.states.desks-test
  (:require [clojure.test :refer [deftest is testing]]
            [etzhayyim.states.desks :as desks]))

(deftest primary-contact-test
  (is (= {"kind" "website" "uri" "w"}
         (desks/primary-contact [{"kind" "portal" "uri" "p"} {"kind" "website" "uri" "w"}])))
  (is (= {"kind" "portal" "uri" "p"}
         (desks/primary-contact [{"kind" "portal" "uri" "p"}]))
      "falls back to first contact when no website"))

(deftest add-generic-test
  (testing "adds desk only to entries with contacts but no desks"
    (let [data {"jpn" {"displayName" "Japan"
                       "contacts" [{"kind" "website" "uri" "https://japan.go.jp/"}]}
                "usa" {"displayName" "USA" "desks" [{"kind" "x"}]
                       "contacts" [{"kind" "website" "uri" "u"}]}
                "nul" {"displayName" "Nowhere"}}
          [d touched] (desks/add-generic data)]
      (is (= 1 touched))
      (is (= [{"kind" "general_inquiry"
               "label" "Japan — citizen inquiry"
               "uri" "https://japan.go.jp/"}]
             (get-in d ["jpn" "desks"])))
      (is (= [{"kind" "x"}] (get-in d ["usa" "desks"])) "existing desks untouched")
      (is (nil? (get-in d ["nul" "desks"])) "no contacts -> skipped"))))
