(ns etzhayyim.states.procedures-test
  (:require [clojure.test :refer [deftest is testing]]
            [etzhayyim.states.procedures :as proc]))

(deftest standard-procs-test
  (let [ps (proc/standard-procs "ABC" "Aplandia")]
    (is (= 3 (count ps)))
    (is (= "abc.access_info" (get (first ps) "id")) "iso lowercased")
    (is (= "Aplandia — passport authority" (get (second ps) "authority")))))

(deftest standard-doc-test
  (is (= [{"id" "abc.access_info_request.v1"
           "title" "Request for access to public information — template"
           "authority" "Aplandia"
           "basis" "Access-to-information statute"}]
         (proc/standard-doc "abc" "Aplandia"))))

(deftest add-standard-test
  (testing "skips RICH and entries that already have procedures; appends docs"
    (let [data {"abc" {"displayName" "Aplandia"
                       "documentTemplates" [{"id" "abc.pre.v1"}]}
                "jpn" {"displayName" "Japan"}            ;; in RICH -> skip
                "xyz" {"displayName" "X" "procedures" [{"id" "xyz.keep"}]}}
          rich #{"jpn"}
          [d touched] (proc/add-standard data rich)]
      (is (= ["abc"] touched))
      (is (= 3 (count (get-in d ["abc" "procedures"]))))
      (is (= 2 (count (get-in d ["abc" "documentTemplates"]))) "appended, not replaced")
      (is (nil? (get-in d ["jpn" "procedures"])))
      (is (= [{"id" "xyz.keep"}] (get-in d ["xyz" "procedures"]))))))
