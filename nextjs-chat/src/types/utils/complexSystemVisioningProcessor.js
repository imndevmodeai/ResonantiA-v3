"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ComplexSystemVisioningProcessor = void 0;
class ComplexSystemVisioningProcessor {
    static async process(content) {
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
    static isComplexSystemVisioning(content) {
        const visioningPatterns = [
            /complex\s*system\s*visioning/i,
            /agent\s*based\s*modeling/i,
            /abm/i,
            /simulation\s*scenario/i,
            /emergent\s*behavior/i
        ];
        return visioningPatterns.some(pattern => pattern.test(content));
    }
    static extractScenarioName(content) {
        const scenarioPatterns = [
            /scenario[:\s]*([^.\n]+)/i,
            /simulation[:\s]*([^.\n]+)/i,
            /model[:\s]*([^.\n]+)/i
        ];
        for (const pattern of scenarioPatterns) {
            const match = content.match(pattern);
            if (match)
                return match[1] || match[0];
        }
        return 'Complex System Visioning Scenario';
    }
    static extractTimeHorizon(content) {
        const timePatterns = [
            /(\d+)\s*(?:year|month|week|day)s?\s*(?:simulation|horizon)/i,
            /time\s*horizon[:\s]*([^.\n]+)/i
        ];
        for (const pattern of timePatterns) {
            const match = content.match(pattern);
            if (match)
                return match[1] || match[0];
        }
        return '10 years';
    }
    static extractAgentGroups(content) {
        const agentPatterns = [
            /agent\s*group[:\s]*([^.\n]+)/gi,
            /agent\s*type[:\s]*([^.\n]+)/gi,
            /behavioral\s*entity[:\s]*([^.\n]+)/gi
        ];
        const agents = [];
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
    static extractAttributes(agentMatch) {
        const attributePatterns = [
            /attributes[:\s]*([^.\n]+)/i,
            /properties[:\s]*([^.\n]+)/i,
            /characteristics[:\s]*([^.\n]+)/i
        ];
        const attributes = [];
        attributePatterns.forEach(pattern => {
            const match = agentMatch.match(pattern);
            if (match)
                attributes.push(match[1] || match[0]);
        });
        return attributes;
    }
    static extractBehavioralRules(agentMatch) {
        const rulePatterns = [
            /behavioral\s*rules[:\s]*([^.\n]+)/gi,
            /rules[:\s]*([^.\n]+)/gi,
            /behavior[:\s]*([^.\n]+)/gi
        ];
        const rules = [];
        rulePatterns.forEach(pattern => {
            const matches = agentMatch.match(pattern);
            if (matches)
                rules.push(...matches);
        });
        return rules;
    }
    static extractInitialStates(agentMatch) {
        const statePatterns = [
            /initial\s*state[:\s]*([^.\n]+)/gi,
            /starting\s*condition[:\s]*([^.\n]+)/gi,
            /baseline\s*state[:\s]*([^.\n]+)/gi
        ];
        const states = [];
        statePatterns.forEach(pattern => {
            const matches = agentMatch.match(pattern);
            if (matches)
                states.push(...matches);
        });
        return states;
    }
    static extractHumanFactorModeling(agentMatch) {
        const hfmPatterns = [
            /fear\s*level[:\s]*([^.\n]+)/i,
            /morale[:\s]*([^.\n]+)/i,
            /risk\s*aversion[:\s]*([^.\n]+)/i,
            /adaptation[:\s]*([^.\n]+)/i
        ];
        const hfm = {};
        hfmPatterns.forEach(pattern => {
            const match = agentMatch.match(pattern);
            if (match) {
                if (pattern.source.includes('fear'))
                    hfm.fear_level_distribution = match[1] || match[0];
                if (pattern.source.includes('morale'))
                    hfm.morale_distribution = match[1] || match[0];
                if (pattern.source.includes('risk'))
                    hfm.risk_aversion_score = match[1] || match[0];
                if (pattern.source.includes('adaptation'))
                    hfm.adaptation_probability = match[1] || match[0];
            }
        });
        return Object.keys(hfm).length > 0 ? hfm : undefined;
    }
    static extractEnvironmentalFactors(content) {
        const envPatterns = [
            /environmental\s*factor[:\s]*([^.\n]+)/gi,
            /environment[:\s]*([^.\n]+)/gi,
            /external\s*factor[:\s]*([^.\n]+)/gi
        ];
        const factors = [];
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
    static extractBaselineProjection(factorMatch) {
        const baselinePattern = /baseline[:\s]*([^.\n]+)/i;
        const match = factorMatch.match(baselinePattern);
        return match ? match[1] || match[0] : 'Standard baseline projection';
    }
    static extractScenarioModifier(factorMatch) {
        const modifierPattern = /modifier[:\s]*([^.\n]+)/i;
        const match = factorMatch.match(modifierPattern);
        return match ? match[1] || match[0] : 'No scenario modification';
    }
    static extractTemporalVariation(factorMatch) {
        const variationPattern = /temporal[:\s]*([^.\n]+)/i;
        const match = factorMatch.match(variationPattern);
        return match ? match[1] || match[0] : 'Constant temporal variation';
    }
    static extractInterventionScenarios(content) {
        const interventionPatterns = [
            /intervention[:\s]*([^.\n]+)/gi,
            /scenario[:\s]*([^.\n]+)/gi
        ];
        const scenarios = [];
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
    static extractDescription(scenarioMatch) {
        const descPattern = /description[:\s]*([^.\n]+)/i;
        const match = scenarioMatch.match(descPattern);
        return match && match[1] ? match[1].trim() : 'Intervention scenario';
    }
    static extractTriggers(scenarioMatch) {
        const triggerPattern = /triggers[:\s]*([^.\n]+)/gi;
        const matches = scenarioMatch.match(triggerPattern);
        return matches || [];
    }
    static extractParameters(scenarioMatch) {
        const paramPattern = /parameters[:\s]*([^.\n]+)/i;
        const match = scenarioMatch.match(paramPattern);
        return match ? { parameters: match[1] || match[0] } : {};
    }
    static extractOutputMetrics(content) {
        const metricPatterns = [
            /output\s*metrics[:\s]*([^.\n]+)/gi,
            /metrics[:\s]*([^.\n]+)/gi,
            /measurements[:\s]*([^.\n]+)/gi
        ];
        const metrics = [];
        metricPatterns.forEach(pattern => {
            const matches = content.match(pattern);
            if (matches)
                metrics.push(...matches);
        });
        return metrics;
    }
    static generateRealismAssessment(content) {
        return {
            overall_score: this.calculateRealismScore(content),
            agent_behavior_plausibility: 0.8,
            environmental_realism: 0.7,
            intervention_effectiveness: 0.6,
            temporal_consistency: 0.9,
            assessment_notes: ['Assessment based on content analysis']
        };
    }
    static calculateRealismScore(content) {
        const realismIndicators = ['realistic', 'plausible', 'credible', 'feasible'];
        let score = 0.5;
        realismIndicators.forEach(indicator => {
            if (content.toLowerCase().includes(indicator))
                score += 0.1;
        });
        return Math.min(10, Math.max(0, score * 10));
    }
    static extractEmergencePatterns(content) {
        const emergencePatterns = [
            /emergence[:\s]*([^.\n]+)/gi,
            /emergent\s*behavior[:\s]*([^.\n]+)/gi,
            /pattern[:\s]*([^.\n]+)/gi
        ];
        const patterns = [];
        emergencePatterns.forEach(pattern => {
            const matches = content.match(pattern);
            if (matches)
                patterns.push(...matches);
        });
        return patterns;
    }
}
exports.ComplexSystemVisioningProcessor = ComplexSystemVisioningProcessor;
