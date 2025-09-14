// utils/iarProcessor.ts
// ResonantiA Protocol v3.1-CA: IAR Processing Module

import { IARReflection } from '@/types/protocol';

export class IARProcessor {
  /**
   * Process message content and extract/generate IAR data
   */
  static async process(content: string, context: any): Promise<IARReflection | null> {
    // Look for existing IAR patterns in the content
    const existingIAR = this.extractExistingIAR(content);
    if (existingIAR) {
      return existingIAR;
    }

    // Generate IAR based on content analysis
    return this.generateIAR(content, context);
  }

  /**
   * Extract existing IAR patterns from content
   */
  private static extractExistingIAR(content: string): IARReflection | null {
    // Look for IAR reflection patterns like ->|action_result|<- or {"reflection": {...}}
    const iarPattern = /\{\s*"reflection"\s*:\s*\{([^}]+)\}\s*\}/;
    const actionResultPattern = /->|action_result|<-\s*([^->]*)/;
    
    const iarMatch = content.match(iarPattern);
    if (iarMatch) {
      try {
        const reflectionData = JSON.parse(`{"reflection": {${iarMatch[1]}}}`);
        return this.normalizeIARData(reflectionData.reflection);
      } catch (e) {
        // Continue to generation if parsing fails
      }
    }

