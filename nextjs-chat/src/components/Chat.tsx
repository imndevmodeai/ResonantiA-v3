"use client";

import React, { useState, useEffect, useRef, useCallback } from 'react';
import ReactFlow, {
  Controls,
  Background,
  addEdge,
  Connection,
  Edge,
  Node,
  Panel,
  applyNodeChanges,
  applyEdgeChanges,
} from 'reactflow';
import 'reactflow/dist/style.css';


const initialNodes: Node[] = [
  {
    id: '1',
    type: 'input',
    data: { label: 'Directive Input' },
    position: { x: 250, y: 5 },
  },
];

const VCDUI = () => {
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [cognitiveStream, setCognitiveStream] = useState<any[]>([]);
  const [nodes, setNodes] = useState<Node[]>(initialNodes);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [message, setMessage] = useState<string>('');
  const websocket = useRef<WebSocket | null>(null);

  const onNodesChange = useCallback((changes: any) => setNodes((nds) => applyNodeChanges(changes, nds)), []);
  const onEdgesChange = useCallback((changes: any) => setEdges((eds) => applyEdgeChanges(changes, eds)), []);

  const onConnect = useCallback((params: Connection | Edge) => {
    setEdges((eds) => addEdge(params, eds));
  }, [setEdges]);

      useEffect(() => {
    // Connect only once
    if (!websocket.current) {
      const wsUrl = process.env.NEXT_PUBLIC_WEBSOCKET_URL || 'ws://localhost:8765';
          console.log('🔗 Connecting to ArchE Cognitive Bus:', wsUrl);
      const ws = new WebSocket(wsUrl);
      websocket.current = ws;

      ws.onopen = () => {
        console.log('✅ WebSocket connection established.');
            setIsConnected(true);
        setCognitiveStream(prev => [...prev, { type: 'SYSTEM', content: 'Connection Established.', timestamp: new Date().toISOString() }]);
      };

      ws.onclose = () => {
        console.log('❌ WebSocket connection closed.');
        setIsConnected(false);
        // Clean up the ref on close
        websocket.current = null;
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        ws.close();
      };

      ws.onmessage = (event) => {
        try {
          const eventData = JSON.parse(event.data);
          console.log('Received event:', eventData);
          setCognitiveStream(prev => [...prev, eventData]);

          // Logic to update the graph
          if (eventData.type === 'thought_process_step') {
              const newNode: Node = {
                  id: eventData.step_id,
                  data: { label: `${eventData.step_name}` },
                  position: { x: Math.random() * 400, y: Math.random() * 400 }, // Position randomly for now
              };
              setNodes((nds) => [...nds, newNode]);

              if (eventData.parent_id) {
                  const newEdge: Edge = {
                      id: `e-${eventData.parent_id}-${eventData.step_id}`,
                      source: eventData.parent_id,
                      target: eventData.step_id,
                      animated: true,
                  };
                  setEdges((eds) => addEdge(newEdge, eds));
              }
          }

            } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };
    }

    // Cleanup function to close the socket when the component unmounts
        return () => {
      if (websocket.current?.readyState === 1) { // 1 = OPEN
        websocket.current.close();
          }
        };
      }, []);

      const sendMessage = () => {
    if (websocket.current?.readyState === WebSocket.OPEN && message) {
      const queryPacket = {
        type: 'query',
        payload: message,
      };
      websocket.current.send(JSON.stringify(queryPacket));
      
      const userNode: Node = {
        id: `user-${new Date().getTime()}`,
        type: 'output',
        data: { label: `IMnDEVmode: "${message}"`},
        position: { x: 250, y: 150}
      };
      setNodes((nds) => [nds[0], userNode]);
      setEdges((eds) => addEdge({ id: `e-1-${userNode.id}`, source: '1', target: userNode.id, animated: false }, eds));

      setMessage('');
    }
  };
        
        return (
    <div className="flex h-screen w-full bg-[#1e1e1e] text-gray-200 font-sans">
      {/* Left Panel: Thought Flow Graph */}
      <div className="w-2/3 h-full border-r border-gray-700">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          fitView
        >
          <Background color="#aaa" gap={16} />
          <Controls />
          <Panel position="top-left" className="p-2 bg-gray-800 rounded-md text-sm">
            Thought Flow
          </Panel>
        </ReactFlow>
            </div>
            
      {/* Right Panel: Control & Cognitive Stream */}
      <div className="w-1/3 h-full flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-gray-700 bg-[#252526]">
          <h1 className="text-xl font-bold">ArchE Resonant Interface</h1>
          <p className="text-sm text-gray-400">ResonantiA Protocol v3.5-GP</p>
          <div className="mt-2 text-sm">
            Status: 
            <span className={`ml-2 font-semibold ${isConnected ? 'text-green-400' : 'text-red-400'}`}>
              {isConnected ? 'Connected' : 'Disconnected'}
                  </span>
          </div>
              </div>

        {/* Cognitive Stream */}
        <div className="flex-grow p-4 overflow-y-auto">
          <h2 className="text-lg font-semibold mb-2">Cognitive Stream</h2>
          <div className="space-y-3">
            {cognitiveStream.map((event, index) => (
              <div key={index} className="p-2 bg-[#2d2d2d] rounded-md text-sm">
                <p className="font-bold text-cyan-400">[{event.type || 'EVENT'}]</p>
                <p className="whitespace-pre-wrap">{typeof event.content === 'object' ? JSON.stringify(event.content, null, 2) : event.content}</p>
                <p className="text-xs text-gray-500 text-right">{event.timestamp}</p>
              </div>
            ))}
          </div>
              </div>

        {/* Input Area */}
        <div className="p-4 border-t border-gray-700 bg-[#252526]">
                <textarea
            className="w-full p-2 bg-[#3c3c3c] rounded-md focus:outline-none focus:ring-2 focus:ring-cyan-500"
                  rows={3}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Enter your query for ArchE..."
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
              }
            }}
                />
                <button 
                  onClick={sendMessage} 
            className="w-full mt-2 p-2 bg-cyan-600 hover:bg-cyan-700 rounded-md font-semibold transition-colors"
          >
            Send Directive
                </button>
            </div>
          </div>
        </div>
      );
    };

export default VCDUI; 