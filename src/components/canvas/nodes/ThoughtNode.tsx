import React from 'react';
import { Handle, Position } from 'reactflow';

const ThoughtNode = ({ data }) => {
  return (
    <div style={{ background: '#fffae6', border: '1px solid #ffc107', borderRadius: '5px', padding: '10px', minWidth: '200px' }}>
      <Handle type="target" position={Position.Top} />
      <div>
        <strong>Thought</strong>
      </div>
      <div style={{ marginTop: '5px' }}>
        <p>{data.label}</p>
      </div>
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
};

export default ThoughtNode;
