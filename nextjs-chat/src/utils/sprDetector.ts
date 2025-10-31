// SPR (Sparse Priming Representations) Detector
// Handles detection and activation of SPRs in content

export interface SPRData {
  guardian_point: string;
  activation_level: number;
  confidence_score: number;
  knowledge_network: {
    resonance_frequency: number;
    activation_history: string[];
    related_sprs: string[];
  };
}

export interface SPRDetection {
  detected_sprs: SPRData[];
  activation_summary: {
    total_activated: number;
    average_activation: number;
    resonance_frequency: number;
  };
  recommendations: string[];
}

export const sprDetector = {
  detectSPRs(content: string, context: any): SPRDetection {
    const detectedSPRs: SPRData[] = [];
    
    // Define known SPRs (these would normally come from the knowledge graph)
    const knownSPRs = [
      'ExecutableSpecificationPrinciple',
      'AutopoieticSystemGenesis',
      'IntegratedActionReflection',
      'SparsePrimingRepresentations',
      'VisualCognitiveDebugger',
      'ResonantInsightStrategyEngine',
      'SynergisticIntentResonanceCycle',
      'CognitiveResonanceCycle',
      'InsightSolidification',
      'VettingAgentApproval'
    ];
    
    // Detect SPRs in content
    knownSPRs.forEach(spr => {
      const activationLevel = this.calculateSPRActivation(content, spr);
      if (activationLevel > 0.3) { // Threshold for detection
        detectedSPRs.push({
          guardian_point: spr,
          activation_level: activationLevel,
          confidence_score: this.calculateConfidence(content, spr),
          knowledge_network: {
            resonance_frequency: this.calculateResonanceFrequency(spr),
            activation_history: this.getActivationHistory(spr),
            related_sprs: this.getRelatedSPRs(spr)
          }
        });
      }
    });
    
    // Sort by activation level
    detectedSPRs.sort((a, b) => b.activation_level - a.activation_level);
    
    return {
      detected_sprs: detectedSPRs,
      activation_summary: this.calculateActivationSummary(detectedSPRs),
      recommendations: this.generateRecommendations(detectedSPRs, content)
    };
  },

  calculateSPRActivation(content: string, spr: string): number {
    const lowerContent = content.toLowerCase();
    const lowerSPR = spr.toLowerCase();
    
    // Check for exact matches
    if (lowerContent.includes(lowerSPR)) {
      return 0.9;
    }
    
    // Check for partial matches
    const words = lowerSPR.split(/(?=[A-Z])/);
    let matchScore = 0;
    
    words.forEach(word => {
      if (lowerContent.includes(word.toLowerCase())) {
        matchScore += 0.2;
      }
    });
    
    // Check for semantic variations
    const semanticVariations = this.getSemanticVariations(spr);
    semanticVariations.forEach(variation => {
      if (lowerContent.includes(variation.toLowerCase())) {
        matchScore += 0.15;
      }
    });
    
    return Math.min(0.9, matchScore);
  },

  calculateConfidence(content: string, spr: string): number {
    const activationLevel = this.calculateSPRActivation(content, spr);
    const contextRelevance = this.calculateContextRelevance(content, spr);
    const semanticClarity = this.calculateSemanticClarity(content, spr);
    
    return (activationLevel * 0.5) + (contextRelevance * 0.3) + (semanticClarity * 0.2);
  },

  calculateResonanceFrequency(spr: string): number {
    // This would normally come from the knowledge graph
    // For now, return a simulated value
    return Math.random() * 0.8 + 0.2;
  },

  getActivationHistory(spr: string): string[] {
    // This would normally come from the knowledge graph
    // For now, return simulated history
    return [`${spr} activated ${Math.floor(Math.random() * 10) + 1} times in recent sessions`];
  },

  getRelatedSPRs(spr: string): string[] {
    // This would normally come from the knowledge graph
    // For now, return simulated related SPRs
    const allSPRs = [
      'ExecutableSpecificationPrinciple',
      'AutopoieticSystemGenesis',
      'IntegratedActionReflection',
      'SparsePrimingRepresentations',
      'VisualCognitiveDebugger'
    ];
    
    return allSPRs.filter(related => related !== spr).slice(0, 3);
  },

  calculateActivationSummary(detectedSPRs: SPRData[]) {
    if (detectedSPRs.length === 0) {
      return {
        total_activated: 0,
        average_activation: 0,
        resonance_frequency: 0
      };
    }
    
    const totalActivated = detectedSPRs.length;
    const averageActivation = detectedSPRs.reduce((sum, spr) => sum + spr.activation_level, 0) / totalActivated;
    const resonanceFrequency = detectedSPRs.reduce((sum, spr) => sum + spr.knowledge_network.resonance_frequency, 0) / totalActivated;
    
    return {
      total_activated: totalActivated,
      average_activation: averageActivation,
      resonance_frequency: resonanceFrequency
    };
  },

  generateRecommendations(detectedSPRs: SPRData[], content: string): string[] {
    const recommendations: string[] = [];
    
    if (detectedSPRs.length === 0) {
      recommendations.push("Consider incorporating more SPRs to enhance cognitive resonance");
      recommendations.push("Review content for alignment with established knowledge patterns");
    } else if (detectedSPRs.length < 3) {
      recommendations.push("Good SPR activation detected, consider expanding to related concepts");
    } else {
      recommendations.push("Excellent SPR coverage, focus on deepening activation levels");
    }
    
    // Check for high-confidence SPRs
    const highConfidenceSPRs = detectedSPRs.filter(spr => spr.confidence_score > 0.8);
    if (highConfidenceSPRs.length > 0) {
      recommendations.push(`Strong activation of ${highConfidenceSPRs[0].guardian_point}, leverage this for deeper insights`);
    }
    
    return recommendations;
  },

  getSemanticVariations(spr: string): string[] {
    // This would normally come from the knowledge graph
    // For now, return some common variations
    const variations: { [key: string]: string[] } = {
      'ExecutableSpecificationPrinciple': ['specification principle', 'executable principle', 'spec principle'],
      'AutopoieticSystemGenesis': ['autopoietic genesis', 'system genesis', 'self-creation'],
      'IntegratedActionReflection': ['action reflection', 'integrated reflection', 'reflection principle'],
      'SparsePrimingRepresentations': ['sparse priming', 'priming representations', 'SPR'],
      'VisualCognitiveDebugger': ['visual debugger', 'cognitive debugger', 'VCD']
    };
    
    return variations[spr] || [];
  },

  calculateContextRelevance(content: string, spr: string): number {
    // This would analyze how well the SPR fits the current context
    // For now, return a simulated value
    return Math.random() * 0.6 + 0.4;
  },

  calculateSemanticClarity(content: string, spr: string): number {
    // This would analyze the semantic clarity of the SPR in context
    // For now, return a simulated value
    return Math.random() * 0.5 + 0.5;
  }
};
