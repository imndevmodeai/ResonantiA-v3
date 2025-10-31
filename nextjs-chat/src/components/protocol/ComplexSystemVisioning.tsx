import React from 'react';
import { Handle, Position } from 'reactflow';
import { ComplexSystemVisioningData } from '../../types/protocol';

interface ComplexSystemVisioningNodeProps {
  data: {
    complexSystemVisioning: ComplexSystemVisioningData;
    isActive: boolean;
  };
}

export const ComplexSystemVisioningNode: React.FC<ComplexSystemVisioningNodeProps> = ({ data }) => {
  const { complexSystemVisioning, isActive } = data;
  
  return (
    <div className={`complex-system-node ${isActive ? 'active' : ''}`}>
      <Handle type="target" position={Position.Top} />
      
      <div className="node-header">
        <h4>Complex System Visioning</h4>
        <span className="scenario-name">{complexSystemVisioning.scenario_name}</span>
      </div>
      
      <div className="complex-content">
        <div className="scenario-info">
          <h5>Time Horizon</h5>
          <p>{complexSystemVisioning.time_horizon}</p>
        </div>
        
        <div className="agent-groups">
          <h5>Agent Groups ({complexSystemVisioning.agent_groups.length})</h5>
          <ul>
            {complexSystemVisioning.agent_groups.map((group, index) => (
              <li key={index}>{group.name}</li>
            ))}
          </ul>
        </div>
        
        <div className="environmental-factors">
          <h5>Environmental Factors ({complexSystemVisioning.environmental_factors.length})</h5>
          <ul>
            {complexSystemVisioning.environmental_factors.map((factor, index) => (
              <li key={index}>{factor.name}</li>
            ))}
          </ul>
        </div>
        
        <div className="realism-assessment">
          <h5>Realism Score</h5>
          <p>{complexSystemVisioning.realism_assessment.overall_score}/10</p>
        </div>
        
        <div className="emergence-patterns">
          <h5>Emergence Patterns</h5>
          <ul>
            {complexSystemVisioning.emergence_patterns.map((pattern, index) => (
              <li key={index}>{pattern}</li>
            ))}
          </ul>
        </div>
      </div>
      
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}; 