**Slug Validation**
- `org-gov-col-dst-88124839-san-rafael` follows `org-gov-<iso3>-dst-<shape-id-suffix>-<shape-name>`; unique in repo (existing ADM2 = 0) so no collision.

**Required Files List**
- `60-apps/etzhayyim-project-states/manifests/org-gov-col-dst-88124839-san-rafael.yaml` (App + EdgeRoute bundle, namespaces per constraints).
- `60-apps/etzhayyim-project-states/config/org-gov-col-dst-88124839-san-rafael.json` (shape metadata and ADM2 tracking).
- `60-apps/etzhayyim-project-states/90-docs/260303-org-gov-col-dst-88124839-san-rafael.md` (pilot note, date-stamped per Codex rules).

**K8s Manifest Skeleton Names**
- `App`: `metadata.name: org-gov-col-dst-88124839-san-rafael`, `metadata.namespace: kotodama-runtime`, `spec.image: ghcr.io/etzhayyim/org-gov-col-dst-88124839-san-rafael:latest`, `spec.endpoint: https://<nanoid>.etzhayyim.com/api/grpc`.
- `EdgeRoute` (HTTPRoute/GRPCRoute as required): `metadata.name: org-gov-col-dst-88124839-san-rafael`, `metadata.namespace: edge-router-performers`, routes to App service, ensure Connect gRPC-Web config.

**Quality Gates Checklist**
- ADM2 inputs synced: 1122 total, gap 1122 → first insert documented.
- Namespace policy: App in `kotodama-runtime`, Edge route in `edge-router-performers`; no default usage.
- Image + metadata name parity verified; GHCR host enforced.
- Endpoint uses nanoid pattern at `etzhayyim.com` per convention.
- Touch targets/layout: confirm Svelte front-end adheres to Apple HIG + four breakpoints if UI needed.
- No legacy harbor endpoints or per-subdomain APIs; Connect gRPC-Web wiring confirmed.
- Documentation filename dated `260303-*` to satisfy temporary artifact rule.

**Estimated Risk**
Medium: first ADM2 entry (gap 1122) so lacks prior templates; coordination required for accurate shape metadata and correct nanoid provisioning.
