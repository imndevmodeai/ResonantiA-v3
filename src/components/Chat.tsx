'use client';

import React, { useState, useEffect } from 'react';
import MessageList from './MessageList';
import ChatInput from './ChatInput';
import Canvas from './Canvas';
import useWebSocket from '../nextjs-chat/src/hooks/useWebSocket';
import { iarProcessor } from '../utils/iarProcessor';
import { sprDetector } from '../utils/sprDetector';
import { temporalAnalyzer } from '../utils/temporalAnalyzer';
import type { 
  EnhancedMessage, 
  ProtocolStatus,
  IARReflection,
  SPRActivation,
  TemporalContext,
  MetaCognitiveState,
  ComplexSystemVisioningData,
  ImplementationResonance
} from '../types/protocol';

export default function Chat() {
  const [messages, setMessages] = useState<EnhancedMessage[]>([]);
  const [showCanvas, setShowCanvas] = useState(true);
  // const [showRiseEngine, setShowRiseEngine] = useState(false); // Disabled - using WebSocket instead
  const [protocolStatus, setProtocolStatus] = useState<ProtocolStatus>({
    iar_enabled: process.env.NEXT_PUBLIC_IAR_ENABLED === 'true',
    spr_recognition_enabled: process.env.NEXT_PUBLIC_SPR_RECOGNITION_ENABLED === 'true',
    temporal_resonance_enabled: process.env.NEXT_PUBLIC_TEMPORAL_RESONANCE_ENABLED === 'true',
    complex_system_visioning_enabled: process.env.NEXT_PUBLIC_COMPLEX_SYSTEM_VISIONING_ENABLED === 'true',
    metacognitive_shift_enabled: process.env.NEXT_PUBLIC_METACOGNITIVE_SHIFT_ENABLED === 'true',
    implementation_resonance_enabled: process.env.NEXT_PUBLIC_IMPLEMENTATION_RESONANCE_ENABLED === 'true',
    sirc_cycle_active: process.env.NEXT_PUBLIC_SIRC_CYCLE_ENABLED === 'true',
    crc_enabled: process.env.NEXT_PUBLIC_CRC_ENABLED === 'true',
    insight_solidification_enabled: process.env.NEXT_PUBLIC_INSIGHT_SOLIDIFICATION_ENABLED === 'true',
    vetting_agent_enabled: process.env.NEXT_PUBLIC_VETTING_AGENT_ENABLED === 'true'
  });

  const {
    messages: wsMessages,
    isConnected,
    sendMessage,
    nodes,
    edges,
    onNodesChange,
    onEdgesChange,
    onConnect
  } = useWebSocket('ws://localhost:3013');

  // Process incoming WebSocket messages with protocol features
  useEffect(() => {
    if (wsMessages.length > 0) {
      const lastMessage = wsMessages[wsMessages.length - 1];
      const enhancedMessage = processMessageWithProtocol(lastMessage);
      setMessages(prev => [...prev, enhancedMessage]);
    }
  }, [wsMessages]);

  // Process message with all ResonantiA Protocol v3.1-CA features
  const processMessageWithProtocol = (rawMessage: any): EnhancedMessage => {
    const messageId = `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const timestamp = new Date().toISOString();
    
    // Determine message type
    let messageType: EnhancedMessage['type'] = 'assistant';
    if (rawMessage.type === 'response') {
      messageType = 'assistant';
    } else if (rawMessage.type === 'system') {
      messageType = 'system';
    } else if (rawMessage.type === 'user') {
      messageType = 'user';
    } else if (rawMessage.content.includes('IAR:')) {
      messageType = 'iar';
    } else if (rawMessage.content.includes('SPR:')) {
      messageType = 'spr';
    } else if (rawMessage.content.includes('Temporal:')) {
      messageType = 'temporal';
    } else if (rawMessage.content.includes('Metacognitive:')) {
      messageType = 'metacognitive';
    }

    // Initialize enhanced message
    const enhancedMessage: EnhancedMessage = {
      id: messageId,
      content: rawMessage.content || rawMessage,
      sender: 'arche',
      type: messageType,
      message_type: messageType,
      timestamp,
      iar: undefined,
      spr_activations: undefined,
      temporal_context: undefined,
      complex_system_visioning: undefined,
      implementation_resonance: undefined,
      thought_trail: undefined,
      protocol_compliance: false,
      protocol_version: undefined,
      protocol_init: undefined,
      protocol_error: undefined,
      iar_data: undefined,
      iar_processing: undefined,
      spr_detection: undefined,
      temporal_analysis: undefined,
      causal_lags: [],
      metacognitive_shift: undefined
    };

    // Apply IAR processing if enabled
    if (protocolStatus.iar_enabled) {
      try {
        const iarData = iarProcessor.generateIAR(
          messageType === 'iar' ? 'metacognitive' : 'response',
          enhancedMessage.content,
          { message_type: messageType, timestamp }
        );
        
        const iarProcessing = iarProcessor.processIAR(iarData);
        
        enhancedMessage.iar_data = iarData;
        enhancedMessage.iar_processing = iarProcessing;
        
        // Update protocol compliance
        enhancedMessage.protocol_compliance = iarData.protocol_compliance;
      } catch (error) {
        console.error('IAR processing error:', error);
      }
    }

    // Apply SPR detection if enabled
    if (protocolStatus.spr_recognition_enabled) {
      try {
        const sprDetection = sprDetector.detectSPRs(enhancedMessage.content, {
          message_type: messageType,
          timestamp,
          iar_data: enhancedMessage.iar_data
        });
        
        enhancedMessage.spr_detection = sprDetection;
        enhancedMessage.spr_activations = sprDetection.detected_sprs;
      } catch (error) {
        console.error('SPR detection error:', error);
      }
    }

    // Apply temporal analysis if enabled
    if (protocolStatus.temporal_resonance_enabled) {
      try {
        const temporalAnalysis = temporalAnalyzer.analyzeTemporal(enhancedMessage.content, {
          message_type: messageType,
          timestamp,
          iar_data: enhancedMessage.iar_data,
          spr_detection: enhancedMessage.spr_detection
        });
        
        enhancedMessage.temporal_analysis = temporalAnalysis;
        
        // Detect causal lags
        const causalLags = temporalAnalyzer.detectCausalLags(enhancedMessage.content, {
          message_type: messageType,
          timestamp
        });

        // Fix: causalLags is already an array
        if (causalLags && Array.isArray(causalLags)) {
          enhancedMessage.causal_lags = causalLags;
        } else {
          enhancedMessage.causal_lags = [];
        }
      } catch (error) {
        console.error('Temporal analysis error:', error);
        enhancedMessage.causal_lags = [];
      }
    }

    // Apply complex system visioning if enabled
    if (protocolStatus.complex_system_visioning_enabled) {
      try {
        enhancedMessage.complex_system_visioning = analyzeComplexSystemVisioning(enhancedMessage.content);
      } catch (error) {
        console.error('Complex system visioning error:', error);
      }
    }

    // Apply meta-cognitive shift analysis if enabled
    if (protocolStatus.metacognitive_shift_enabled) {
      try {
        enhancedMessage.metacognitive_shift = analyzeMetacognitiveShift(enhancedMessage.content);
      } catch (error) {
        console.error('Meta-cognitive shift analysis error:', error);
      }
    }

    return enhancedMessage;
  };

  // Analyze complex system visioning
  const analyzeComplexSystemVisioning = (content: string) => {
    const systemIndicators = ['system', 'component', 'interaction', 'relationship', 'structure'];
    const humanIndicators = ['human', 'behavior', 'motivation', 'emotion', 'decision'];
    const emergenceIndicators = ['emerge', 'emergent', 'unexpected', 'surprise', 'emergent'];
    const scenarioIndicators = ['scenario', 'situation', 'case', 'example', 'instance'];
    
    const systemComprehension = Math.min(0.9, 0.4 + (systemIndicators.filter(indicator => 
      content.toLowerCase().includes(indicator)
    ).length * 0.1));
    
    const humanFactorModeling = Math.min(0.9, 0.3 + (humanIndicators.filter(indicator => 
      content.toLowerCase().includes(indicator)
    ).length * 0.12));
    
    const emergencePrediction = Math.min(0.9, 0.2 + (emergenceIndicators.filter(indicator => 
      content.toLowerCase().includes(indicator)
    ).length * 0.15));
    
    const scenarioAccuracy = Math.min(0.9, 0.4 + (scenarioIndicators.filter(indicator => 
      content.toLowerCase().includes(indicator)
    ).length * 0.1));

    return {
      system_comprehension: systemComprehension,
      human_factor_modeling: humanFactorModeling,
      emergence_prediction: emergencePrediction,
      scenario_accuracy: scenarioAccuracy
    };
  };

  // Analyze meta-cognitive shift
  const analyzeMetacognitiveShift = (content: string) => {
    const selfAwarenessIndicators = ['I think', 'I believe', 'my analysis', 'I understand'];
    const errorIndicators = ['error', 'mistake', 'incorrect', 'wrong', 'should be'];
    const correctionIndicators = ['correct', 'fix', 'improve', 'better', 'enhance'];
    const learningIndicators = ['learn', 'understand', 'insight', 'realize', 'discover'];
    
    const selfAwareness = Math.min(0.9, 0.4 + (selfAwarenessIndicators.filter(indicator => 
      content.toLowerCase().includes(indicator)
    ).length * 0.1));
    
    const errorDetection = Math.min(0.9, 0.3 + (errorIndicators.filter(indicator => 
      content.toLowerCase().includes(indicator)
    ).length * 0.15));
    
    const correctionAbility = Math.min(0.9, 0.4 + (correctionIndicators.filter(indicator => 
      content.toLowerCase().includes(indicator)
    ).length * 0.1));
    
    const learningIntegration = Math.min(0.9, 0.3 + (learningIndicators.filter(indicator => 
      content.toLowerCase().includes(indicator)
    ).length * 0.12));

    return {
      self_awareness: selfAwareness,
      error_detection: errorDetection,
      correction_ability: correctionAbility,
      learning_integration: learningIntegration
    };
  };

  // Handle message sending with protocol processing
  const handleSendMessage = (content: string) => {
    // Create user message
    const userMessage: EnhancedMessage = {
      id: `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      content,
      sender: 'user',
      type: 'user',
      message_type: 'user',
      timestamp: new Date().toISOString(),
      iar: undefined,
      spr_activations: undefined,
      temporal_context: undefined,
      meta_cognitive_state: undefined,
      complex_system_visioning: undefined,
      implementation_resonance: undefined,
      thought_trail: undefined,
      protocol_compliance: false,
      protocol_version: undefined,
      protocol_init: undefined,
      protocol_error: undefined
    };

    // Process user message with protocol features
    const processedUserMessage = processMessageWithProtocol(userMessage);
    setMessages(prev => [...prev, processedUserMessage]);

    // Send message via WebSocket
    sendMessage(content);
  };

  // Handle RISE Engine analysis results - DISABLED: Using WebSocket instead
  // const handleRiseEngineAnalysis = (result: any) => {
  //   // Add RISE Engine analysis result as a system message
  //   const riseMessage: EnhancedMessage = {
  //     id: `rise_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
  //     content: `🚀 RISE Engine Analysis Complete\n\n${result.output || 'Analysis completed successfully'}`,
  //     type: 'system',
  //     timestamp: new Date().toISOString(),
  //     protocol_compliance: {
  //       sirc_cycle_active: true,
  //       crc_enabled: true,
  //       insight_solidification: true,
  //       vetting_agent_approved: true
  //     }
  //   };
  //   setMessages(prev => [...prev, riseMessage]);
  // };

  // Get protocol status indicator
  const getProtocolStatusIndicator = () => {
    const activeFeatures = Object.values(protocolStatus).filter(Boolean).length;
    const totalFeatures = Object.keys(protocolStatus).length;
    const percentage = (activeFeatures / totalFeatures) * 100;
    
    return {
      percentage,
      status: percentage >= 80 ? 'excellent' : percentage >= 60 ? 'good' : percentage >= 40 ? 'fair' : 'poor',
      activeFeatures,
      totalFeatures
    };
  };

  const statusIndicator = getProtocolStatusIndicator();

  return (
    <div className="flex h-screen bg-gray-900 text-white">
      {/* Main Chat Area */}
      <div className={`flex flex-col ${showCanvas ? 'w-1/2' : 'w-full'} transition-all duration-300`}>
        {/* RISE Engine Panel - DISABLED: Using WebSocket instead */}
        {/* {showRiseEngine && (
          <div className="bg-gray-800 border-b border-gray-700">
            <RiseEnginePanel 
              onAnalysisComplete={handleRiseEngineAnalysis}
              className="bg-gray-800 text-white"
            />
          </div>
        )} */}
        {/* Header with Protocol Status */}
        <div className="bg-gray-800 p-4 border-b border-gray-700">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-4">
              <h1 className="text-xl font-bold text-blue-400">ArchE - ResonantiA Protocol v3.1-CA</h1>
              <div className={`px-2 py-1 rounded text-xs font-medium ${
                isConnected ? 'bg-green-600 text-white' : 'bg-red-600 text-white'
              }`}>
                {isConnected ? 'Connected' : 'Disconnected'}
              </div>
            </div>
            
            {/* Protocol Status Indicator */}
            <div className="flex items-center space-x-2">
              <div className="text-xs text-gray-400">
                Protocol Status: {statusIndicator.activeFeatures}/{statusIndicator.totalFeatures}
              </div>
              <div className={`w-16 h-2 rounded-full overflow-hidden bg-gray-700`}>
                <div 
                  className={`h-full transition-all duration-300 ${
                    statusIndicator.status === 'excellent' ? 'bg-green-500' :
                    statusIndicator.status === 'good' ? 'bg-blue-500' :
                    statusIndicator.status === 'fair' ? 'bg-yellow-500' : 'bg-red-500'
                  }`}
                  style={{ width: `${statusIndicator.percentage}%` }}
                />
              </div>
            </div>
            
            {/* RISE Engine button disabled - using WebSocket instead */}
            {/* <button
              onClick={() => setShowRiseEngine(!showRiseEngine)}
              className="px-3 py-1 bg-green-600 hover:bg-green-700 rounded text-sm transition-colors mr-2"
            >
              {showRiseEngine ? 'Hide RISE' : 'Show RISE'}
            </button> */}
            <button
              onClick={() => setShowCanvas(!showCanvas)}
              className="px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-sm transition-colors"
            >
              {showCanvas ? 'Hide Canvas' : 'Show Canvas'}
            </button>
          </div>
          
          {/* Protocol Features Status */}
          <div className="mt-2 flex flex-wrap gap-2">
            {Object.entries(protocolStatus).map(([feature, enabled]) => (
              <div
                key={feature}
                className={`px-2 py-1 rounded text-xs font-medium ${
                  enabled ? 'bg-green-600 text-white' : 'bg-gray-600 text-gray-300'
                }`}
              >
                {feature.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </div>
            ))}
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto">
          <MessageList 
            messages={messages} 
            protocolStatus={protocolStatus}
          />
        </div>

        {/* Input */}
        <div className="p-4 border-t border-gray-700">
          <ChatInput onSendMessage={handleSendMessage} protocolStatus={protocolStatus} />
        </div>
      </div>

      {/* Canvas Area */}
      {showCanvas && (
        <div className="w-1/2 border-l border-gray-700">
          <Canvas
            nodes={nodes}
            edges={edges as any}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            protocolStatus={protocolStatus}
            messages={messages as any}
          />
        </div>
      )}
    </div>
  );
}
