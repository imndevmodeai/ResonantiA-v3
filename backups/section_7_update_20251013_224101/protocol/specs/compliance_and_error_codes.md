# Compliance and Error Codes (v3.5‑GP)

IAR Compliance Levels
- L0: Engine‑synthesized IAR only
- L1: Tool returns partial IAR, engine augments
- L2: Tool returns full IAR with confidence & alignment
- L3: Full IAR + policy hooks + telemetry

Error Code Families
- RES-ERR-ACTN-#### – Action execution failures
- RES-ERR-SCHE-#### – Schema/validation issues
- RES-ERR-WFLW-#### – Workflow resolution/errors
- RES-ERR-POLI-#### – Policy/ethics vetting failures
- RES-ERR-BRID-#### – Bridge/transport errors

Error Object
```json
{
  "code": "RES-ERR-ACTN-0001",
  "message": "provider timeout",
  "details": {"provider": "serpapi", "timeout_ms": 30000}
}
```

Compliance Checks
- Presence of IAR in every task result
- Alignment check not `fail` for successful tasks
- Confidence below threshold triggers escalation or gate
