(ns etzhayyim.states.enrich-test
  (:require [clojure.test :refer [deftest is testing]]
            [etzhayyim.states.enrich :as enrich]))

(deftest scalar-merge-test
  (testing "scalar fields overwrite when different, count changes"
    (let [[p changed] (enrich/merge-profile {"ministryCount" 1}
                                            {"ministryCount" 9 "contractCount" 3})]
      (is (= 9 (get p "ministryCount")))
      (is (= 3 (get p "contractCount")))
      (is (= 2 changed)))))

(deftest list-fill-test
  (testing "list-fill only sets when profile field empty"
    (let [[p changed] (enrich/merge-profile {"contacts" [{"x" 1}]}
                                            {"contacts" [{"y" 2}] "desks" [{"d" 1}]})]
      (is (= [{"x" 1}] (get p "contacts")) "non-empty preserved")
      (is (= [{"d" 1}] (get p "desks")) "empty filled")
      (is (= 1 changed)))))

(deftest id-merge-test
  (testing "procedures merged by id; existing kept, new appended"
    (let [[p changed] (enrich/merge-profile
                       {"procedures" [{"id" "a"} {"id" "b"}]}
                       {"procedures" [{"id" "b"} {"id" "c"} {"no-id" 1}]})]
      (is (= [{"id" "a"} {"id" "b"} {"id" "c"}] (get p "procedures")))
      (is (= 1 changed))))
  (testing "no change when nothing new"
    (let [[_ changed] (enrich/merge-profile {"procedures" [{"id" "a"}]}
                                            {"procedures" [{"id" "a"}]})]
      (is (= 0 changed)))))

(deftest unchanged-test
  (is (= [{} 0] (enrich/merge-profile {} {}))))
