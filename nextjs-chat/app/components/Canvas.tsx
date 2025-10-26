'use client';

import React, { useMemo } from 'react';
import ReactFlow, { MiniMap, Controls, Background, NodeTypes, EdgeTypes } from 'reactflow';
import { useStore } from '@/app/store';
import 'reactflow/dist/style.css';

export function Canvas() {
  const { logEntries } = useStore();

  // Define node types with useMemo to prevent recreation
  const nodeTypes = useMemo((): NodeTypes => ({
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
  }), []);

  // Define edge types with useMemo to prevent recreation
  const edgeTypes = useMemo((): EdgeTypes => ({
    default: {
      style: { stroke: '#b1b1b7' },
      type: 'smoothstep',
    },
    cognitive: {
      style: { stroke: '#3b82f6', strokeWidth: 2 },
      type: 'smoothstep',
    },
  }), []);

  // Create nodes based on recent activity - memoized to prevent recreation
  const nodes = useMemo(() => {
    const baseNodes = [
      { 
        id: 'arche-core', 
        type: 'aco',
        position: { x: 100, y: 100 }, 
        data: { 
          label: 'ArchE Core',
          description: 'Adaptive Cognitive Orchestrator'
        } 
      },
    ];

    // Add nodes for recent thought trail entries
    const recentEntries = logEntries.slice(-3);
    recentEntries.forEach((entry, index) => {
      if (entry.meta?.action_type) {
        baseNodes.push({
          id: `process-${index}`,
          type: 'process',
          position: { x: 300 + (index * 150), y: 100 + (index * 50) },
          data: {
            label: entry.meta.action_type.replace(/_/g, ' '),
            description: entry.msg
          }
        });
      }
    });

    return baseNodes;
  }, [logEntries]);

  // Create edges connecting the nodes - memoized to prevent recreation
  const edges = useMemo(() => {
    const baseEdges = [];
    
    // Connect ArchE Core to process nodes
    const processNodes = nodes.filter(node => node.type === 'process');
    processNodes.forEach((node, index) => {
      baseEdges.push({
        id: `edge-${index}`,
        source: 'arche-core',
        target: node.id,
        type: 'cognitive',
        animated: true,
        sourceHandle: 'right',
        targetHandle: 'left',
      });
    });

    return baseEdges;
  }, [nodes]);

  return (
    <div className="w-full h-full rounded-lg shadow-inner bg-gray-100 dark:bg-zinc-800">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        defaultViewport={{ x: 0, y: 0, zoom: 1 }}
      >
        <Controls />
        <MiniMap />
        <Background />
      </ReactFlow>
    </div>
  );
}
