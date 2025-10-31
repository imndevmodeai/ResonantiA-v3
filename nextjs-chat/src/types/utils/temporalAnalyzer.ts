import { TemporalContext } from '@/types/protocol';

export class TemporalAnalyzer {
  static async analyze(content: string): Promise<TemporalContext> {
    return {
      time_horizon: this.extractTimeHorizon(content),
      historical_context: this.extractHistoricalContext(content),
      future_projection: this.extractFutureProjection(content),
      current_state: this.extractCurrentState(content),
      temporal_dynamics: this.extractTemporalDynamics(content),
      causal_lag_detection: this.extractCausalLagDetection(content)
    };
  }

  private static extractTimeHorizon(content: string): string {
    const timePatterns = [
      /(\d+)\s*(?:year|month|week|day)s?\s*(?:ahead|forward|projection)/i,
      /time\s*horizon[:\s]*([^.\n]+)/i,
      /(\d+)\s*(?:year|month|week|day)\s*analysis/i
    ];
    
    for (const pattern of timePatterns) {
      const match = content.match(pattern);
      if (match) return match[1] || match[0];
    }
    
    return '5 years'; // Default time horizon
  }

  private static extractHistoricalContext(content: string): string[] {
    const historicalPatterns = [
      /historical\s*context[:\s]*([^.\n]+)/gi,
      /past\s*(?:data|trends)[:\s]*([^.\n]+)/gi,
      /previous\s*(?:analysis|results)[:\s]*([^.\n]+)/gi
    ];
    
    const contexts: string[] = [];
    historicalPatterns.forEach(pattern => {
      const matches = content.match(pattern);
      if (matches) contexts.push(...matches);
    });
    
    return contexts;
  }

  private static extractFutureProjection(content: string): string[] {
    const futurePatterns = [
      /future\s*(?:projection|forecast)[:\s]*([^.\n]+)/gi,
      /predicted\s*(?:outcome|result)[:\s]*([^.\n]+)/gi,
      /expected\s*(?:trend|change)[:\s]*([^.\n]+)/gi
    ];
    
    const projections: string[] = [];
    futurePatterns.forEach(pattern => {
      const matches = content.match(pattern);
      if (matches) projections.push(...matches);
    });
    
    return projections;
  }

  private static extractCurrentState(content: string): string {
    const currentPatterns = [
      /current\s*state[:\s]*([^.\n]+)/i,
      /present\s*situation[:\s]*([^.\n]+)/i,
      /now[:\s]*([^.\n]+)/i
    ];
    
    for (const pattern of currentPatterns) {
      const match = content.match(pattern);
      if (match) return match[1] || match[0];
    }
    
    return 'Current state analysis in progress';
  }

  private static extractTemporalDynamics(content: string): string[] {
    const dynamicsPatterns = [
      /temporal\s*dynamics[:\s]*([^.\n]+)/gi,
      /time\s*evolution[:\s]*([^.\n]+)/gi,
      /dynamic\s*changes[:\s]*([^.\n]+)/gi
    ];
    
    const dynamics: string[] = [];
    dynamicsPatterns.forEach(pattern => {
      const matches = content.match(pattern);
      if (matches) dynamics.push(...matches);
    });
    
    return dynamics;
  }

  private static extractCausalLagDetection(content: string): string[] {
    const causalPatterns = [
      /causal\s*lag[:\s]*([^.\n]+)/gi,
      /time\s*delay[:\s]*([^.\n]+)/gi,
      /lagged\s*effect[:\s]*([^.\n]+)/gi
    ];
    
    const causalLags: string[] = [];
    causalPatterns.forEach(pattern => {
      const matches = content.match(pattern);
      if (matches) causalLags.push(...matches);
    });
    
    return causalLags;
  }
} 