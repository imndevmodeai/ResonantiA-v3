import React from 'react';
import { Handle, Position } from 'reactflow';
import { MetaCognitiveState } from '../../types/protocol';

interface MetaCognitiveLoopsNodeProps {
  data: {
    metaCognitiveState: MetaCognitiveState;
    isActive: boolean;
  };
}

export const MetaCognitiveLoopsNode: React.FC<MetaCognitiveLoopsNodeProps> = ({ data }) => {
  const { metaCognitiveState, isActive } = data;
  
  return (
    <div className={`meta-cognitive-node ${isActive ? 'active' : ''}`}>
      <Handle type="target" position={Position.Top} />
      
      <div className="node-header">
        <h4>Meta-cognitive Loops</h4>
        <span className={`status ${metaCognitiveState.metacognitive_shift_active ? 'active' : 'inactive'}`}>
          {metaCognitiveState.metacognitive_shift_active ? 'Active' : 'Inactive'}
        </span>
      </div>
      
      <div className="meta-cognitive-content">
        {metaCognitiveState.sirc_phase && (
          <div className="sirc-phase">
            <h5>SIRC Phase</h5>
            <p>{metaCognitiveState.sirc_phase}</p>
          </div>
        )}
        
        <div className="crc-status">
          <h5>CRC Status</h5>
          <p>{metaCognitiveState.crc_active ? 'Active' : 'Inactive'}</p>
        </div>
        
        <div className="dissonance-status">
          <h5>Dissonance Detection</h5>
          <p>{metaCognitiveState.dissonance_detected ? 'Dissonance Detected' : 'No Dissonance'}</p>
        </div>
        
        {metaCognitiveState.correction_applied && (
          <div className="correction-applied">
            <h5>Correction Applied</h5>
            <p>{metaCognitiveState.correction_applied}</p>
          </div>
        )}
      </div>
      
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}; 