import { ComplexSystemVisioningData, AgentGroup, EnvironmentalFactor, InterventionScenario, HumanFactorModeling } from '@/types/protocol';

export class ComplexSystemVisioningProcessor {
  static async process(content: string): Promise<ComplexSystemVisioningData | undefined> {
    // Check if content contains complex system visioning indicators
    if (!this.isComplexSystemVisioning(content)) {
      return undefined;
    }

    return {
      scenario_name: this.extractScenarioName(content),
      time_horizon: this.extractTimeHorizon(content),
      agent_groups: this.extractAgentGroups(content),
      environmental_factors: this.extractEnvironmentalFactors(content),
      intervention_scenarios: this.extractInterventionScenarios(content),
      output_metrics: this.extractOutputMetrics(content),
      realism_assessment: this.generateRealismAssessment(content),
      emergence_patterns: this.extractEmergencePatterns(content)
    };
  }

  private static isComplexSystemVisioning(content: string): boolean {
    const visioningPatterns = [
      /complex\s*system\s*visioning/i,
      /agent\s*based\s*modeling/i,
      /abm/i,
      /simulation\s*scenario/i,
      /emergent\s*behavior/i
    ];
    
    return visioningPatterns.some(pattern => pattern.test(content));
  }

  private static extractScenarioName(content: string): string {
    const scenarioPatterns = [
      /scenario[:\s]*([^.\n]+)/i,
      /simulation[:\s]*([^.\n]+)/i,
      /model[:\s]*([^.\n]+)/i
    ];
    
    for (const pattern of scenarioPatterns) {
      const match = content.match(pattern);
      if (match) return match[1] || match[0];
    }
    
    return 'Complex System Visioning Scenario';
  }

  private static extractTimeHorizon(content: string): string {
    const timePatterns = [
      /(\d+)\s*(?:year|month|week|day)s?\s*(?:simulation|horizon)/i,
      /time\s*horizon[:\s]*([^.\n]+)/i
    ];
    
    for (const pattern of timePatterns) {
      const match = content.match(pattern);
      if (match) return match[1] || match[0];
    }
    
    return '10 years';
  }

  private static extractAgentGroups(content: string): AgentGroup[] {
    const agentPatterns = [
      /agent\s*group[:\s]*([^.\n]+)/gi,
      /agent\s*type[:\s]*([^.\n]+)/gi,
      /behavioral\s*entity[:\s]*([^.\n]+)/gi
    ];
    
    const agents: AgentGroup[] = [];
    agentPatterns.forEach(pattern => {
      const matches = content.match(pattern);
      if (matches) {
        matches.forEach(match => {
          agents.push({
            name: match,
            attributes: this.extractAttributes(match),
            behavioral_rules: this.extractBehavioralRules(match),
            initial_states: this.extractInitialStates(match),
            human_factor_modeling: this.extractHumanFactorModeling(match)
          });
        });
      }
    });
    
    return agents;
  }

  private static extractAttributes(agentMatch: string): string[] {
    const attributePatterns = [
      /attributes[:\s]*([^.\n]+)/i,
      /properties[:\s]*([^.\n]+)/i,
      /characteristics[:\s]*([^.\n]+)/i
    ];
    
    const attributes: string[] = [];
    attributePatterns.forEach(pattern => {
      const match = agentMatch.match(pattern);
      if (match) attributes.push(match[1] || match[0]);
    });
    
    return attributes;
  }

  private static extractBehavioralRules(agentMatch: string): string[] {
    const rulePatterns = [
      /behavioral\s*rules[:\s]*([^.\n]+)/gi,
      /rules[:\s]*([^.\n]+)/gi,
      /behavior[:\s]*([^.\n]+)/gi
    ];
    
    const rules: string[] = [];
    rulePatterns.forEach(pattern => {
      const matches = agentMatch.match(pattern);
      if (matches) rules.push(...matches);
    });
    
    return rules;
  }

  private static extractInitialStates(agentMatch: string): string[] {
    const statePatterns = [
      /initial\s*state[:\s]*([^.\n]+)/gi,
      /starting\s*condition[:\s]*([^.\n]+)/gi,
      /baseline\s*state[:\s]*([^.\n]+)/gi
    ];
    
    const states: string[] = [];
    statePatterns.forEach(pattern => {
      const matches = agentMatch.match(pattern);
      if (matches) states.push(...matches);
    });
    
    return states;
  }

  private static extractHumanFactorModeling(agentMatch: string): HumanFactorModeling | undefined {
    const hfmPatterns = [
      /fear\s*level[:\s]*([^.\n]+)/i,
      /morale[:\s]*([^.\n]+)/i,
      /risk\s*aversion[:\s]*([^.\n]+)/i,
      /adaptation[:\s]*([^.\n]+)/i
    ];
    
    const hfm: Partial<HumanFactorModeling> = {};
    hfmPatterns.forEach(pattern => {
      const match = agentMatch.match(pattern);
      if (match) {
        if (pattern.source.includes('fear')) hfm.fear_level_distribution = match[1] || match[0];
        if (pattern.source.includes('morale')) hfm.morale_distribution = match[1] || match[0];
        if (pattern.source.includes('risk')) hfm.risk_aversion_score = match[1] || match[0];
        if (pattern.source.includes('adaptation')) hfm.adaptation_probability = match[1] || match[0];
      }
    });
    
    return Object.keys(hfm).length > 0 ? hfm as HumanFactorModeling : undefined;
  }

