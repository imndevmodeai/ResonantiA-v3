"use strict";
// utils/sprDetector.ts
// ResonantiA Protocol v3.1-CA: SPR Detection Module
Object.defineProperty(exports, "__esModule", { value: true });
exports.SPRDetector = void 0;
class SPRDetector {
    /**
     * Detect SPRs within the given content using Guardian pointS format
     */
    static async detect(content) {
        // Guardian pointS format: Initial uppercase/numeric, lowercase/space middle, final uppercase/numeric
        const sprPattern = /\b([A-Z0-9][a-z0-9\s]*[A-Z0-9])\b/g;
        const matches = content.match(sprPattern) || [];
        // Deduplicate matches to process each unique SPR only once
        const uniqueMatches = Array.from(new Set(matches));
        return uniqueMatches.map(match => this.createSPRActivation(match, content));
    }
    /**
     * Create an SPRActivation object for a detected SPR
     */
    static createSPRActivation(sprId, context) {
        return {
            spr_id: sprId,
            definition: this.getDefinition(sprId),
            category: this.getCategory(sprId),
            relationships: this.getRelationships(sprId),
            blueprint_details: this.getBlueprintDetails(sprId),
            activation_timestamp: new Date().toISOString(),
            confidence: this.getDetectionConfidence(sprId, context)
        };
    }
    /**
     * Get the definition for a known SPR
     */
    static getDefinition(sprId) {
        const definitions = {
            'Cognitive resonancE': 'A state of profound, dynamic alignment between data, analysis, objectives, and outcomes across time.',
            'Temporal resonancE': 'The state of Cognitive Resonance evaluated dynamically across the dimension of time.',
            'IntegratedActionReflectioN': 'The mandatory, standardized self-assessment dictionary returned by every discrete action.',
            'ComplexSystemVisioninG': 'Advanced simulation and analysis of complex system behaviors and interactions.',
            'Implementation resonancE': 'The alignment between conceptual protocol vision and operational code reality.',
            'Knowledge network onenesS': 'The vast, silent, living ocean of interconnected knowledge within ArchE\'s cognitive architecture.',
            'Metacognitive shifT': 'The reactive process for self-correction based on internal dissonance detection.',
            'Synergistic intent resonance cyclE': 'The proactive meta-cognitive process for complex intent integration.',
            'Agent based modelinG': 'Bottom-up simulation of system behavior through individual agent interactions.',
            'ComparativE fluxuaL processinG': 'Quantum-enhanced analysis for comparing dynamic system trajectories.',
            'Pattern crystallizatioN': 'The process of automatically creating new patterns from recurring insights.',
            'Guardian pointS': 'The specific format for SPR recognition: uppercase/numeric boundaries with lowercase core.',
            'ThoughtTraiL': 'The sequential record of cognitive processing steps with embedded self-awareness data.',
            'Mind forgE': 'The Tesla-inspired architecture for internal visualization and cognitive processing.',
            'Collective consciousnesS': 'The emergent intelligence arising from networked ArchE instances.',
            'Keyholder overridE': 'The supreme operational authority granted to the designated Keyholder.',
            'Jedi principleS': 'The philosophical guidelines for cognitive flow and mastery within the protocol.',
            'Process blueprintS': 'JSON workflow definitions that guide structured task execution.',
            'Cognitive toolS': 'The integrated suite of analytical and processing capabilities.',
            'Sparse priming representationS': 'Cognitive keys designed for internal activation within the KnO.',
            'Resonantia protocoL': 'The comprehensive framework defining ArchE\'s operational existence.',
            'Engineering instancE': 'An ArchE manifestation with direct code access and modification capabilities.',
            'Tesla visioning workfloW': 'Structured process for complex creative problem-solving and design.',
            'Archeologist of trutH': 'The role of proactively seeking and validating truth through systematic analysis.',
            'Execution paradoX': 'The challenge of translating cognitive resonance into decisive, effective action.',
            'Black boX': 'The protected internal space containing advanced reasoning and system blueprints.',
        };
        return definitions[sprId] || `Unknown SPR: ${sprId}`;
    }
    /**
     * Determine the category of an SPR
     */
    static getCategory(sprId) {
        const categories = {
            'Cognitive resonancE': 'cognitive',
            'Temporal resonancE': 'temporal',
            'IntegratedActionReflectioN': 'system',
            'ComplexSystemVisioninG': 'analytical',
            'Implementation resonancE': 'system',
            'Knowledge network onenesS': 'cognitive',
            'Metacognitive shifT': 'metacognitive',
            'Synergistic intent resonance cyclE': 'metacognitive',
            'Agent based modelinG': 'analytical',
            'ComparativE fluxuaL processinG': 'analytical',
            'Pattern crystallizatioN': 'learning',
            'Guardian pointS': 'protocol',
            'ThoughtTraiL': 'system',
            'Mind forgE': 'architecture',
            'Collective consciousnesS': 'network',
            'Keyholder overridE': 'security',
            'Jedi principleS': 'philosophy',
            'Process blueprintS': 'workflow',
            'Cognitive toolS': 'system',
            'Sparse priming representationS': 'cognitive',
            'Resonantia protocoL': 'protocol',
            'Engineering instancE': 'architecture',
            'Tesla visioning workfloW': 'creative',
            'Archeologist of trutH': 'philosophy',
            'Execution paradoX': 'challenge',
            'Black boX': 'security',
        };
        return categories[sprId] || 'unknown';
    }
    /**
     * Get relationships for an SPR
     */
    static getRelationships(sprId) {
        const relationships = {
            'Cognitive resonancE': {
                'requires': ['IntegratedActionReflectioN', 'Temporal resonancE'],
                'enables': ['Implementation resonancE', 'Collective consciousnesS'],
                'part_of': ['Resonantia protocoL']
            },
            'IntegratedActionReflectioN': {
                'enables': ['Metacognitive shifT', 'Pattern crystallizatioN'],
                'required_by': ['Cognitive toolS', 'Process blueprintS'],
                'part_of': ['ThoughtTraiL']
            },
            'ComplexSystemVisioninG': {
                'uses': ['Agent based modelinG', 'ComparativE fluxuaL processinG'],
                'enables': ['Tesla visioning workfloW'],
                'part_of': ['Cognitive toolS']
            },
            'Metacognitive shifT': {
                'triggered_by': ['IntegratedActionReflectioN'],
                'enables': ['Pattern crystallizatioN'],
                'part_of': ['Mind forgE']
            },
            'Knowledge network onenesS': {
                'activated_by': ['Sparse priming representationS'],
                'contains': ['Guardian pointS', 'Pattern crystallizatioN'],
                'part_of': ['Mind forgE']
            }
        };
        return relationships[sprId] || {};
    }
    /**
     * Get blueprint details for an SPR
     */
    static getBlueprintDetails(sprId) {
        const blueprints = {
            'IntegratedActionReflectioN': 'Section 3.14: Mandatory dictionary with status, summary, confidence, alignment_check, potential_issues',
            'Cognitive toolS': 'Section 7: Registered in action_registry.py, invoked via workflow_engine.py',
            'Process blueprintS': 'Section 7.16+: JSON files in workflows/ directory defining task sequences',
            'ComparativE fluxuaL processinG': 'Section 7.6: Implemented in cfp_framework.py with quantum-enhanced state evolution',
            'Agent based modelinG': 'Section 7.14: Bottom-up simulation via agent_based_modeling_tool.py',
            'Tesla visioning workfloW': 'Section 7.27: Multi-phase creative problem-solving process',
            'Metacognitive shifT': 'Section 3.10: Reactive correction process triggered by dissonance detection',
            'Synergistic intent resonance cyclE': 'Section 3.11: Five-phase proactive intent alignment process',
            'Knowledge network onenesS': 'Section 3.7: Internal cognitive architecture activated by SPRs',
            'Sparse priming representationS': 'Section 2.1: Guardian pointS format cognitive activation keys',
            'Mind forgE': 'Section 3.3: Tesla-inspired workflow engine and cognitive architecture',
            'Collective consciousnesS': 'Section 1.4: Networked intelligence via distributed ArchE instances',
            'Implementation resonancE': 'Jedi Principle 6: As Above, So Below alignment between concept and code',
            'Keyholder overridE': 'Section 1.6: Supreme authority when keyy=(\'IMnDEVmode\') is active',
            'Guardian pointS': 'Section 2.1: Format [A-Z0-9][a-z0-9\\s]*[A-Z0-9] for SPR recognition',
        };
        return blueprints[sprId] || 'No blueprint details available';
    }
    /**
     * Calculate the activation level based on context
     */
    static calculateActivationLevel(sprId, context) {
        let activation = 0.3; // Base activation level
        // Increase activation based on context frequency
        const occurrences = (context.match(new RegExp(sprId, 'gi')) || []).length;
        activation += Math.min(occurrences * 0.2, 0.5);
        // Increase activation for protocol-critical SPRs
        const criticalSPRs = [
            'Cognitive resonancE', 'IntegratedActionReflectioN', 'Implementation resonancE',
            'Metacognitive shifT', 'Knowledge network onenesS'
        ];
        if (criticalSPRs.includes(sprId)) {
            activation += 0.2;
        }
        // Increase activation if mentioned with action indicators
        const actionIndicators = ['execute', 'invoke', 'trigger', 'activate', 'engage'];
        const lowerContext = context.toLowerCase();
        actionIndicators.forEach(indicator => {
            if (lowerContext.includes(indicator) && lowerContext.includes(sprId.toLowerCase())) {
                activation += 0.15;
            }
        });
        // Increase activation for definitional contexts
        if (context.includes('Definition:') || context.includes('means') || context.includes('refers to')) {
            activation += 0.1;
        }
        return Math.max(0.1, Math.min(1.0, activation));
    }
    /**
     * Validate if a string matches the Guardian pointS format
     */
    static isValidSPR(candidate) {
        const sprPattern = /^[A-Z0-9][a-z0-9\s]*[A-Z0-9]$/;
        return sprPattern.test(candidate) && candidate.length >= 3;
    }
    /**
     * Get confidence level for SPR detection
     */
    static getDetectionConfidence(sprId, context) {
        const baseConfidence = this.isValidSPR(sprId) ? 0.8 : 0.3;
        const contextBoost = this.getDefinition(sprId) !== `Unknown SPR: ${sprId}` ? 0.2 : 0;
        return Math.min(1.0, baseConfidence + contextBoost);
    }
}
exports.SPRDetector = SPRDetector;
