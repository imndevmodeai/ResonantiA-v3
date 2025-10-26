import React, { useCallback, useEffect } from 'react';
import ReactFlow, {
  Node,
  Edge,
  addEdge,
  Connection,
  useNodesState,
  useEdgesState,
  Controls,
  Background,
  MiniMap,
  BackgroundVariant,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { TemporalResonanceNode } from '../protocol/TemporalResonance';
import { MetaCognitiveLoopsNode } from '../protocol/MetaCognitiveLoops';
import { ComplexSystemVisioningNode } from '../protocol/ComplexSystemVisioning';
import { EnhancedMessage } from '../../types/protocol';

const nodeTypes = {
  temporalResonance: TemporalResonanceNode,
  metaCognitive: MetaCognitiveLoopsNode,
  complexSystem: ComplexSystemVisioningNode,
};

interface ProtocolFlowProps {
  messages: EnhancedMessage[];
}

export const ProtocolFlow: React.FC<ProtocolFlowProps> = ({ messages }) => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  useEffect(() => {
    const newNodes: Node[] = [];
    const newEdges: Edge[] = [];

    messages.forEach((message, index) => {
      const yPosition = index * 300;
      
      // Add IAR node
      newNodes.push({
        id: `iar-${message.id}`,
        type: 'default',
        position: { x: 100, y: yPosition },
        data: { 
          label: `IAR: ${message.iar?.status || 'Pending'}`,
          confidence: message.iar?.confidence || 0
        },
        style: {
          background: '#e0f2fe',
          border: '2px solid #0284c7',
          borderRadius: '8px',
          padding: '10px',
          minWidth: '150px'
        }
      });

      // Add Temporal Resonance node
      if (message.temporal_context) {
        newNodes.push({
          id: `temporal-${message.id}`,
          type: 'temporalResonance',
          position: { x: 300, y: yPosition },
          data: { 
            temporalContext: message.temporal_context,
            isActive: true
          },
        });

        newEdges.push({
          id: `iar-temporal-${message.id}`,
          source: `iar-${message.id}`,
          target: `temporal-${message.id}`,
          animated: true,
          style: { stroke: '#3b82f6' }
        });
      }

      // Add Meta-cognitive node
      if (message.meta_cognitive_state) {
        newNodes.push({
          id: `meta-${message.id}`,
          type: 'metaCognitive',
          position: { x: 500, y: yPosition },
          data: { 
            metaCognitiveState: message.meta_cognitive_state,
            isActive: true
          },
        });

        newEdges.push({
          id: `temporal-meta-${message.id}`,
          source: `temporal-${message.id}`,
          target: `meta-${message.id}`,
          animated: true,
          style: { stroke: '#8b5cf6' }
        });
      }

      // Add Complex System Visioning node
      if (message.complex_system_visioning) {
        newNodes.push({
          id: `complex-${message.id}`,
          type: 'complexSystem',
          position: { x: 700, y: yPosition },
          data: { 
            complexSystemVisioning: message.complex_system_visioning,
            isActive: true
          },
        });

        newEdges.push({
          id: `meta-complex-${message.id}`,
          source: `meta-${message.id}`,
          target: `complex-${message.id}`,
          animated: true,
          style: { stroke: '#10b981' }
        });
      }

      // Add SPR activation nodes
      if (message.spr_activations && message.spr_activations.length > 0) {
        message.spr_activations.forEach((spr, sprIndex) => {
          const sprNodeId = `spr-${message.id}-${sprIndex}`;
          newNodes.push({
            id: sprNodeId,
            type: 'default',
            position: { x: 200, y: yPosition + 100 + (sprIndex * 50) },
            data: { 
              label: spr.spr_id,
              category: spr.category,
              confidence: spr.confidence
            },
            style: {
              background: '#fef3c7',
              border: '1px solid #f59e0b',
              borderRadius: '8px',
              padding: '10px',
              fontSize: '12px',
              minWidth: '120px'
            }
          });

          newEdges.push({
            id: `iar-spr-${message.id}-${sprIndex}`,
            source: `iar-${message.id}`,
            target: sprNodeId,
            style: { stroke: '#f59e0b' }
          });
        });
      }
    });

    setNodes(newNodes);
    setEdges(newEdges);
  }, [messages, setNodes, setEdges]);

  return (
    <div style={{ height: '100%', width: '100%' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        nodeTypes={nodeTypes}
        fitView
      >
        <Controls />
        <MiniMap />
        <Background variant={BackgroundVariant.Dots} gap={12} size={1} />
      </ReactFlow>
    </div>
  );
}; 