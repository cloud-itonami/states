# ADM2 Multi-Agent Batch 50 Report

- Date: 2026-03-04 (JST)
- Targets file: `tmp/260304-adm2-multi-agent-batch-targets-60.jsonl` (head 50 used)
- Generator: `tools/260304-adm2-multi-agent-generate.py`
- Command: `--limit 50 --go-mod-tidy`

## Result

- Generated components: `50`
- Manifest quality gate: `ok=50 fail=0`

## Design (per component)

- MCP over `/api/grpc`
- messaging endpoints: `/api/messages`, `/api/messages/send`
- Agent manifest: `/.well-known/agent.json`
- KV store: `default`
- App namespace: `kotodama-runtime`
