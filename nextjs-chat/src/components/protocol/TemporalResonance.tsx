import React from 'react';
import { Handle, Position } from 'reactflow';
import { TemporalContext } from '../../types/protocol';

interface TemporalResonanceNodeProps {
  data: {
    temporalContext: TemporalContext;
    isActive: boolean;
  };
}

export const TemporalResonanceNode: React.FC<TemporalResonanceNodeProps> = ({ data }) => {
  const { temporalContext, isActive } = data;
  
  return (
    <div className={`temporal-resonance-node ${isActive ? 'active' : ''}`}>
      <Handle type="target" position={Position.Top} />
      
      <div className="node-header">
        <h4>Temporal Resonance</h4>
        <span className="time-horizon">{temporalContext.time_horizon}</span>
      </div>
      
      <div className="temporal-content">
        <div className="temporal-section">
          <h5>Historical Context</h5>
          <ul>
            {temporalContext.historical_context.map((context, index) => (
              <li key={index}>{context}</li>
            ))}
          </ul>
        </div>
        
        <div className="temporal-section">
          <h5>Future Projections</h5>
          <ul>
            {temporalContext.future_projection.map((projection, index) => (
              <li key={index}>{projection}</li>
            ))}
          </ul>
        </div>
        
        <div className="temporal-section">
          <h5>Current State</h5>
          <p>{temporalContext.current_state}</p>
        </div>
        
        {temporalContext.causal_lag_detection && (
          <div className="temporal-section">
            <h5>Causal Lag Detection</h5>
            <ul>
              {temporalContext.causal_lag_detection.map((lag, index) => (
                <li key={index}>{lag}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
      
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}; 