  private static extractEnvironmentalFactors(content: string): EnvironmentalFactor[] {
    const envPatterns = [
      /environmental\s*factor[:\s]*([^.\n]+)/gi,
      /environment[:\s]*([^.\n]+)/gi,
      /external\s*factor[:\s]*([^.\n]+)/gi
    ];
    
    const factors: EnvironmentalFactor[] = [];
    envPatterns.forEach(pattern => {
      const matches = content.match(pattern);
      if (matches) {
        matches.forEach(match => {
          factors.push({
            name: match,
            baseline_projection: this.extractBaselineProjection(match),
            scenario_modifier: this.extractScenarioModifier(match),
            temporal_variation: this.extractTemporalVariation(match)
          });
        });
      }
    });
    
    return factors;
  }

  private static extractBaselineProjection(factorMatch: string): string {
    const baselinePattern = /baseline[:\s]*([^.\n]+)/i;
    const match = factorMatch.match(baselinePattern);
    return match ? match[1] || match[0] : 'Standard baseline projection';
  }

  private static extractScenarioModifier(factorMatch: string): string {
    const modifierPattern = /modifier[:\s]*([^.\n]+)/i;
    const match = factorMatch.match(modifierPattern);
    return match ? match[1] || match[0] : 'No scenario modification';
  }

  private static extractTemporalVariation(factorMatch: string): string {
    const variationPattern = /temporal[:\s]*([^.\n]+)/i;
    const match = factorMatch.match(variationPattern);
    return match ? match[1] || match[0] : 'Constant temporal variation';
  }

  private static extractInterventionScenarios(content: string): InterventionScenario[] {
    const interventionPatterns = [
      /intervention[:\s]*([^.\n]+)/gi,
      /scenario[:\s]*([^.\n]+)/gi
    ];
    
    const scenarios: InterventionScenario[] = [];
    interventionPatterns.forEach(pattern => {
      const matches = content.match(pattern);
      if (matches) {
        matches.forEach(match => {
          scenarios.push({
            name: match,
            description: this.extractDescription(match),
            implementation_triggers: this.extractTriggers(match),
            parameters: this.extractParameters(match)
          });
        });
      }
    });
    
    return scenarios;
  }

  private static extractDescription(scenarioMatch: string): string {
    const descPattern = /description[:\s]*([^.\n]+)/i;
    const match = scenarioMatch.match(descPattern);
    return match && match[1] ? match[1].trim() : 'Intervention scenario';
  }

  private static extractTriggers(scenarioMatch: string): string[] {
    const triggerPattern = /triggers[:\s]*([^.\n]+)/gi;
    const matches = scenarioMatch.match(triggerPattern);
    return matches || [];
  }

  private static extractParameters(scenarioMatch: string): Record<string, any> {
    const paramPattern = /parameters[:\s]*([^.\n]+)/i;
    const match = scenarioMatch.match(paramPattern);
    return match ? { parameters: match[1] || match[0] } : {};
  }

  private static extractOutputMetrics(content: string): string[] {
    const metricPatterns = [
      /output\s*metrics[:\s]*([^.\n]+)/gi,
      /metrics[:\s]*([^.\n]+)/gi,
      /measurements[:\s]*([^.\n]+)/gi
    ];
    
    const metrics: string[] = [];
    metricPatterns.forEach(pattern => {
      const matches = content.match(pattern);
      if (matches) metrics.push(...matches);
    });
    
    return metrics;
  }

  private static generateRealismAssessment(content: string) {
    return {
      overall_score: this.calculateRealismScore(content),
      agent_behavior_plausibility: 0.8,
      environmental_realism: 0.7,
      intervention_effectiveness: 0.6,
      temporal_consistency: 0.9,
      assessment_notes: ['Assessment based on content analysis']
    };
  }

  private static calculateRealismScore(content: string): number {
    const realismIndicators = ['realistic', 'plausible', 'credible', 'feasible'];
    let score = 0.5;
    
    realismIndicators.forEach(indicator => {
      if (content.toLowerCase().includes(indicator)) score += 0.1;
    });
    
    return Math.min(10, Math.max(0, score * 10));
  }

  private static extractEmergencePatterns(content: string): string[] {
    const emergencePatterns = [
      /emergence[:\s]*([^.\n]+)/gi,
      /emergent\s*behavior[:\s]*([^.\n]+)/gi,
      /pattern[:\s]*([^.\n]+)/gi
    ];
    
    const patterns: string[] = [];
    emergencePatterns.forEach(pattern => {
      const matches = content.match(pattern);
      if (matches) patterns.push(...matches);
    });
    
    return patterns;
  }
} 