# Distributed Registry (v3.5‑GP)

Purpose
- Define the Arche instance registry API and records for capability discovery and scheduling.

Record Schema
```json
{
  "instance_id": "uuid",
  "version": "semver",
  "capabilities": ["cfp","abm","causal","vision"],
  "endpoints": {"rpc": "url", "events": "url"},
  "health": {"status": "up|down", "latency_ms": 0},
  "updated_at": "iso-datetime"
}
```

APIs
- `POST /instances` – register/update
- `GET /instances` – list/filter
- `GET /instances/{id}` – detail

Scheduling Hints
- Prefer instances by capability coverage and health.

Code
- `arche_registry/` (client/server), `distributed_arche_registry.py`.
