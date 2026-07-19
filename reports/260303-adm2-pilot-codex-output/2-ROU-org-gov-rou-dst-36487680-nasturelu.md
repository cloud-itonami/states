**Slug Validation**
- `org-gov-rou-dst-36487680-nasturelu` follows `org-gov-{iso3}-dst-{geom-id}-{adm2-name}`; ids match target (ROU, 36487680, NASTURELU). No duplicates reported (existing ADM2 count 0). Stem safe for metadata/image names.

**Required Files List**
- `deploy/kotodama/org-gov-rou-dst-36487680-nasturelu.app.yaml` – App spec (namespace `kotodama-runtime`, image pulled from `ghcr.io/etzhayyim/org-gov-rou-dst-36487680-nasturelu`, endpoint `https://<nanoid>.etzhayyim.com/api/grpc`).
- `deploy/edge/org-gov-rou-dst-36487680-nasturelu.hhroute.yaml` – Edge HTTPRoute in `edge-router-performers`, referencing kotodama service.
- `deploy/env/org-gov-rou-dst-36487680-nasturelu.configmap.yaml` – ConfigMap for ADM metadata (country, rank, adm2_total, gap).

**K8s Manifest Skeleton Names**
- `App/org-gov-rou-dst-36487680-nasturelu` (ns `kotodama-runtime`).
- `Service/org-gov-rou-dst-36487680-nasturelu` (ns `kotodama-runtime`) to expose kotodama port.
- `HTTPRoute/org-gov-rou-dst-36487680-nasturelu` (ns `edge-router-performers`) with hostname `<nanoid>.etzhayyim.com`, backend reference to service.
- `ConfigMap/org-gov-rou-dst-36487680-nasturelu` (ns `kotodama-runtime`) for pilot metadata.

**Quality Gates Checklist**
- Image built/pushed to `ghcr.io/etzhayyim/org-gov-rou-dst-36487680-nasturelu:<tag>`; metadata.name matches stem.
- App env vars/config wired from ConfigMap (rank=2, adm2_total=3235, gap=3235, target_shape_id).
- HTTPRoute enforces Connect gRPC-Web path `POST /api/grpc/*`, TLS cert references existing edge secret, hostname matches endpoint rule.
- Service ports expose kotodama listener (default 3000) with `touch-action: manipulation` UI compliance noted.
- CI verifies buf codegen alignment and linters/test suites clean before deploy.
- Deployment doc includes Apple HIG/iPad layout note and safe-area meta tag confirmation.

**Estimated Risk**
- Medium: new ADM2 region with large gap (3235 units) and zero existing coverage; misconfiguration could block ingestion, but scope limited to single pilot and clear naming reduces blast radius.
