import { NodeTypes, EdgeTypes } from 'reactflow';

// Define node types outside component to avoid React Flow warnings
export const nodeTypes: NodeTypes = {
  default: ({ data }) => (
    <div className="px-4 py-2 shadow-md rounded-md bg-white border-2 border-stone-400">
      <div className="font-bold">{data.label}</div>
      {data.description && (
        <div className="text-sm text-gray-600">{data.description}</div>
      )}
    </div>
  ),
  aco: ({ data }) => (
    <div className="px-4 py-2 shadow-md rounded-md bg-blue-100 border-2 border-blue-400">
      <div className="font-bold text-blue-800">🧠 {data.label}</div>
      {data.description && (
        <div className="text-sm text-blue-600">{data.description}</div>
      )}
    </div>
  ),
  process: ({ data }) => (
    <div className="px-4 py-2 shadow-md rounded-md bg-green-100 border-2 border-green-400">
      <div className="font-bold text-green-800">⚙️ {data.label}</div>
      {data.description && (
        <div className="text-sm text-green-600">{data.description}</div>
      )}
    </div>
  ),
};

// Define edge types outside component
export const edgeTypes: EdgeTypes = {
  default: {
    style: { stroke: '#b1b1b7' },
    type: 'smoothstep',
  },
  cognitive: {
    style: { stroke: '#3b82f6', strokeWidth: 2 },
    type: 'smoothstep',
  },
};
