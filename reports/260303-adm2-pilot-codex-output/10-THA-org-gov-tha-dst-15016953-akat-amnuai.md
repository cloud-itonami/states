**Slug Validation**
- Proposed `org-gov-tha-dst-15016953-akat-amnuai` is lowercase, hyphenated, unique, and matches target metadata/image stem requirement; no conflicts known.

**Required Files List**
- `states/tha/akat-amnuai/README.md` – ADM2 summary, deployment references, Apple HIG/iPad UX commit notes.
- `states/tha/akat-amnuai/app.yaml` – App spec in `kotodama-runtime` namespace with metadata/image stem `org-gov-tha-dst-15016953-akat-amnuai`.
- `states/tha/akat-amnuai/edge-route.yaml` – `HTTPRoute` in `edge-router-performers` namespace pointing to Connect gRPC-Web backend.
- `states/tha/akat-amnuai/buf.gen.yaml` + proto stub or reference updates if new Connect service codegen needed.
- `states/tha/akat-amnuai/README-data.md` (optional) – ingestion notes, ADM2 total tracking (928 gap closure log).

**K8s Manifest Skeleton Names**
- `App/org-gov-tha-dst-15016953-akat-amnuai` (namespace `kotodama-runtime`, image `ghcr.io/etzhayyim/org-gov-tha-dst-15016953-akat-amnuai:<tag>`).
- `Deployment/org-gov-tha-dst-15016953-akat-amnuai` (if App wraps workloads, ensure annotations for Connect gRPC-Web).
- `Service/org-gov-tha-dst-15016953-akat-amnuai` (ClusterIP).
- `HTTPRoute/org-gov-tha-dst-15016953-akat-amnuai` (namespace `edge-router-performers`, host `https://<nanoid>.etzhayyim.com/api/grpc`).
- `ConfigMap/org-gov-tha-dst-15016953-akat-amnuai` (optional for ADM2 payload/template).

**Quality Gates Checklist**
- Image hosted at `ghcr.io/etzhayyim/...`, metadata.name matches image stem; explicit tag (no `:latest`).
- App namespace `kotodama-runtime`; HTTPRoute namespace `edge-router-performers`.
- Endpoint string follows `https://{nanoid}.etzhayyim.com/api/grpc`; Connect gRPC-Web client from `@connectrpc/connect-web`.
- UI leverages `@etzhayyim/appshellv2` + `@etzhayyim/design-system`, meets Apple HIG iPad breakpoints (md/lg/xl).
- No `<style>` blocks in Svelte; touch targets ≥44px, hover-optional interactions only.
- Git hygiene: small incremental commits, only scoped files staged.
- DNS/Gateway alignment: HTTPRoute hostnames feed external-dns, no manual DNS writes.

**Estimated Risk**
- Moderate: zero existing ADM2 assets for Thailand means new pipelines, namespace wiring, and Connect endpoint scaffolding must be created from scratch; potential scheduling dependencies but manageable with template reuse.
