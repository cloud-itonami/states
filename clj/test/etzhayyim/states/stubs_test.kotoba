(ns etzhayyim.states.stubs-test
  (:require [clojure.test :refer [deftest is testing]]
            [etzhayyim.states.stubs :as stubs]))

(deftest nanoid-for-test
  (is (= "g0vjpn01" (stubs/nanoid-for "jpn")))
  (is (= "g0vjpn01" (stubs/nanoid-for "JPN")) "lowercased"))

(deftest make-stub-test
  (let [s (stubs/make-stub "jpn" "Japan")]
    (testing "top-level invariants"
      (is (= "did:web:jpn.state.etzhayyim.com" (get s "@id")))
      (is (= "g0vjpn01" (get s "nanoid")))
      (is (= "gov-jpn" (get s "name")))
      (is (= "states" (get s "project"))))
    (testing "profile block (AI agent disclaimer fields)"
      (is (= "JP" (get-in s ["profile" "avatar"])) "first 2 of upper iso")
      (is (true? (get-in s ["profile" "isBot"])))
      (is (= "Japan" (get-in s ["profile" "displayName"])))
      (is (= "government" (get-in s ["profile" "category"]))))
    (testing "routes + triggers"
      (is (= "jpn.state.etzhayyim.com" (get-in s ["routes" 0 "host"])))
      (is (= 7 (count (get-in s ["triggers" "subscribeRepos" "collections"])))))))
