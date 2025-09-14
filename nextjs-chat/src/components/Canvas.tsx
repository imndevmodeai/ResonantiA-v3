'use client';

import React, { useCallback, useMemo } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  NodeTypes,
  EdgeTypes,
} from 'reactflow';
import 'reactflow/dist/style.css';

interface EnhancedMessage {
  id: string;
  content: string;
  type: 'user' | 'assistant' | 'system' | 'iar' | 'spr' | 'temporal' | 'metacognitive';
  timestamp: string;
  
  // IAR Data
  iar_data?: any;
  iar_processing?: any;
  
  // SPR Data
  spr_detection?: any;
  spr_activations?: any[];
  
  // Temporal Data
  temporal_analysis?: any;
  causal_lags?: any[];
  
  // Protocol Compliance
  protocol_compliance?: {
    sirc_cycle_active: boolean;
    crc_enabled: boolean;
    insight_solidification: boolean;
    vetting_agent_approved: boolean;
  };
  
  // Meta-cognitive Data
  metacognitive_shift?: {
    self_awareness: number;
    error_detection: number;
    correction_ability: number;
    learning_integration: number;
  };
  
  // Complex System Visioning
  complex_system_visioning?: {
    system_comprehension: number;
    human_factor_modeling: number;
    emergence_prediction: number;
    scenario_accuracy: number;
  };
}

interface ProtocolStatus {
  iar_enabled: boolean;
  spr_recognition_enabled: boolean;
  temporal_resonance_enabled: boolean;
  complex_system_visioning_enabled: boolean;
  metacognitive_shift_enabled: boolean;
  implementation_resonance_enabled: boolean;
  sirc_cycle_active: boolean;
  crc_enabled: boolean;
  insight_solidification_enabled: boolean;
  vetting_agent_enabled: boolean;
}

interface CanvasProps {
  nodes: Node[];
  edges: Edge[];
  onNodesChange: any;
  onEdgesChange: any;
  onConnect: (connection: Connection) => void;
  protocolStatus: ProtocolStatus;
  messages: EnhancedMessage[];
}

// Custom node types for protocol visualization
const IARNode = ({ data }: { data: any }) => (
  <div className="px-4 py-2 shadow-lg rounded-lg bg-blue-900 border-2 border-blue-400 text-white text-sm">
    <div className="font-bold text-blue-200">{data.label}</div>
    <div className="text-xs text-blue-300">Confidence: {Math.round(data.confidence * 100)}%</div>
    <div className="text-xs text-blue-300">Resonance: {Math.round(data.resonance * 100)}%</div>
  </div>
);

const SPRNode = ({ data }: { data: any }) => (
  <div className="px-4 py-2 shadow-lg rounded-lg bg-green-900 border-2 border-green-400 text-white text-sm">
    <div className="font-bold text-green-200">{data.label}</div>
    <div className="text-xs text-green-300">Activation: {Math.round(data.activation * 100)}%</div>
    <div className="text-xs text-green-300">Frequency: {data.frequency}</div>
  </div>
);

const TemporalNode = ({ data }: { data: any }) => (
  <div className="px-4 py-2 shadow-lg rounded-lg bg-purple-900 border-2 border-purple-400 text-white text-sm">
    <div className="font-bold text-purple-200">{data.label}</div>
    <div className="text-xs text-purple-300">4D Score: {Math.round(data.fourDScore * 100)}%</div>
    <div className="text-xs text-purple-300">Causal: {Math.round(data.causalScore * 100)}%</div>
  </div>
);

const MetaCognitiveNode = ({ data }: { data: any }) => (
  <div className="px-4 py-2 shadow-lg rounded-lg bg-orange-900 border-2 border-orange-400 text-white text-sm">
    <div className="font-bold text-orange-200">{data.label}</div>
    <div className="text-xs text-orange-300">Self-Awareness: {Math.round(data.selfAwareness * 100)}%</div>
    <div className="text-xs text-orange-300">Learning: {Math.round(data.learning * 100)}%</div>
  </div>
);

