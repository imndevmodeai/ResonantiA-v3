'use client';

import React, { useState, useRef, useEffect } from 'react';
import { iarProcessor } from '../utils/iarProcessor';
import { sprDetector } from '../utils/sprDetector';
import { temporalAnalyzer } from '../utils/temporalAnalyzer';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  protocolStatus?: {
    iar_enabled: boolean;
    spr_recognition_enabled: boolean;
    temporal_resonance_enabled: boolean;
    complex_system_visioning_enabled: boolean;
    metacognitive_shift_enabled: boolean;
  };
}

export default function ChatInput({ onSendMessage, protocolStatus }: ChatInputProps) {
  const [message, setMessage] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [protocolAnalysis, setProtocolAnalysis] = useState<any>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [message]);

  // Real-time protocol analysis
  useEffect(() => {
    if (message.length > 10 && protocolStatus) {
      const analyzeInput = async () => {
        try {
          const analysis: any = {};

          // IAR analysis
          if (protocolStatus.iar_enabled) {
            const iarData = iarProcessor.generateIAR('thought', message, { source: 'user_input' });
            analysis.iar = {
              confidence: iarData.confidence_level,
              resonance: iarData.resonance_score,
              recommendations: iarProcessor.processIAR(iarData).recommendations
            };
          }

          // SPR detection
          if (protocolStatus.spr_recognition_enabled) {
            const sprDetection = sprDetector.detectSPRs(message, { source: 'user_input' });
            analysis.spr = {
              detected: sprDetection.detected_sprs.length,
              recommendations: sprDetection.recommendations
            };
          }

          // Temporal analysis
          if (protocolStatus.temporal_resonance_enabled) {
            const temporalAnalysis = temporalAnalyzer.analyzeTemporal(message, { source: 'user_input' });
            analysis.temporal = {
              confidence: temporalAnalysis.temporal_data.confidence_level,
              resonance: temporalAnalysis.temporal_data.resonance_score,
              insights: temporalAnalysis.temporal_insights
            };
          }

          setProtocolAnalysis(analysis);
        } catch (error) {
          console.error('Protocol analysis error:', error);
        }
      };

      // Debounce analysis
      const timeoutId = setTimeout(analyzeInput, 500);
      return () => clearTimeout(timeoutId);
    } else {
      setProtocolAnalysis(null);
    }
  }, [message, protocolStatus]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim() || isProcessing) return;

    setIsProcessing(true);
    
    try {
      // Final protocol analysis before sending
      if (protocolStatus) {
        const finalAnalysis = {
          iar: protocolStatus.iar_enabled ? iarProcessor.generateIAR('thought', message, { final: true }) : null,
          spr: protocolStatus.spr_recognition_enabled ? sprDetector.detectSPRs(message, { final: true }) : null,
          temporal: protocolStatus.temporal_resonance_enabled ? temporalAnalyzer.analyzeTemporal(message, { final: true }) : null,
        };
        
        console.log('Final protocol analysis:', finalAnalysis);
      }

      onSendMessage(message);
      setMessage('');
      setProtocolAnalysis(null);
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  // Get protocol status indicator
  const getProtocolStatusIndicator = () => {
    if (!protocolAnalysis) return null;

    const indicators = [];
    
    if (protocolAnalysis.iar) {
      const confidence = protocolAnalysis.iar.confidence;
      const color = confidence >= 0.8 ? 'text-green-400' : confidence >= 0.6 ? 'text-yellow-400' : 'text-red-400';
      indicators.push(
        <div key="iar" className={`text-xs ${color}`}>
          IAR: {Math.round(confidence * 100)}%
        </div>
      );
    }

    if (protocolAnalysis.spr) {
      const detected = protocolAnalysis.spr.detected;
      const color = detected > 0 ? 'text-green-400' : 'text-gray-400';
      indicators.push(
        <div key="spr" className={`text-xs ${color}`}>
          SPR: {detected} detected
        </div>
      );
    }

    if (protocolAnalysis.temporal) {
      const resonance = protocolAnalysis.temporal.resonance;
      const color = resonance >= 0.8 ? 'text-blue-400' : resonance >= 0.6 ? 'text-purple-400' : 'text-orange-400';
      indicators.push(
        <div key="temporal" className={`text-xs ${color}`}>
          4D: {Math.round(resonance * 100)}%
        </div>
      );
    }

    return indicators;
  };

  // Get protocol recommendations
  const getProtocolRecommendations = () => {
    if (!protocolAnalysis) return null;

    const recommendations = [];
    
    if (protocolAnalysis.iar?.recommendations) {
      recommendations.push(...protocolAnalysis.iar.recommendations);
    }
    
    if (protocolAnalysis.spr?.recommendations) {
      recommendations.push(...protocolAnalysis.spr.recommendations);
    }

    if (recommendations.length === 0) return null;

    return (
      <div className="mt-2 p-2 bg-gray-800 rounded text-xs text-gray-300">
        <div className="font-medium mb-1">Protocol Recommendations:</div>
        <ul className="space-y-1">
          {recommendations.slice(0, 3).map((rec: string, index: number) => (
            <li key={index} className="flex items-start">
              <span className="text-blue-400 mr-1">•</span>
              {rec}
            </li>
          ))}
        </ul>
      </div>
    );
  };

  return (
    <div className="p-4 border-t border-gray-700 bg-gray-800">
      <form onSubmit={handleSubmit} className="space-y-2">
        {/* Protocol Status Indicators */}
        {protocolAnalysis && (
          <div className="flex space-x-4 mb-2">
            {getProtocolStatusIndicator()}
          </div>
        )}

        {/* Input Area */}
        <div className="flex space-x-2">
          <div className="flex-1 relative">
            <textarea
              ref={textareaRef}
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type your message... (Shift+Enter for new line)"
              className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              rows={1}
              maxLength={2000}
            />
            
            {/* Character count */}
            <div className="absolute bottom-1 right-2 text-xs text-gray-500">
              {message.length}/2000
            </div>
          </div>
          
          <button
            type="submit"
            disabled={!message.trim() || isProcessing}
            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-lg transition-colors flex items-center space-x-2"
          >
            {isProcessing ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <span>Processing...</span>
              </>
            ) : (
              <>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
                <span>Send</span>
              </>
            )}
          </button>
        </div>

        {/* Protocol Recommendations */}
        {getProtocolRecommendations()}
        {/* Protocol Features Info */}
        {protocolStatus && (
          <div className="text-xs text-gray-500">
            <div className="flex flex-wrap gap-2">
              {protocolStatus.iar_enabled && (
                <span className="px-2 py-1 bg-blue-900 text-blue-300 rounded">IAR Enabled</span>
              )}
              {protocolStatus.spr_recognition_enabled && (
                <span className="px-2 py-1 bg-green-900 text-green-300 rounded">SPR Recognition</span>
              )}
              {protocolStatus.temporal_resonance_enabled && (
                <span className="px-2 py-1 bg-purple-900 text-purple-300 rounded">4D Analysis</span>
              )}
              {protocolStatus.complex_system_visioning_enabled && (
                <span className="px-2 py-1 bg-cyan-900 text-cyan-300 rounded">Complex System</span>
              )}
              {protocolStatus.metacognitive_shift_enabled && (
                <span className="px-2 py-1 bg-orange-900 text-orange-300 rounded">Meta-cognitive</span>
              )}
            </div>
          </div>
        )}
      </form>
    </div>
  );
}
