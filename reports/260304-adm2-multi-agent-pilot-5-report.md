# ADM2 Multi-Agent Pilot (5) Report

- Date: 2026-03-04 (JST)
- Project: `60-apps/etzhayyim-project-states`
- Generator: `tools/260304-adm2-multi-agent-generate.py`
- Targets: `tmp/260304-adm2-multi-agent-pilot-5-targets.jsonl`

## Implemented Components

1. `org-gov-moz-dst-80491119-alto-molocue`
2. `org-gov-ago-dst-64942932-ambriz`
3. `org-gov-dom-dst-38647260-azua-de-compostela`
4. `org-gov-nic-dst-18162683-municipio-nueva-guinea`
5. `org-gov-lao-dst-54903685-add`

## Per-Component Design (Common)

- gRPC endpoint: `https://{nanoid}.etzhayyim.com/api/grpc`
- MCP protocol: JSON-RPC 2.0 over `/api/grpc`
- messaging endpoint: `https://{nanoid}.etzhayyim.com/api/messages/send`
- agent manifest endpoint: `/.well-known/agent.json`
- KV store: kotodama key-value store `default`
  - seed key: `division:default`
  - message key prefix: `messages:*`

## Generated Files (per component)

- `main.go`
- `go.mod` / `go.sum`
- `kotodama.toml`
- `wit/world.wit`
- `deploy config`
- `<slug>.jsonld`
- `agent.json`

## Validation

- `70-tools/70-tools/70-tools/scripts/260303-check-wasm-manifests.sh <component>/main.go`
- Result: 5/5 passed

## Notes

- `/api/mcp` path is not exposed; MCP is served via `/api/grpc` to match endpoint convention.
- `deploy config` namespace is `kotodama-runtime` (no `default` namespace usage).
