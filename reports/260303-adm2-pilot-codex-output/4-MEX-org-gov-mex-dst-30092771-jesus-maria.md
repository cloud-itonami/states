**Slug Validation**
- `org-gov-mex-dst-30092771-jesus-maria` follows the `{org}-{sector}-{iso2?}-{type}-{nanoid}-{region}` pattern, uses lowercase kebab-case, and no conflicts reported in repo (existing ADM2 = 0).
- Nanoid `30092771` aligns with required endpoint convention (`https://30092771.etzhayyim.com/api/grpc`) and can be reused across manifests.

**Required Files List**
- `states/adm2/mexico/jesus-maria/README.md` – pilot brief, gap context, runbook links.
- `states/adm2/mexico/jesus-maria/org-gov-mex-dst-30092771-jesus-maria.app.yaml` – App CR (namespace `kotodama-runtime`).
- `states/adm2/mexico/jesus-maria/org-gov-mex-dst-30092771-jesus-maria.edge-route.yaml` – Edge HTTPRoute (namespace `edge-router-performers`).
- `states/adm2/mexico/jesus-maria/org-gov-mex-dst-30092771-jesus-maria.values.json` – runtime config (endpoint, geo metadata, B2 buckets, etc.).
- `states/adm2/mexico/jesus-maria/260303-gap-notes.md` – dated checklist/log for ADM2 coverage progress.

**K8s Manifest Skeleton Names**
- App: `org-gov-mex-dst-30092771-jesus-maria`
  - `metadata.name`: `org-gov-mex-dst-30092771-jesus-maria`
  - `spec.image`: `ghcr.io/etzhayyim/org-gov-mex-dst-30092771-jesus-maria:<<tag>>` (stem matches metadata).
  - `spec.template.env`: include `CONNECT_ENDPOINT=https://30092771.etzhayyim.com/api/grpc`, `OBJSTORE_SITE_BUCKETS=jesus-maria`.
- Edge HTTPRoute: `org-gov-mex-dst-30092771-jesus-maria-route`
  - Hostname `jesus-maria.etzhayyim.com` (or shared subdomain per DNS strategy).
  - Backend ref → App service in `kotodama-runtime`.
  - Annotations enforce Connect gRPC-Web, touch-action hints for iPad UI if needed.

**Quality Gates Checklist**
- Slug + metadata match, NanoID reused consistently.
- Namespaces: App → `kotodama-runtime`, HTTPRoute → `edge-router-performers`.
- Container image from `ghcr.io/etzhayyim/*` with explicit tag; `imagePullSecrets: ghcr-pull-secret`.
- Endpoint respects `https://{nanoid}.etzhayyim.com/api/grpc`.
- UI plan references Apple HIG / iPad breakpoints; Svelte uses Tailwind + `@etzhayyim` components, no `<style>` blocks.
- Storage/backing services (Quickwit, B2) follow prescribed endpoints.
- README documents gap (2457 total, 0 existing → full backlog) and single-writer deploy discipline.
- Dated scratch/log file created (e.g., `260303-gap-notes.md`).
- `go:embed` removal script untouched unless required.
- Stage/commit scope limited to new ADM2 assets; keep worktree tidy (<50 files).

**Estimated Risk**
- Medium: entirely new ADM2 footprint (2457-unit gap) plus zero prior assets means high surface for data/geo errors; mitigated via tight namespace/image conventions and small, incremental commits.
