import React from 'react';
import ReactFlow, { Controls, Background, Node, Edge, OnNodesChange, OnEdgesChange, OnConnect } from 'reactflow';
import 'reactflow/dist/style.css';

interface CanvasProps {
  nodes: Node[];
  edges: Edge[];
  onNodesChange: OnNodesChange;
  onEdgesChange: OnEdgesChange;
  onConnect: OnConnect;
}

const Canvas: React.FC<CanvasProps> = ({ nodes, edges, onNodesChange, onEdgesChange, onConnect }) => {
  return (
    <div style={{ width: '100%', height: '100%' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        fitView
      >
        <Controls />
        <Background />
      </ReactFlow>
    </div>
  );
};

export default Canvas;
