# Visual & Debug Bridges (v3.5‑GP)

Scope
- Define bridges that expose workflow/task state for UI and debugging (e.g., nextjs‑chat, WS streams).

Bridges
- Structured Log Bridge: streams event envelope (§Protocol Events) over stdout/file.
- WebSocket Bridge: pushes `task.*`, `workflow.*`, and `iar.*` to subscribed clients.
- Snapshot Bridge: writes point‑in‑time JSON snapshots under `outputs/run_{id}/`.

Message Contract
```json
{
  "channel": "workflow|task|iar",
  "event": "...",
  "ts": "iso-datetime",
  "payload": {}
}
```

Security
- Read‑only by default; redact secrets; per‑run token recommended.

Integration
- UI: `nextjs-chat/` can render nodes/edges from `task.*` events.
- Server: `arche_websocket_server.py` / `arche_interface.py`.
