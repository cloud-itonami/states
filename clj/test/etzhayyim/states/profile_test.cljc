(ns etzhayyim.states.profile-test
  (:require [clojure.test :refer [deftest is testing]]
            [etzhayyim.states.profile :as p]))

(deftest slug-test
  (testing "lowercase + non-alnum collapse + trim (emit_country.slug)"
    (is (= "ministry-of-justice" (p/slug "Ministry of Justice")))
    (is (= "abc" (p/slug "  --ABC!!--  ")))
    (is (= "x" (p/slug "")))
    (is (= "x" (p/slug "???")))
    (is (= 48 (count (p/slug (apply str (repeat 100 "a"))))))))

(deftest put-body-test
  (is (= {"repo" "r" "collection" "c" "rkey" "k" "record" {"a" 1}}
         (p/put-body "r" "c" "k" {"a" 1}))))

(deftest display-name-test
  (is (= "Japan" (p/display-name {"displayName" "Japan"} "jpn")))
  (is (= "JPN" (p/display-name {} "jpn")))
  (is (= "JPN" (p/display-name {"displayName" nil} "jpn"))))

(deftest load-data-test
  (testing "embedded reference data resources load with expected sizes"
    (is (= 195 (count (p/load-data "country.json"))))
    (is (= 46 (count (p/load-data "frameworks.json"))))
    (is (= 15 (count (p/load-data "final.json"))))
    (is (thrown? #?(:clj clojure.lang.ExceptionInfo :cljs :default)
                 (p/load-data "nope.json")))))
