// components/visualization/nodes/ThoughtTrailNode.tsx
import React from 'react';
import { Handle, Position } from 'reactflow';

interface ThoughtTrailNodeData {
  content: string;
  timestamp: string;
  sender: 'user' | 'assistant';
}

interface ThoughtTrailNodeProps {
  data: ThoughtTrailNodeData;
}

export const ThoughtTrailNode: React.FC<ThoughtTrailNodeProps> = ({ data }) => {
  return (
    <div className="thought-trail-node">
      <Handle type="target" position={Position.Left} />
      
      <div className="node-header">
        <div className="node-title">ThoughtTraiL</div>
        <div className="node-timestamp">{new Date(data.timestamp).toLocaleTimeString()}</div>
      </div>
      
      <div className="node-content">
        {data.content.length > 100 
          ? `${data.content.substring(0, 100)}...` 
          : data.content
        }
      </div>
      
      <Handle type="source" position={Position.Right} />
      <Handle type="source" position={Position.Bottom} />
      
      <style jsx>{`
        .thought-trail-node {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          border: 2px solid #4a5568;
          border-radius: 8px;
          padding: 12px;
          min-width: 200px;
          max-width: 250px;
          color: white;
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .node-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 8px;
          border-bottom: 1px solid rgba(255, 255, 255, 0.2);
          padding-bottom: 4px;
        }
        
        .node-title {
          font-weight: bold;
          font-size: 12px;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }
        
        .node-timestamp {
          font-size: 10px;
          opacity: 0.8;
        }
        
        .node-content {
          font-size: 11px;
          line-height: 1.4;
          word-wrap: break-word;
        }
      `}</style>
    </div>
  );
}; 