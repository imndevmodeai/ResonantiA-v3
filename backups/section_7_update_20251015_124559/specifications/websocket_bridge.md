# Living Specification: WebSocket Bridge for VCD

## Overview

The **WebSocket Bridge for VCD** is ArchE's critical communication infrastructure that bridges engine and protocol streams to UI clients, enriching raw data frames through sophisticated protocol processors and broadcasting them as standardized EnhancedMessage and VcdEvent structures. This bridge serves as the central nervous system for ArchE's real-time observability, enabling seamless communication between the core cognitive engine and the Visual Cognitive Debugger interface.

The bridge operates through a comprehensive processing pipeline that transforms incoming text frames through six specialized processors: IARProcessor (Integrated Action Reflection), SPRDetector (Sparse Priming Representation detection), TemporalAnalyzer (temporal context analysis), MetaCognitiveTracker (meta-cognitive state tracking), ComplexSystemVisioningProcessor (complex system analysis), and ImplementationResonanceTracker (CRDSP compliance tracking). The system includes robust connection management with exponential backoff (250ms to 5s cap), heartbeat mechanisms (20s intervals), multi-client fanout capabilities, session scoping, comprehensive security measures (origin allowlists, rate limiting, secret redaction), and extensive testing protocols for unit, integration, and end-to-end validation.

## Purpose
Bridge engine/protocol streams to UI clients; enrich frames with protocol processors (IAR/SPR/Temporal/Meta/Complex/CRDSP) and broadcast as `EnhancedMessage`/`VcdEvent`.

## Responsibilities
- Accept inbound user/control frames from UI.
- Initialize/maintain upstream connection to ArchE (or tail engine stdout).
- Process text frames through processors; emit enriched envelopes/events.
- Heartbeat, backoff, multi-client fanout, session scoping.

## Interfaces
- Server: `WEBSOCKET_URL` (e.g., `ws://localhost:3004`).
- Client→Server: `{ kind: 'user_input'|'control', payload:any }`.
- Server→Client: `EnhancedMessage` and `VcdEvent` JSON frames.

## Processing Pipeline (reference `webSocketServer.js`)
1. IARProcessor.process(content) → `iar`.
2. SPRDetector.detect(content) → `spr_activations`.
3. TemporalAnalyzer.analyze(content) → `temporal_context`.
4. MetaCognitiveTracker.track(content) → `meta_cognitive_state`.
5. ComplexSystemVisioningProcessor.process(content) → `complex_system_visioning`.
6. ImplementationResonanceTracker.track() → `implementation_resonance`.
7. Build `EnhancedMessage`; also stream `VcdEvent` for task transitions and thought trail.

## Connection Policy
- Backoff 250ms, 500ms, 1s, 2s, 4s, 5s cap.
- Heartbeat ping every 20s; drop timeout 45s; broadcast status.
- Max clients configurable; per-session room by `session_id`.

## Security
- Origin allowlist; optional bearer token header; rate limit per IP.
- Redact secrets; size cap; JSON parse try/catch with error frames.

## Testing
- Unit: processors mocked; frame transformation tests.
- Integration: two clients receive identical sequences; disconnect/reconnect.
- E2E: Phoenix playback; assert workflow start/success and expected markers.

## CRDSP Links
- Code: `webSocketServer.js`, client `nextjs-chat/src/hooks/useWebSocket.ts`.
- Specs: `visual_cognitive_debugger_ui.md`, `protocol_event_schema.md`.