const ComplexSystemNode = ({ data }: { data: any }) => (
  <div className="px-4 py-2 shadow-lg rounded-lg bg-cyan-900 border-2 border-cyan-400 text-white text-sm">
    <div className="font-bold text-cyan-200">{data.label}</div>
    <div className="text-xs text-cyan-300">System Comp: {Math.round(data.systemComp * 100)}%</div>
    <div className="text-xs text-cyan-300">Human Factor: {Math.round(data.humanFactor * 100)}%</div>
  </div>
);

const ProtocolStatusNode = ({ data }: { data: any }) => (
  <div className="px-4 py-2 shadow-lg rounded-lg bg-indigo-900 border-2 border-indigo-400 text-white text-sm">
    <div className="font-bold text-indigo-200">{data.label}</div>
    <div className="text-xs text-indigo-300">Compliance: {Math.round(data.compliance * 100)}%</div>
    <div className="text-xs text-indigo-300">Features: {data.activeFeatures}/{data.totalFeatures}</div>
  </div>
);

const nodeTypes: NodeTypes = {
  iar: IARNode,
  spr: SPRNode,
  temporal: TemporalNode,
  metacognitive: MetaCognitiveNode,
  complex: ComplexSystemNode,
  protocol: ProtocolStatusNode,
};

export default function Canvas({
  nodes,
  edges,
  onNodesChange,
  onEdgesChange,
  onConnect,
  protocolStatus,
  messages,
}: CanvasProps) {
  // Generate protocol-aware nodes from messages
  const protocolNodes = useMemo(() => {
    const newNodes: Node[] = [];
    let nodeId = 0;

    // Add protocol status node
    const activeFeatures = Object.values(protocolStatus).filter(Boolean).length;
    const totalFeatures = Object.keys(protocolStatus).length;
    const complianceScore = activeFeatures / totalFeatures;

    newNodes.push({
      id: 'protocol-status',
      type: 'protocol',
      position: { x: 50, y: 50 },
      data: {
        label: 'Protocol Status',
        compliance: complianceScore,
        activeFeatures,
        totalFeatures,
      },
    });

    // Process messages for protocol visualization
    messages.forEach((message, index) => {
      const baseX = 200 + (index * 300);
      const baseY = 100 + (index * 200);

      // Add IAR node if available
      if (message.iar_data && protocolStatus.iar_enabled) {
        newNodes.push({
          id: `iar-${message.id}`,
          type: 'iar',
          position: { x: baseX, y: baseY },
          data: {
            label: `IAR Analysis`,
            confidence: message.iar_data.confidence_level,
            resonance: message.iar_data.resonance_score,
            messageId: message.id,
          },
        });
      }

      // Add SPR nodes if available
      if (message.spr_activations && protocolStatus.spr_recognition_enabled) {
        message.spr_activations.forEach((spr, sprIndex) => {
          newNodes.push({
            id: `spr-${message.id}-${sprIndex}`,
            type: 'spr',
            position: { x: baseX + 150, y: baseY + (sprIndex * 80) },
            data: {
              label: spr.guardian_point,
              activation: spr.activation_level,
              frequency: spr.knowledge_network.resonance_frequency,
              messageId: message.id,
            },
          });
        });
      }

      // Add temporal node if available
      if (message.temporal_analysis && protocolStatus.temporal_resonance_enabled) {
        newNodes.push({
          id: `temporal-${message.id}`,
          type: 'temporal',
          position: { x: baseX, y: baseY + 150 },
          data: {
            label: '4D Analysis',
            fourDScore: message.temporal_analysis.temporal_data.four_d_synthesis.temporal_coherence,
            causalScore: message.temporal_analysis.temporal_data.causal_understanding.causal_chain_clarity,
            messageId: message.id,
          },
        });
      }

      // Add meta-cognitive node if available
      if (message.metacognitive_shift && protocolStatus.metacognitive_shift_enabled) {
        newNodes.push({
          id: `metacognitive-${message.id}`,
          type: 'metacognitive',
          position: { x: baseX + 150, y: baseY + 150 },
          data: {
            label: 'Meta-cognitive',
            selfAwareness: message.metacognitive_shift.self_awareness,
            learning: message.metacognitive_shift.learning_integration,
            messageId: message.id,
          },
        });
      }

      // Add complex system node if available
      if (message.complex_system_visioning && protocolStatus.complex_system_visioning_enabled) {
        newNodes.push({
          id: `complex-${message.id}`,
          type: 'complex',
          position: { x: baseX, y: baseY + 300 },
          data: {
            label: 'Complex System',
            systemComp: message.complex_system_visioning.system_comprehension,
            humanFactor: message.complex_system_visioning.human_factor_modeling,
            messageId: message.id,
          },
        });
      }
    });

    return newNodes;
  }, [messages, protocolStatus]);

  // Generate protocol-aware edges
  const protocolEdges = useMemo(() => {
    const newEdges: Edge[] = [];
    let edgeId = 0;

    // Connect protocol status to all other nodes
    protocolNodes.forEach((node) => {
      if (node.id !== 'protocol-status') {
        newEdges.push({
          id: `edge-${edgeId++}`,
          source: 'protocol-status',
          target: node.id,
          type: 'smoothstep',
          style: { stroke: '#6366f1', strokeWidth: 2 },
          animated: true,
        });
      }
    });

    // Connect IAR nodes to related nodes
    protocolNodes.forEach((node) => {
      if (node.type === 'iar') {
        // Connect to SPR nodes from same message
        protocolNodes.forEach((targetNode) => {
          if (targetNode.type === 'spr' && 
              node.data.messageId === targetNode.data.messageId) {
            newEdges.push({
              id: `edge-${edgeId++}`,
              source: node.id,
              target: targetNode.id,
              type: 'smoothstep',
              style: { stroke: '#10b981', strokeWidth: 2 },
              animated: true,
            });
          }
        });

        // Connect to temporal nodes from same message
        protocolNodes.forEach((targetNode) => {
          if (targetNode.type === 'temporal' && 
              node.data.messageId === targetNode.data.messageId) {
            newEdges.push({
              id: `edge-${edgeId++}`,
              source: node.id,
              target: targetNode.id,
              type: 'smoothstep',
              style: { stroke: '#8b5cf6', strokeWidth: 2 },
              animated: true,
            });
          }
        });
      }
    });

    // Connect temporal nodes to causal lags
    messages.forEach((message) => {
      if (message.causal_lags && message.causal_lags.length > 0) {
        const temporalNode = protocolNodes.find(n => 
          n.type === 'temporal' && n.data.messageId === message.id
        );
        
        if (temporalNode) {
          message.causal_lags.forEach((lag, index) => {
            // Create causal lag node
            const lagNode: Node = {
              id: `causal-lag-${message.id}-${index}`,
              type: 'temporal',
              position: { 
                x: temporalNode.position.x + 200, 
                y: temporalNode.position.y + (index * 60) 
              },
              data: {
                label: `${lag.pattern_type} Lag`,
                fourDScore: lag.confidence,
                causalScore: lag.confidence,
                messageId: message.id,
              },
            };
            
            protocolNodes.push(lagNode);
            
            newEdges.push({
              id: `edge-${edgeId++}`,
              source: temporalNode.id,
              target: lagNode.id,
              type: 'smoothstep',
              style: { stroke: '#f59e0b', strokeWidth: 2, strokeDasharray: '5,5' },
              animated: true,
            });
          });
        }
      }
    });

    return newEdges;
  }, [protocolNodes, messages]);

  // Combine original nodes/edges with protocol nodes/edges
  const allNodes = useMemo(() => {
    return [...nodes, ...protocolNodes];
  }, [nodes, protocolNodes]);

  const allEdges = useMemo(() => {
    return [...edges, ...protocolEdges];
  }, [edges, protocolEdges]);

  const handleConnect = useCallback(
    (params: Connection) => {
      onConnect(params);
    },
    [onConnect]
  );

  // Calculate protocol statistics
  const protocolStats = useMemo(() => {
    const totalMessages = messages.length;
    const iarProcessed = messages.filter(m => m.iar_data).length;
    const sprDetected = messages.filter(m => m.spr_detection).length;
    const temporalAnalyzed = messages.filter(m => m.temporal_analysis).length;
    const metacognitiveShifted = messages.filter(m => m.metacognitive_shift).length;
    const complexSystemModeled = messages.filter(m => m.complex_system_visioning).length;

    return {
      totalMessages,
      iarProcessed,
      sprDetected,
      temporalAnalyzed,
      metacognitiveShifted,
      complexSystemModeled,
      iarPercentage: totalMessages > 0 ? (iarProcessed / totalMessages) * 100 : 0,
      sprPercentage: totalMessages > 0 ? (sprDetected / totalMessages) * 100 : 0,
      temporalPercentage: totalMessages > 0 ? (temporalAnalyzed / totalMessages) * 100 : 0,
      metacognitivePercentage: totalMessages > 0 ? (metacognitiveShifted / totalMessages) * 100 : 0,
      complexSystemPercentage: totalMessages > 0 ? (complexSystemModeled / totalMessages) * 100 : 0,
    };
  }, [messages]);

  return (
    <div className="h-full flex flex-col">
      {/* Protocol Statistics Header */}
      <div className="bg-gray-800 p-3 border-b border-gray-700">
        <h3 className="text-sm font-semibold text-white mb-2">Protocol Visualization</h3>
        <div className="grid grid-cols-3 gap-2 text-xs">
          <div className="bg-blue-900 p-2 rounded">
            <div className="text-blue-300">IAR Processed</div>
            <div className="text-white font-bold">{protocolStats.iarPercentage.toFixed(1)}%</div>
          </div>
          <div className="bg-green-900 p-2 rounded">
            <div className="text-green-300">SPR Detected</div>
            <div className="text-white font-bold">{protocolStats.sprPercentage.toFixed(1)}%</div>
          </div>
          <div className="bg-purple-900 p-2 rounded">
            <div className="text-purple-300">4D Analyzed</div>
            <div className="text-white font-bold">{protocolStats.temporalPercentage.toFixed(1)}%</div>
          </div>
          <div className="bg-orange-900 p-2 rounded">
            <div className="text-orange-300">Meta-cognitive</div>
            <div className="text-white font-bold">{protocolStats.metacognitivePercentage.toFixed(1)}%</div>
          </div>
          <div className="bg-cyan-900 p-2 rounded">
            <div className="text-cyan-300">Complex System</div>
            <div className="text-white font-bold">{protocolStats.complexSystemPercentage.toFixed(1)}%</div>
          </div>
          <div className="bg-indigo-900 p-2 rounded">
            <div className="text-indigo-300">Total Messages</div>
            <div className="text-white font-bold">{protocolStats.totalMessages}</div>
          </div>
        </div>
      </div>

      {/* ReactFlow Canvas */}
      <div className="flex-1">
        <ReactFlow
          nodes={allNodes}
          edges={allEdges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={handleConnect}
          nodeTypes={nodeTypes}
          fitView
          attributionPosition="bottom-left"
        >
          <Controls />
          <Background color="#374151" gap={20} />
        </ReactFlow>
      </div>

      {/* Protocol Legend */}
      <div className="bg-gray-800 p-3 border-t border-gray-700">
        <h4 className="text-xs font-semibold text-white mb-2">Protocol Node Types</h4>
        <div className="grid grid-cols-2 gap-2 text-xs">
          <div className="flex items-center">
            <div className="w-3 h-3 bg-blue-400 rounded mr-2"></div>
            <span className="text-gray-300">IAR Analysis</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 bg-green-400 rounded mr-2"></div>
            <span className="text-gray-300">SPR Activation</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 bg-purple-400 rounded mr-2"></div>
            <span className="text-gray-300">Temporal Analysis</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 bg-orange-400 rounded mr-2"></div>
            <span className="text-gray-300">Meta-cognitive</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 bg-cyan-400 rounded mr-2"></div>
            <span className="text-gray-300">Complex System</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 bg-indigo-400 rounded mr-2"></div>
            <span className="text-gray-300">Protocol Status</span>
          </div>
        </div>
      </div>
    </div>
  );
}
