'use client';
import React, { useMemo } from 'react';
import ReactFlow, { MiniMap, Controls, Background, Node, Edge, OnNodesChange, OnEdgesChange, OnConnect } from 'reactflow';
import 'reactflow/dist/style.css';

interface CanvasProps {
  nodes: Node[];
  edges: Edge[];
  onNodesChange: OnNodesChange;
  onEdgesChange: OnEdgesChange;
  onConnect: OnConnect;
}

const Canvas: React.FC<CanvasProps> = ({ nodes, edges, onNodesChange, onEdgesChange, onConnect }) => {
  const nodeTypes = useMemo(() => ({}), []);
  const edgeTypes = useMemo(() => ({}), []);

  return (
    <div style={{ width: '100%', height: '100%' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        fitView
      >
        <Controls />
        <MiniMap />
        <Background />
      </ReactFlow>
    </div>
  );
};

export default Canvas;
