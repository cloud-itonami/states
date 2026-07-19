**Slug Validation**
- `org-gov-bra-dst-83675112-alta-floresta-d-oeste` follows org-gov-{iso3}-{adm}-{shapeId}-{slug} pattern, is lowercase, hyphen-delimited, unique, and matches target ADM2; ✅ use as metadata.name + image stem.

**Required Files List**
- `deploy/.../org-gov-bra-dst-83675112-alta-floresta-d-oeste.yaml`: App CR with namespace `kotodama-runtime`, image `ghcr.io/etzhayyim/org-gov-bra-dst-83675112-alta-floresta-d-oeste:<<tag>>`, endpoint `https://<nanoid>.etzhayyim.com/api/grpc`.
- `deploy/edge-route/org-gov-bra-dst-83675112-alta-floresta-d-oeste.yaml`: `GRPCRoute` or `HTTPRoute` in namespace `edge-router-performers` pointing to App service, honoring 4 breakpoint UX + HIG notes in annotations if needed.
- `docs/adm2/org-gov-bra-dst-83675112-alta-floresta-d-oeste.md`: Pilot item brief (rank, gap, deployment notes).
- Optional helper script/report `260303-adm2-bra-alta-floresta-d-oeste.md` if interim data capture is needed (follows dated prefix rule).

**K8s Manifest Skeleton Names**
- `App/org-gov-bra-dst-83675112-alta-floresta-d-oeste` (ns `kotodama-runtime`).
- `Service/org-gov-bra-dst-83675112-alta-floresta-d-oeste` (ns `kotodama-runtime`, target for route).
- `GRPCRoute/org-gov-bra-dst-83675112-alta-floresta-d-oeste` (ns `edge-router-performers`, host `*.etzhayyim.com`).
- If telemetry needed: `ServiceMonitor/org-gov-bra-dst-83675112-alta-floresta-d-oeste` (optional).

**Quality Gates Checklist**
- App image/tag hosted on `ghcr.io/etzhayyim/*`, stem exactly slug.
- Endpoint uses `https://{nanoid}.etzhayyim.com/api/grpc`; no legacy subdomains.
- K8s namespaces: `kotodama-runtime` for compute, `edge-router-performers` for routing.
- HIG/iPad UI + Connect gRPC-Web enforced in wasm code references.
- No default namespace resources; ensure fsGroup/secret rules respected if storage introduced.
- git hygiene: stage/commit only touched files, keep <50 work files dirty.

**Estimated Risk**
- Medium: first ADM2 entry (gap 5,570) so schema mistakes or namespace mismatch could block future bulk onboarding; careful review of naming + endpoints mitigates.
