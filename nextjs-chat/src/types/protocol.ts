// types/protocol.ts
// ResonantiA Protocol v3.1-CA TypeScript Interface Definitions

export interface IARReflection {
  status: 'Success' | 'Failure' | 'Partial' | 'Skipped';
  summary: string;
  confidence: number; // 0.0-1.0
  alignment_check: 'Aligned' | 'Potentially Misaligned' | 'N/A';
  potential_issues: string[];
  raw_output_preview: string;
  tactical_resonance: number | undefined;
  crystallization_potential: number | undefined;
  timestamp: string;
}

export interface SPRActivation {
  spr_id: string; // Guardian pointS format
  definition: string;
  category: string;
  relationships: Record<string, any>;
  blueprint_details: string | undefined;
  activation_timestamp: string;
  confidence: number;
}

export interface TemporalContext {
  time_horizon: string;
  historical_context: string[];
  future_projection: string[];
  current_state: string;
  temporal_dynamics: string[];
  causal_lag_detection: string[] | undefined;
}

export interface MetaCognitiveState {
  metacognitive_shift_active: boolean;
  sirc_phase: 'Intent Deconstruction' | 'Resonance Mapping' | 'Blueprint Generation' | 'Harmonization Check' | 'Integrated Actualization' | undefined;
  crc_active: boolean;
  dissonance_detected: boolean;
  correction_applied: string | undefined;
}

export interface AgentGroup {
  name: string;
  attributes: string[];
  behavioral_rules: string[];
  initial_states: string[];
  human_factor_modeling: HumanFactorModeling | undefined;
}

export interface HumanFactorModeling {
  fear_level_distribution: string;
  morale_distribution: string;
  risk_aversion_score: string;
  adaptation_probability: string;
}

export interface EnvironmentalFactor {
  name: string;
  baseline_projection: string;
  scenario_modifier: string;
  temporal_variation: string;
}

export interface InterventionScenario {
  name: string;
  description: string;
  implementation_triggers: string[];
  parameters: Record<string, any>;
}

export interface RealismAssessment {
  overall_score: number;
  agent_behavior_plausibility: number;
  environmental_realism: number;
  intervention_effectiveness: number;
  temporal_consistency: number;
  assessment_notes: string[];
}

export interface ComplexSystemVisioningData {
  scenario_name: string;
  time_horizon: string;
  agent_groups: AgentGroup[];
  environmental_factors: EnvironmentalFactor[];
  intervention_scenarios: InterventionScenario[];
  output_metrics: string[];
  realism_assessment: RealismAssessment;
  emergence_patterns: string[];
}

export interface ImplementationResonance {
  code_documentation_alignment: number;
  crdsp_compliance: boolean;
  engineering_instance_status: 'active' | 'inactive' | 'error';
  pending_updates: string[];
  validation_status: 'pass' | 'fail' | 'pending';
}

export interface EnhancedMessage {
  id: string;
  content: string;
  timestamp: string;
  sender: 'user' | 'arche';
  message_type: 'chat' | 'iar' | 'spr' | 'temporal' | 'meta' | 'complex' | 'implementation' | 'protocol_init' | 'error';
  iar: IARReflection | undefined;
  spr_activations: SPRActivation[] | undefined;
  temporal_context: TemporalContext | undefined;
  meta_cognitive_state: MetaCognitiveState | undefined;
  complex_system_visioning: ComplexSystemVisioningData | undefined;
  implementation_resonance: ImplementationResonance | undefined;
  thought_trail: string[] | undefined;
  protocol_compliance: boolean;
  protocol_version: string | undefined;
  protocol_init: {
    message: string;
    capabilities: string[];
    status: string;
  } | undefined;
  protocol_error: {
    message: string;
    error: string;
    fallback_mode: boolean;
  } | undefined;
}

// Type aliases for backward compatibility and cleaner imports
export type IAR_Data = IARReflection;
export type SPR_Data = SPRActivation;
export type Temporal_Data = TemporalContext;
export type MetaCognitive_Data = MetaCognitiveState;
export type ComplexSystemVisioning_Data = ComplexSystemVisioningData;
export type ImplementationResonance_Data = ImplementationResonance; 