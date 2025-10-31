// components/visualization/nodes/SPRNode.tsx
import React from 'react';
import { Handle, Position } from 'reactflow';
import { SPR_Data } from '@/types/protocol';

interface SPRNodeProps {
  data: SPR_Data;
}

export const SPRNode: React.FC<SPRNodeProps> = ({ data }) => {
  const getCategoryColor = (category: string) => {
    switch (category.toLowerCase()) {
      case 'cognitive': return '#9c88ff';
      case 'temporal': return '#ffa8a8';
      case 'system': return '#69db7c';
      case 'protocol': return '#74c0fc';
      default: return '#4ecdc4';
    }
  };

  const getActivationIntensity = (confidence: number) => {
    return Math.min(Math.max(confidence, 0.2), 1.0);
  };

  return (
    <div 
      className="spr-node"
      style={{ 
        opacity: getActivationIntensity(data.confidence),
        borderColor: getCategoryColor(data.category)
      }}
    >
      <Handle type="target" position={Position.Top} />
      
      <div className="node-header">
        <div className="node-title">SPR</div>
        <div 
          className="category-badge"
          style={{ backgroundColor: getCategoryColor(data.category) }}
        >
          {data.category}
        </div>
      </div>
      
      <div className="spr-id">{data.spr_id}</div>
      
      <div className="node-content">
        <div className="definition">
          {data.definition.length > 80 
            ? `${data.definition.substring(0, 80)}...` 
            : data.definition
          }
        </div>
        
        <div className="activation-bar">
          <div className="activation-label">Confidence</div>
          <div className="activation-meter">
            <div 
              className="activation-fill"
              style={{ 
                width: `${data.confidence * 100}%`,
                backgroundColor: getCategoryColor(data.category)
              }}
            />
          </div>
        </div>
      </div>
      
      <Handle type="source" position={Position.Bottom} />
      
      <style jsx>{`
        .spr-node {
          background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%);
          border: 2px solid;
          border-radius: 8px;
          padding: 10px;
          min-width: 160px;
          max-width: 200px;
          color: white;
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
          transition: opacity 0.3s ease;
        }
        
        .node-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 6px;
        }
        
        .node-title {
          font-weight: bold;
          font-size: 12px;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }
        
        .category-badge {
          padding: 2px 6px;
          border-radius: 4px;
          font-size: 9px;
          font-weight: bold;
          text-transform: uppercase;
        }
        
        .spr-id {
          font-weight: bold;
          font-size: 13px;
          margin-bottom: 8px;
          text-align: center;
          background: rgba(255, 255, 255, 0.1);
          padding: 4px;
          border-radius: 4px;
        }
        
        .node-content {
          font-size: 10px;
        }
        
        .definition {
          line-height: 1.3;
          margin-bottom: 8px;
          word-wrap: break-word;
        }
        
        .activation-bar {
          margin-top: 8px;
        }
        
        .activation-label {
          font-size: 9px;
          margin-bottom: 2px;
          opacity: 0.8;
        }
        
        .activation-meter {
          height: 4px;
          background: rgba(255, 255, 255, 0.2);
          border-radius: 2px;
          overflow: hidden;
        }
        
        .activation-fill {
          height: 100%;
          transition: width 0.3s ease;
        }
      `}</style>
    </div>
  );
}; 