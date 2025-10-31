export interface IARReflection {
    status: 'ok' | 'warn' | 'error';
    confidence: number;
    alignment_check?: 'aligned' | 'concern' | 'violation';
    potential_issues?: string[];
    notes?: string;
  }
  
  export interface SPRActivation {
    spr_id: string;
    confidence?: number;
    context_excerpt?: string;
  }
  
  export interface TemporalContext {
    timeframe?: string;
    forecasts?: Record<string, number>;
    caveats?: string[];
  }
  
  export interface MetaCognitiveState {
    sirc_active?: boolean;
    shift_active?: boolean;

    issues?: string[];
  }
  
  export interface ComplexSystemVisioningData {
    abm_summary?: string;
    indicators?: Record<string, number>;
  }
  
  export interface ImplementationResonance {
    crdsp_pass?: boolean;
    docs_updated?: boolean;
    items?: { artifact: string; status: 'ok' | 'missing' | 'outdated' }[];
  }
  
  export interface ProtocolInit {
    session_id: string;
    version: string;
  }
  
  export interface ProtocolError {
    message: string;
    error?: string;
    fallback_mode?: boolean;
  }
  
  export type EnhancedMessageType =
    | 'chat'
    | 'iar'
    | 'spr'
    | 'temporal'
    | 'meta'
    | 'complex'
    | 'implementation'
    | 'protocol_init'
    | 'error';
  
  export interface Message {
    id: string;
    content: string;
    timestamp: string;
    sender: 'user' | 'arche';
    message_type: EnhancedMessageType;
    protocol_compliance: boolean;
    protocol_version?: string;
    iar?: IARReflection;
    spr_activations?: SPRActivation[];
    temporal_context?: TemporalContext;
    meta_cognitive_state?: MetaCognitiveState;
    complex_system_visioning?: ComplexSystemVisioningData;
    implementation_resonance?: ImplementationResonance;
    thought_trail?: string[];
    protocol_init?: ProtocolInit;
    protocol_error?: ProtocolError;
  }
  
  export interface LogEntry {
    id: string;
    t: number;
    type: string;
    message: string;
    metadata?: Record<string, unknown>;
    severity?: 'info' | 'success' | 'warn' | 'error';
  }
  
  export interface IAREnvironment {
      // Define the structure for IAR environment data
  }
