**Slug Validation**
- `org-gov-chn-dst-68901730-mohexian` follows `org-gov-<iso3>-dst-<shapeid>-<name>`; maps to metadata/image stem; no clashes reported → use as-is.

**Required Files List**
- `deploy/org-gov-chn-dst-68901730-mohexian/app.yaml` – App spec with `metadata.name` = slug, namespace `kotodama-runtime`, image `ghcr.io/etzhayyim/org-gov-chn-dst-68901730-mohexian:ADM2-pilot`.
- `deploy/org-gov-chn-dst-68901730-mohexian/edge-route.yaml` – `HTTPRoute` (or combined gRPC route) in `edge-router-performers`.
- `deploy/org-gov-chn-dst-68901730-mohexian/config/envoy.yaml` (or equivalent) if per-app route config required.
- `deploy/org-gov-chn-dst-68901730-mohexian/README.md` – runbook + endpoint note with nanoid placeholder.
- Optional: `deploy/org-gov-chn-dst-68901730-mohexian/kustomization.yaml` to bundle manifests for pilot rollout.

**K8s Manifest Skeleton Names**
- `App/org-gov-chn-dst-68901730-mohexian` in `kotodama-runtime`, `spec.image` pointing to `ghcr.io/etzhayyim/org-gov-chn-dst-68901730-mohexian:ADM2-pilot`, env contains `ADM2_TARGET_SHAPE_ID=17275852B82946568901730`, `ADM2_TARGET_NAME=Mohexian`.
- `HTTPRoute/org-gov-chn-dst-68901730-mohexian` (gateway: edge gateway) in `edge-router-performers`, host `mohexian.etzhayyim.com` (placeholder), backend ref = App service, `backendRefs[].filters[].requestHeaderModifier.set["x-etzhayyim-endpoint"]=https://<nanoid>.etzhayyim.com/api/grpc`.
- If service object needed: `Service/org-gov-chn-dst-68901730-mohexian` exposing App pod on gRPC/Web port.

**Quality Gates Checklist**
- `metadata.name`, container image repo/tag, and deployment slug identical.
- Image registry is `ghcr.io/etzhayyim/*`; tag pinned, no `:latest`.
- App namespace `kotodama-runtime`; edge route namespace `edge-router-performers`.
- Endpoint string uses nanoid pattern `https://xxxxx.etzhayyim.com/api/grpc`.
- Route ensures Connect gRPC-Web compatibility; no hover-only UX dependencies for future UI.
- ADM2 env vars and config reference `Mohexian` + shape ID exactly; no hard-coded legacy endpoints.
- Manifest reviews confirm zero `<style>` blocks (if Svelte surface needed later) and follow Apple HIG/iPad rules when UI assets appear.

**Estimated Risk**
- Medium: first ADM2 insert for China (gap 2391, no existing ADM2 records) means high data volume pressure; upstream schema or tiles may expose latent scaling issues despite straightforward infra scaffolding.
