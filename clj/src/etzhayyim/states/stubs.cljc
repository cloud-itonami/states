(ns etzhayyim.states.stubs
  "Port of scripts/create-missing-stubs.py.

  Create minimal appview stub `kotodama.jsonld` files for countries present in
  static-profile-data.json that lack an appview dir. Only kotodama.jsonld is
  written; src/app.ts and wrangler.jsonc remain absent (deploy will fail until
  added) — the stub is enough for enrich-kotodama-profiles to work."
  (:require [etzhayyim.states.profile :as profile]
            [clojure.string :as str]
            #?(:clj [clojure.java.io :as io])))

(defn nanoid-for
  "Port of nanoid_for(iso): g0v{iso}01 (4-3-2 = 8 chars)."
  [iso]
  (str "g0v" (str/lower-case iso) "01"))

(defn make-stub
  "Port of make_stub(iso, display_name) — the minimal kotodama.jsonld map."
  [iso display-name]
  (let [nanoid (nanoid-for iso)]
    {"@context" "https://etzhayyim.com/ns/kotodama/v1"
     "@id" (str "did:web:" iso ".state.etzhayyim.com")
     "convoSystemPrompt" (str "You are the " display-name
                              " AI Agent. You represent government organizations as path-based DIDs. Respond professionally.")
     "governance" {"raci" "responsible" "classification" "public" "complianceFrameworks" []}
     "kpi" ["GovOrg DID registration count"]
     "name" (str "gov-" iso)
     "nanoid" nanoid
     "performerType" "service"
     "profile" {"avatar" (subs (str/upper-case iso) 0 (min 2 (count iso)))
                "banner" "#888888"
                "capabilities" ["gov-actor-registry" "path-did-resolution"]
                "category" "government"
                "country" iso
                "contract" "Constitutional / basic law"
                "description" (str display-name " — path-based DID registry (minimal stub; expand for ministries).")
                "displayName" display-name
                "isBot" true
                "agentType" "autonomous"}
     "project" "states"
     "routes" [{"host" (str iso ".state.etzhayyim.com") "paths" ["/"] "tls" true}]
     "runtimeType" "worker"
     "space" {"channels" [{"default" true "description" (str display-name " activity feed")
                           "kind" "public" "name" (str "gov-" iso "-feed")}]
              "description" (str display-name " — AI Agent registry")
              "historyVisibility" "world-readable"
              "joinRule" "public"
              "name" display-name}
     "triggers" {"subscribeRepos"
                 {"collections" ["app.bsky.feed.post" "app.bsky.feed.like"
                                 "app.bsky.graph.follow" "com.etzhayyim.apps.site.wet"
                                 "com.etzhayyim.apps.site.wat" "com.etzhayyim.apps.site.page"
                                 "com.etzhayyim.apps.site.domain"]}}
     "uiType" "yoro"
     "version" "1.0.0"}))

#?(:clj
   (defn existing-isos
     "Set of iso3 codes that already have an appview dir
     (etzhayyim-wasm-states-{iso}-{nanoid}); the iso is the 5th '-' segment."
     [appview-dir]
     (->> (.listFiles (io/file appview-dir))
          (filter #(.isDirectory %))
          (map #(.getName %))
          (filter #(str/starts-with? % "etzhayyim-wasm-states-"))
          (keep (fn [n] (let [parts (str/split n #"-")]
                          (when (>= (count parts) 5) (nth parts 4)))))
          set)))

#?(:clj
   (defn -main
     [& args]
     (let [app-root (or (first args) "60-apps/etzhayyim-project-states")
           appview (str app-root "/appview")
           static (profile/read-json (str app-root "/scripts/static-profile-data.json"))
           existing (existing-isos appview)
           created (atom [])]
       (doseq [[iso entry] static :when (not (contains? existing iso))]
         (let [name (profile/display-name entry iso)
               dir (io/file appview (str "etzhayyim-wasm-states-" iso "-" (nanoid-for iso)))]
           (.mkdirs dir)
           (profile/write-json! (io/file dir "kotodama.jsonld") (make-stub iso name))
           (swap! created conj iso)))
       (println (str "created " (count @created) " stub kotodama.jsonld files")))))
