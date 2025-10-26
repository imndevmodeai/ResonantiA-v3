// components/visualization/nodes/IARNode.tsx
import React from 'react';
import { Handle, Position } from 'reactflow';
import { IAR_Data } from '@/types/protocol';

interface IARNodeProps {
  data: IAR_Data;
}

export const IARNode: React.FC<IARNodeProps> = ({ data }) => {
  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'success': return '#48bb78';
      case 'failure': return '#f56565';
      case 'partial': return '#ed8936';
      default: return '#4299e1';
    }
  };

  return (
    <div className="iar-node">
      <Handle type="target" position={Position.Top} />
      
      <div className="node-header">
        <div className="node-title">IAR</div>
        <div 
          className="status-indicator"
          style={{ backgroundColor: getStatusColor(data.status) }}
        >
          {data.status}
        </div>
      </div>
      
      <div className="node-content">
        <div className="summary">{data.summary}</div>
        <div className="metrics">
          <div className="metric">
            <span>Confidence:</span>
            <span>{(data.confidence * 100).toFixed(0)}%</span>
          </div>
          <div className="metric">
            <span>Alignment:</span>
            <span>{data.alignment_check}</span>
          </div>
        </div>
      </div>
      
      <Handle type="source" position={Position.Bottom} />
      
      <style jsx>{`
        .iar-node {
          background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
          border: 2px solid #c0392b;
          border-radius: 8px;
          padding: 10px;
          min-width: 180px;
          max-width: 220px;
          color: white;
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .node-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 8px;
        }
        
        .node-title {
          font-weight: bold;
          font-size: 12px;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }
        
        .status-indicator {
          padding: 2px 6px;
          border-radius: 4px;
          font-size: 10px;
          font-weight: bold;
          text-transform: uppercase;
        }
        
        .node-content {
          font-size: 11px;
        }
        
        .summary {
          margin-bottom: 8px;
          line-height: 1.3;
          word-wrap: break-word;
        }
        
        .metrics {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }
        
        .metric {
          display: flex;
          justify-content: space-between;
          font-size: 10px;
          opacity: 0.9;
        }
      `}</style>
    </div>
  );
}; 