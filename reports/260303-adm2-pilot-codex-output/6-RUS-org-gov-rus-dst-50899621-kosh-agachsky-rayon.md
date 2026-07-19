**Slug Validation**
- `org-gov-rus-dst-50899621-kosh-agachsky-rayon` fits org-gov-{ISO3}-{context}-{shapeId}-{shape} scheme, unique (existing ADM2 = 0), ASCII, length 56 (<63), so ✅.

**Required Files List**
- `infra/kotodama-runtime/org-gov-rus-dst-50899621-kosh-agachsky-rayon/README.md` – pilot summary (rank 6, gap 2328, shape metadata, Apple HIG/iPad assurance).
- `infra/kotodama-runtime/org-gov-rus-dst-50899621-kosh-agachsky-rayon/values.yaml` – shared App inputs (country codes, `SHAPE_ID=50074027B11056050899621`, replica=1, endpoint host placeholder).
- `infra/kotodama-runtime/org-gov-rus-dst-50899621-kosh-agachsky-rayon/app.yaml` – App CR; `metadata.name=image stem`, namespace `kotodama-runtime`, image `ghcr.io/etzhayyim/org-gov-rus-dst-50899621-kosh-agachsky-rayon:<tag>`, env for endpoint + ADM payload.
- `infra/kotodama-runtime/org-gov-rus-dst-50899621-kosh-agachsky-rayon/service.yaml` – ClusterIP Service (port 8080) for App.
- `infra/kotodama-runtime/org-gov-rus-dst-50899621-kosh-agachsky-rayon/edge-route.yaml` – `HTTPRoute` in `edge-router-performers`, host `https://{nanoid}.etzhayyim.com/api/grpc`, parent gateway refs, backend Service.
- `infra/kotodama-runtime/org-gov-rus-dst-50899621-kosh-agachsky-rayon/kustomization.yaml` – aggregates App + Service + Route.
- Optional helper script `70-tools/70-tools/70-tools/scripts/260303-sync-50074027B11056050899621.sh` for ingestion (date-prefixed).

**K8s Manifest Skeleton Names**
- `App/org-gov-rus-dst-50899621-kosh-agachsky-rayon` (ns `kotodama-runtime`).
- `Service/org-gov-rus-dst-50899621-kosh-agachsky-rayon` (ns `kotodama-runtime`).
- `HTTPRoute/org-gov-rus-dst-50899621-kosh-agachsky-rayon` (ns `edge-router-performers`, host `xxxxx.etzhayyim.com`).

**Quality Gates Checklist**
- [ ] `metadata.name`, Service name, slug, and image stem identical.
- [ ] Image hosted at `ghcr.io/etzhayyim/org-gov-rus-dst-50899621-kosh-agachsky-rayon:<tag>`; tag pinned.
- [ ] App env exports `SHAPE_ID=50074027B11056050899621`, `COUNTRY_ISO3=RUS`, `CONNECT_ENDPOINT=https://{nanoid}.etzhayyim.com/api/grpc`.
- [ ] Service exposes port 8080 (gRPC) with `app=org-gov-rus-dst-50899621-kosh-agachsky-rayon` selector; HTTPRoute parentRefs to approved gateway; TLS secret wired.
- [ ] README captures ADM2 totals (2328 total, 0 existing, pilot gap 2328) + data provenance + Apple HIG/iPad compliance statement.
- [ ] `kustomize build infra/kotodama-runtime/org-gov-...` succeeds; `kubectl apply --dry-run=client` clean; lint for namespaces (App/Service in `kotodama-runtime`, HTTPRoute in `edge-router-performers`).
- [ ] Endpoint host nanoid reserved and DNS synced via Gateway external-dns.

**Estimated Risk**
Medium – first Russian Federation ADM2 entry (gap 2328) so naming/endpoint mistakes would block reachability, but blast radius limited to single pilot deployment.
