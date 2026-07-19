(ns etzhayyim.states.emit-records-test
  (:require [clojure.test :refer [deftest is testing]]
            [etzhayyim.states.emit-records :as emit]))

(deftest read-ndjson-test
  (is (= [{"a" 1} {"b" 2}]
         (emit/read-ndjson "{\"a\":1}\n\n {\"b\":2} \nnot-json\n")))
  (is (= [] (emit/read-ndjson nil))))

(def ministries
  [{"path" "moj" "name" "法務省" "nameEn" "Ministry of Justice"
    "contract" "設置法" "website" "https://moj.go.jp/" "orgTier" "ministry" "tags" ["legal"]}
   {"name" "外務省" "nameEn" "MOFA"}])

(def contracts
  [{"contractSlug" "shochiho" "name" "設置法" "nameEn" "Establishment Act"
    "legalBasis" "law" "url" "https://e.gov" "govLevel" "national"}])

(deftest inline-procedures-test
  (let [ps (emit/inline-procedures "jpn" ministries #{"moj.bpmn"})]
    (is (= 2 (count ps)))
    (is (= "jpn.moj" (get (first ps) "id")))
    (is (= "60-apps/etzhayyim-project-states/data/gov/jpn/bpmn/moj.bpmn"
           (get (first ps) "bpmnRef")) "bpmnRef set when file present")
    (is (nil? (get (second ps) "bpmnRef")) "no bpmn -> nil")))

(deftest procedure-records-test
  (let [recs (emit/procedure-records "jpn" ministries #{})]
    (is (= 2 (count recs)))
    (is (= "jpn-moj" (ffirst recs)) "rkey = iso3-slug(path)")
    (is (= "ministry" (get (second (first recs)) "orgTier")))))

(deftest document-records-test
  (let [recs (emit/document-records "jpn" contracts)]
    (is (= 1 (count recs)))
    (is (= "jpn-shochiho" (ffirst recs)))
    (is (= "Establishment Act" (get (second (first recs)) "title")))))

(deftest emit-country-test
  (testing "full country emission with put-body wrapping"
    (let [country {"jpn" ["Japan" "east_asia"]}
          static {"jpn" {"displayName" "Government of Japan" "addresses" [{"k" 1}]}}
          out (emit/emit-country country static "jpn" ministries contracts #{"moj.bpmn"})]
      (is (= "com.etzhayyim.apps.states.stateProfile"
             (get-in out [:profile "collection"])))
      (is (= "states.etzhayyim.com" (get-in out [:profile "repo"])))
      (is (= "Government of Japan" (get-in out [:profile "record" "displayName"])))
      (is (= 2 (get-in out [:profile "record" "ministryCount"])))
      (is (= 2 (count (:procedures out))))
      (is (= 1 (count (:documents out))))))
  (testing "unknown iso3 -> nil"
    (is (nil? (emit/emit-country {} {} "zzz" [] [] #{})))))
