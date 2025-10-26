'use client';

// components/visualization/ThoughtTrailGraph.tsx
import React, { useCallback, useEffect } from 'react';
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
  BackgroundVariant,
} from 'reactflow';
import 'reactflow/dist/style.css';

// Import custom node components
import { ThoughtTrailNode } from './nodes/ThoughtTrailNode';
import { IARNode } from './nodes/IARNode';
import { SPRNode } from './nodes/SPRNode';

import { EnhancedMessage } from '@/types/protocol';

interface ThoughtTrailGraphProps {
  messages: EnhancedMessage[];
}

// Define the custom node types for ReactFlow
const nodeTypes: NodeTypes = {
  thoughtTrail: ThoughtTrailNode,
  iar: IARNode,
  spr: SPRNode,
};

export const ThoughtTrailGraph: React.FC<ThoughtTrailGraphProps> = ({ messages }) => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  // Process messages into nodes and edges whenever messages array updates
  useEffect(() => {
    const graphNodes: Node[] = [];
    const graphEdges: Edge[] = [];
    let lastMessageNodeId: string | null = null;

    messages.forEach((message, index) => {
      const messageNodeId = `msg-${index}`;
      const messageNode: Node = {
        id: messageNodeId,
        type: 'thoughtTrail',
        position: { x: 250 * index, y: 50 },
        data: { content: message.content, timestamp: message.timestamp, sender: message.sender },
      };
      graphNodes.push(messageNode);

      // Connect sequential messages
      if (lastMessageNodeId) {
        graphEdges.push({
          id: `edge-${lastMessageNodeId}-${messageNodeId}`,
          source: lastMessageNodeId,
          target: messageNodeId,
          type: 'smoothstep',
        });
      }

      // Add IAR nodes if present
      if (message.iar) {
        const iarNodeId = `iar-${index}`;
        const iarNode: Node = {
          id: iarNodeId,
          type: 'iar',
          position: { x: 250 * index + 50, y: 200 },
          data: message.iar,
        };
        graphNodes.push(iarNode);

        // Connect message to its IAR
        graphEdges.push({
          id: `edge-${messageNodeId}-${iarNodeId}`,
          source: messageNodeId,
          target: iarNodeId,
          type: 'step',
          style: { stroke: '#10b981' },
        });
      }

      // Add SPR nodes if present
      if (message.spr_activations && message.spr_activations.length > 0) {
        message.spr_activations.forEach((spr, sprIndex) => {
          const sprNodeId = `spr-${index}-${sprIndex}`;
          const sprNode: Node = {
            id: sprNodeId,
            type: 'spr',
            position: { x: 250 * index - 50, y: 200 + (sprIndex * 120) },
            data: spr,
          };
          graphNodes.push(sprNode);

          // Connect message to its SPR
          graphEdges.push({
            id: `edge-${messageNodeId}-${sprNodeId}`,
            source: messageNodeId,
            target: sprNodeId,
            type: 'step',
            style: { stroke: '#8b5cf6' },
          });
        });
      }

      lastMessageNodeId = messageNodeId;
    });

    setNodes(graphNodes);
    setEdges(graphEdges);
  }, [messages, setNodes, setEdges]);

  const onConnect = useCallback(
    (params: Edge | Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  return (
    <div style={{ width: '100%', height: '600px' }}>
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
        <Background variant={BackgroundVariant.Dots} gap={12} size={1} />
      </ReactFlow>
    </div>
  );
}; 