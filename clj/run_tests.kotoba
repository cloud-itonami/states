#!/usr/bin/env bb
;; Test runner for the etzhayyim-project-states clj port (repo rule: run_tests.clj,
;; NOT a .sh). Loads every test ns, runs clojure.test, exits non-zero on failure.
;; Usage:  bb run_tests.clj   (from this directory)  |  bb test
(require '[clojure.test :as t]
         'etzhayyim.states.profile-test
         'etzhayyim.states.frameworks-test
         'etzhayyim.states.desks-test
         'etzhayyim.states.procedures-test
         'etzhayyim.states.extend-test
         'etzhayyim.states.stubs-test
         'etzhayyim.states.enrich-test
         'etzhayyim.states.emit-records-test)

(let [{:keys [fail error]}
      (t/run-tests 'etzhayyim.states.profile-test
                   'etzhayyim.states.frameworks-test
                   'etzhayyim.states.desks-test
                   'etzhayyim.states.procedures-test
                   'etzhayyim.states.extend-test
                   'etzhayyim.states.stubs-test
                   'etzhayyim.states.enrich-test
                   'etzhayyim.states.emit-records-test)]
  (System/exit (if (pos? (+ fail error)) 1 0)))
