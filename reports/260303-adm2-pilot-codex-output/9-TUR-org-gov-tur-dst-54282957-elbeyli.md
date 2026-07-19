**1) Slug Validation**
- `org-gov-tur-dst-54282957-elbeyli` follows `org|gov-countrycode-tier-id-shapename` pattern, uses Turkey ISO `tur`, and ends with shape name in lowercase; no collisions detected in repo (existing ADM2 count 0), so slug approved.

**2) Required Files List**
- `states/adm2/org-gov-tur-dst-54282957-elbeyli/README.md` – pilot overview, boundary references, ADM2 data pointers.
- `states/adm2/org-gov-tur-dst-54282957-elbeyli/app.yaml` – App spec in `kotodama-runtime` namespace; metadata/image stem `org-gov-tur-dst-54282957-elbeyli`.
- `states/adm2/org-gov-tur-dst-54282957-elbeyli/edge-route.yaml` – `HTTPRoute` in `edge-router-performers` namespace.
- `states/adm2/org-gov-tur-dst-54282957-elbeyli/kustomization.yaml` – ties the App + edge route for deployment.
- `states/adm2/org-gov-tur-dst-54282957-elbeyli/values.json` – ADM2 metadata (rank 9, gap 999, target shape id/name).

**3) K8s Manifest Skeleton Names**
- App: `kind: App`, `metadata.name: org-gov-tur-dst-54282957-elbeyli`, `spec.image: ghcr.io/etzhayyim/org-gov-tur-dst-54282957-elbeyli:pilot`, `spec.runtime.namespace: kotodama-runtime`.
- ServiceAccount/RoleBinding (if needed): names derived from slug for least-privilege.
- Edge route: `kind: HTTPRoute`, `metadata.name: org-gov-tur-dst-54282957-elbeyli`, `metadata.namespace: edge-router-performers`, backend ref to App service.
- ConfigMap/Secret placeholders for ADM2 dataset references (prefixed with slug) if data ingestion requires them.

**4) Quality Gates Checklist**
- slug + metadata match: stem consistent across README, manifests, image.
- namespace policy: App → `kotodama-runtime`, HTTPRoute → `edge-router-performers`.
- endpoint: Connect gRPC-Web client points to `https://<nanoid>.etzhayyim.com/api/grpc`; document nanoid in README.
- image source: `ghcr.io/etzhayyim/*`, tag not `latest`, push workflow updated.
- ADM2 data: confirm `adm2_total = 999` and `gap = 999` documented; include shape ID `54988432B86465154282957`.
- HIG/iPad layout note for any future WASM frontends (even if not built yet).
- Kustomization validated via `kustomize build` (dry run) before commit.

**5) Estimated Risk**
- Medium: first ADM2 entry for Turkey with large gap (999) means sourcing accuracy and schema alignment are high-effort; failure would leave ADM2 coverage empty, but blast radius limited to pilot namespace.