    return null;
  }

  /**
   * Generate IAR based on content analysis
   */
  private static generateIAR(content: string, context: any): IARReflection {
    const status = this.determineStatus(content);
    const summary = this.generateSummary(content);
    const confidence = this.calculateConfidence(content, context);
    const alignment = this.checkAlignment(content);
    const issues = this.identifyIssues(content);
    const tacticalResonance = this.calculateTacticalResonance(content);
    const crystallizationPotential = this.calculateCrystallizationPotential(content);

    return {
      status,
      summary,
      confidence,
      alignment_check: alignment,
      potential_issues: issues,
      tactical_resonance: tacticalResonance,
      raw_output_preview: content.substring(0, 200), // Add mandatory field
      timestamp: new Date().toISOString(), // Add mandatory field
      crystallization_potential: this.calculateCrystallizationPotential(content)
    };
  }

  /**
   * Determine the status based on content indicators
   */
  private static determineStatus(content: string): IARReflection['status'] {
    const successIndicators = ['success', 'complete', 'achieved', 'resolved', 'implemented'];
    const failureIndicators = ['error', 'failed', 'unable', 'cannot', 'impossible'];
    const partialIndicators = ['partial', 'incomplete', 'in progress', 'working'];

    const lowerContent = content.toLowerCase();

    if (failureIndicators.some(indicator => lowerContent.includes(indicator))) {
      return 'Failure';
    }
    if (partialIndicators.some(indicator => lowerContent.includes(indicator))) {
      return 'Partial';
    }
    if (successIndicators.some(indicator => lowerContent.includes(indicator))) {
      return 'Success';
    }

    return 'Skipped';
  }

  /**
   * Generate a concise summary of the content
   */
  private static generateSummary(content: string): string {
    // Extract first meaningful sentence or create summary
    const sentences = content.split(/[.!?]+/).filter(s => s.trim().length > 10);
    if (sentences.length > 0) {
      const firstSentence = sentences[0].trim();
      return firstSentence.length > 100 
        ? `${firstSentence.substring(0, 97)}...`
        : firstSentence;
    }
    
    return content.length > 100 
      ? `${content.substring(0, 97)}...`
      : content;
  }

  /**
   * Calculate confidence level based on content analysis
   */
  private static calculateConfidence(content: string, context: any): number {
    let confidence = 0.5; // Base confidence

    // Increase confidence for specific indicators
    const highConfidenceIndicators = ['verified', 'confirmed', 'validated', 'tested', 'proven'];
    const lowConfidenceIndicators = ['uncertain', 'maybe', 'possibly', 'unclear', 'ambiguous'];

    const lowerContent = content.toLowerCase();

    highConfidenceIndicators.forEach(indicator => {
      if (lowerContent.includes(indicator)) confidence += 0.15;
    });

    lowConfidenceIndicators.forEach(indicator => {
      if (lowerContent.includes(indicator)) confidence -= 0.2;
    });

    // Adjust for content length and structure
    if (content.length > 500) confidence += 0.1;
    if (content.includes('->|execution|<-')) confidence += 0.2;

    return Math.max(0.0, Math.min(1.0, confidence));
  }

  /**
   * Check alignment with protocol objectives
   */
  private static checkAlignment(content: string): IARReflection['alignment_check'] {
    const alignedIndicators = ['resonance', 'protocol', 'cognitive', 'implementation'];
    const misalignedIndicators = ['dissonance', 'error', 'violation', 'breach'];

    const lowerContent = content.toLowerCase();

    if (misalignedIndicators.some(indicator => lowerContent.includes(indicator))) {
      return 'Potentially Misaligned';
    }
    if (alignedIndicators.some(indicator => lowerContent.includes(indicator))) {
      return 'Aligned';
    }

    return 'N/A';
  }

  /**
   * Identify potential issues in the content
   */
  private static identifyIssues(content: string): string[] {
    const issues: string[] = [];
    const lowerContent = content.toLowerCase();

    const issuePatterns = [
      { pattern: /error|exception|failed/i, issue: 'Execution error detected' },
      { pattern: /todo|fixme|hack/i, issue: 'Technical debt identified' },
      { pattern: /deprecated|obsolete/i, issue: 'Deprecated functionality' },
      { pattern: /security|vulnerable/i, issue: 'Security concern' },
      { pattern: /performance|slow|timeout/i, issue: 'Performance issue' },
    ];

    issuePatterns.forEach(({ pattern, issue }) => {
      if (pattern.test(content)) {
        issues.push(issue);
      }
    });

    return issues;
  }

  /**
   * Calculate tactical resonance level
   */
  private static calculateTacticalResonance(content: string): number {
    let resonance = 0.5;

    const resonanceIndicators = [
      'strategic', 'tactical', 'aligned', 'coherent', 'integrated', 'synergistic'
    ];

    const lowerContent = content.toLowerCase();
    resonanceIndicators.forEach(indicator => {
      if (lowerContent.includes(indicator)) resonance += 0.1;
    });

    return Math.max(0.0, Math.min(1.0, resonance));
  }

  /**
   * Calculate crystallization potential
   */
  private static calculateCrystallizationPotential(content: string): number {
    let potential = 0.3; // Base potential

    const crystallizationIndicators = [
      'pattern', 'insight', 'learning', 'knowledge', 'discovery', 'breakthrough'
    ];

    const lowerContent = content.toLowerCase();
    crystallizationIndicators.forEach(indicator => {
      if (lowerContent.includes(indicator)) potential += 0.15;
    });

    // Higher potential for longer, more detailed content
    if (content.length > 300) potential += 0.1;
    if (content.length > 1000) potential += 0.1;

    return Math.max(0.0, Math.min(1.0, potential));
  }

  /**
   * Normalize IAR data to ensure it matches the interface
   */
  private static normalizeIARData(data: any): IARReflection {
    return {
      status: data.status || 'Pending',
      summary: data.summary || 'No summary available',
      confidence: typeof data.confidence === 'number' ? data.confidence : 0.5,
      alignment_check: data.alignment_check || 'Uncertain',
      potential_issues: Array.isArray(data.potential_issues) ? data.potential_issues : [],
      raw_output_preview: String(data.raw_output_preview || '').substring(0, 200),
      timestamp: data.timestamp || new Date().toISOString(),
      tactical_resonance: typeof data.tactical_resonance === 'number' ? data.tactical_resonance : undefined,
      crystallization_potential: typeof data.crystallization_potential === 'number' ? data.crystallization_potential : undefined,
    };
  }
} 