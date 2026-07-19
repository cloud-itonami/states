slug validation
- `org-gov-usa-dst-53498623-highland` already kebab-case, ≤63 chars, unique stem ties to image/metadata naming → ok.

required files list
- `60-apps/etzhayyim-project-states/manifests/org-gov-usa-dst-53498623-highland-app.yaml`
- `60-apps/etzhayyim-project-states/manifests/org-gov-usa-dst-53498623-highland-route.yaml`
- `60-apps/etzhayyim-project-states/docs/org-gov-usa-dst-53498623-highland.md`

k8s manifest skeleton names
- App (namespace `kotodama-runtime`), metadata.name `org-gov-usa-dst-53498623-highland`, image `ghcr.io/etzhayyim/org-gov-usa-dst-53498623-highland:<tag>`, env/config refs for ADM2 pilot toggle, endpoint `https://<nanoid>.etzhayyim.com/api/grpc`.
- Edge HTTPRoute (namespace `edge-router-performers`), metadata.name `org-gov-usa-dst-53498623-highland`, parentRefs to edge gateway, hostnames set to `<nanoid>.etzhayyim.com`, backend refs to App service.
- Supporting ConfigMap/Secret names (if needed) prefixed `org-gov-usa-dst-53498623-highland-*` to keep namespace cleanliness.

quality gates checklist
- Metadata/image stem alignment verified (`org-gov-usa-dst-53498623-highland`).
- Container image points at `ghcr.io/etzhayyim/*` with explicit tag (no `:latest`).
- App service endpoint uses Connect gRPC-Web over `https://{nanoid}.etzhayyim.com/api/grpc`.
- Route namespace `edge-router-performers`; App in `kotodama-runtime`.
- Touch targets/layout follow Apple HIG iPad breakpoints in any UI doc section (if UI involved).
- Docs include ADM2 stats (rank 3, gap 3233) and Highland shape linkage.
- No go:embed static usage; proto references align with WIT if codegen touched.

estimated risk
- Moderate: first ADM2 entry (0 existing) so patterns untested in repo; however scope limited to manifests/docs, no external deps expected.
