**1) slug validation**
- `org-gov-jpn-dst-37401071-ine` is unique across repo (existing ADM2 count is 0), follows `org-gov-{iso3}-dst-{shapeIdSuffix}-{name}` convention, safe to adopt as both metadata.name and image stem.

**2) required files list**
- `kotodama/org-gov-jpn-dst-37401071-ine.kotodama.toml` (Kotodama app manifest referencing `ghcr.io/etzhayyim/org-gov-jpn-dst-37401071-ine:<tag>` and `https://{nanoid}.etzhayyim.com/api/grpc`)
- `deploy/.../org-gov-jpn-dst-37401071-ine-app.yaml` (App CRD, namespace `kotodama-runtime`)
- `deploy/edge-route/org-gov-jpn-dst-37401071-ine-http-route.yaml` (HTTPRoute, namespace `edge-router-performers`)
- `proto/etzhayyim/states/v1/org-gov-jpn-dst-37401071-ine.proto` (placeholder proto for ADM2 API surface if new methods required)
- `26203-ine-adm2-notes.md` (dated scratchpad for ingest notes; optional but required if keeping local context)

**3) k8s manifest skeleton names**
- App: `org-gov-jpn-dst-37401071-ine` (metadata.name matches image stem, namespace `kotodama-runtime`)
- HTTPRoute: `org-gov-jpn-dst-37401071-ine-route` (namespace `edge-router-performers`, parent refs to Edge Gateway, host `*.etzhayyim.com`)
- Supporting Secret/ConfigMap if needed: `org-gov-jpn-dst-37401071-ine-env` (namespace aligned with consumer workload)

**4) quality gates checklist**
- kotodama image hosted at `ghcr.io/etzhayyim/org-gov-jpn-dst-37401071-ine:<tag>`; no Harbor usage.
- App references Connect gRPC-Web endpoint `https://{nanoid}.etzhayyim.com/api/grpc` and uses `@connectrpc/connect-web`.
- Edge HTTPRoute uses Gateway API, namespace `edge-router-performers`, hostnames configured for `external-dns`.
- No default-namespace workloads; App runs in `kotodama-runtime`.
- AppShell v2 layout rules + iPad breakpoints honored in any wasm UI touched.
- Metadata names, labels, image stem all match slug.
- Secrets mounted from `infra-secrets` namespace if operational creds required.
- Build pipeline pushes to GHCR with explicit tags; `ghcr-pull-secret` referenced.

**5) estimated risk**
- Medium: ADM2 gap is large (1745 units) so ingestion load is high, but pilot focuses on single target (Ine) with known shape ID; primary uncertainty is availability of authoritative Ine boundaries and ensuring Connect gRPC exposure aligns with downstream consumers.
