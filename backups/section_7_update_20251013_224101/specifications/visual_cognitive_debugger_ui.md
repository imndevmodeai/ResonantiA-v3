# Living Specification: Visual Cognitive Debugger (VCD) UI

## Overview

The **Visual Cognitive Debugger (VCD) UI** is ArchE's sophisticated real-time introspection and observability interface, providing comprehensive visualization of ArchE's cognitive processes, protocol execution, and Phoenix operations. Built on Next.js with React 18 and TypeScript, this system renders Thought Trails, IAR reflections, SPR activations, Temporal Resonance, Meta-cognition (SIRC/Shift), ComplexSystemVisioning, and Implementation Resonance/CRDSP data in an intuitive, interactive interface.

The VCD UI operates through a WebSocket-based data flow architecture that receives EnhancedMessage envelopes and VcdEvent timeline atoms, validates them against TypeScript schemas, stores them in a centralized state management system, and renders them through specialized components. Key components include Chat (layout and panel management), MessageList (EnhancedMessage rendering with badges and expansion), ChatInput (input handling with meta-command support), ProtocolFlow (phase pipeline visualization), ThoughtTrailGraph (timeline and reasoning trail display), and Canvas (ReactFlow-based task and SPR dependency visualization). The system includes comprehensive security measures, testing protocols, and integration with ArchE's workflow engine and autopoietic genesis protocol.

## Purpose
Real-time, observable introspection of ArchE cognition and protocol execution for Phoenix and normal operation. Renders Thought Trails, IAR reflections, SPR activations, Temporal Resonance, Meta-cognition (SIRC/Shift), ComplexSystemVisioning, and Implementation Resonance/CRDSP.

## Architecture
- Next.js (React 18, TS) client at `nextjs-chat/`.
- Data flow: WebSocket → schema validation → store → components.
- Event model: `EnhancedMessage` (envelope) + `VcdEvent` (timeline).

## Environment
- `WEBSOCKET_URL`, `PROTOCOL_VERSION`, `KEYHOLDER_OVERRIDE_ACTIVE` (already exposed in next.config.js).
- Reconnect policy: backoff 250ms→5s cap; heartbeat ~20s.

## Schemas (TS)
```ts
export interface IARReflection { status:'ok'|'warn'|'error'; confidence:number; alignment_check?:'aligned'|'concern'|'violation'; potential_issues?:string[]; notes?:string; }
export interface SPRActivation { spr_id:string; confidence?:number; context_excerpt?:string; }
export interface TemporalContext { timeframe?:string; forecasts?:Record<string,number>; caveats?:string[]; }
export interface MetaCognitiveState { sirc_active?:boolean; shift_active?:boolean; issues?:string[]; }
export interface ComplexSystemVisioningData { abm_summary?:string; indicators?:Record<string,number>; }
export interface ImplementationResonance { crdsp_pass?:boolean; docs_updated?:boolean; items?:{artifact:string; status:'ok'|'missing'|'outdated'}[]; }
export interface ProtocolInit { session_id:string; version:string; }
export interface ProtocolError { message:string; error?:string; fallback_mode?:boolean; }
export type EnhancedMessageType = 'chat'|'iar'|'spr'|'temporal'|'meta'|'complex'|'implementation'|'protocol_init'|'error';
export interface EnhancedMessage { id:string; content:string; timestamp:string; sender:'user'|'arche'; message_type:EnhancedMessageType; protocol_compliance:boolean; protocol_version?:string; iar?:IARReflection; spr_activations?:SPRActivation[]; temporal_context?:TemporalContext; meta_cognitive_state?:MetaCognitiveState; complex_system_visioning?:ComplexSystemVisioningData; implementation_resonance?:ImplementationResonance; thought_trail?:string[]; protocol_init?:ProtocolInit; protocol_error?:ProtocolError; }
export interface VcdEvent { id:string; t:number; type:string; message:string; metadata?:Record<string,unknown>; severity?:'info'|'success'|'warn'|'error'; }
```

## Components
- `Chat.tsx`: layout, panel toggles.
- `MessageList.tsx`: `EnhancedMessage` render with badges/expand.
- `ChatInput.tsx`: input; supports meta-commands (e.g., `/phoenix start`).
- `ProtocolFlow.tsx`: phase pipeline (IAR→SPR→Temporal→Meta→Complex→CRDSP).
- `ThoughtTrailGraph.tsx`: timeline of `VcdEvent` + reasoning trail.
- `Canvas.tsx`: ReactFlow: tasks, SPRs, dependencies.

## State
Store (Context/Zustand): messages, events, connection, filters, session.
Selectors: badge counts, avg confidence, last phase status, error presence.

## Rendering Rules
- Confidence badge: red <0.4, amber <0.75, green ≥0.75.
- Protocol error banner when `protocol_compliance=false` or `protocol_error`.
- Keyholder override ribbon when `KEYHOLDER_OVERRIDE_ACTIVE==='true'`.

## Security
No secrets; redact sensitive substrings; escape HTML; reject `file://`.

## Testing
- Unit: schema guards; component snapshots.
- Integration: mocked WS playback; disconnect banner; phase badge asserts.
- E2E: Phoenix playback → ProtocolInit → Task… → WorkflowSuccess.

## CRDSP Links
- Code: `nextjs-chat/*`, `webSocketServer.js`.
- Specs: `protocol_event_schema.md`, `workflow_engine.md`, `autopoietic_genesis_protocol.md`.
