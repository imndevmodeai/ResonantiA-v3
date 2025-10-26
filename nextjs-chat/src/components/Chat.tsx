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
import { CognitiveStream } from './CognitiveStream';
import { VCDRichEvent } from '../types'; // Assuming types are defined in a separate file

const initialNodes: Node[] = [
  {
    id: 'root',
    type: 'input',
    data: { label: 'User Directive' },
    position: { x: 250, y: 5 },
  },
];

const Chat = () => {
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [cognitiveStream, setCognitiveStream] = useState<VCDRichEvent[]>([]);
  const [nodes, setNodes] = useState<Node[]>(initialNodes);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [message, setMessage] = useState<string>('');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [playbookMode, setPlaybookMode] = useState(false);
  const websocket = useRef<WebSocket | null>(null);

  const onNodesChange = useCallback((changes: any) => setNodes((nds) => applyNodeChanges(changes, nds)), []);
  const onEdgesChange = useCallback((changes: any) => setEdges((eds) => applyEdgeChanges(changes, eds)), []);

  const onConnect = useCallback((params: Connection | Edge) => {
    setEdges((eds) => addEdge(params, eds));
  }, [setEdges]);

      useEffect(() => {
    if (!websocket.current) {
      const wsUrl = process.env.NEXT_PUBLIC_WEBSOCKET_URL || 'ws://localhost:8765';
          console.log('🔗 Connecting to ArchE Cognitive Bus:', wsUrl);
      const ws = new WebSocket(wsUrl);
      websocket.current = ws;

      ws.onopen = () => {
        console.log('✅ WebSocket connection established.');
            setIsConnected(true);
      };

      ws.onclose = () => {
        console.log('❌ WebSocket connection closed.');
        setIsConnected(false);
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
          
          if (eventData.type === 'rich_event' && eventData.payload) {
            setCognitiveStream(prev => [...prev, eventData.payload]);

            if(eventData.payload.event_type === 'analysis_start') {
              setSessionId(eventData.payload.metadata?.session_id || null);
            }
            
            // Basic node creation for phases
            if (eventData.payload.event_type === 'phase_start') {
              const phaseNode: Node = {
                id: eventData.payload.event_id,
                data: { label: `Phase: ${eventData.payload.phase}` },
                position: { x: Math.random() * 400, y: nodes.length * 100 },
              };
              setNodes((nds) => [...nds, phaseNode]);
            }
          } else if (eventData.type === 'system') {
            const systemEvent: VCDRichEvent = {
              event_id: `system-${Date.now()}`,
              event_type: 'system_message' as any,
              timestamp: eventData.timestamp,
              phase: 'System',
              title: 'System Message',
              description: eventData.content,
            };
            setCognitiveStream(prev => [...prev, systemEvent]);
          }

        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };
    }

    return () => {
      if (websocket.current?.readyState === 1) {
        websocket.current.close();
      }
    };
  }, [nodes]);

  const generateDynamicPlaybook = async (question: string) => {
    try {
      const response = await fetch('/api/dynamic-playbook', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question, buildPlaybook: true }),
      });

      const result = await response.json();
      
      if (result.status === 'success') {
        // Add playbook node to the graph
        const playbookNode: Node = {
          id: `playbook-${new Date().getTime()}`,
          data: { label: `Generated Playbook: ${result.playbook?.name}` },
          position: { x: 250, y: 250 },
          style: { backgroundColor: '#10b981', color: 'white' }
        };
        setNodes((nds) => [...nds, playbookNode]);
        
        // Add system message
        const systemEvent: VCDRichEvent = {
          event_id: `playbook-${Date.now()}`,
          event_type: 'system_message' as any,
          timestamp: new Date().toISOString(),
          phase: 'Playbook Generation',
          title: 'Dynamic Playbook Generated',
          description: `Generated playbook: ${result.playbook_path}`,
        };
        setCognitiveStream(prev => [...prev, systemEvent]);
      }
    } catch (error) {
      console.error('Failed to generate playbook:', error);
    }
  };

  const sendMessage = () => {
    if (websocket.current?.readyState === WebSocket.OPEN && message) {
      if (playbookMode) {
        // Generate dynamic playbook
        generateDynamicPlaybook(message);
      } else {
        // Regular chat mode
        const queryPacket = {
          type: 'query',
          payload: message,
        };
        websocket.current.send(JSON.stringify(queryPacket));
      }
      
      const userNode: Node = {
        id: `user-${new Date().getTime()}`,
        type: 'output',
        data: { label: playbookMode ? `Playbook: "${message}"` : `IMnDEVmode: "${message}"`},
        position: { x: 250, y: 150}
      };
      setNodes((nds) => [nds[0], userNode]);
      setEdges((eds) => addEdge({ id: `e-root-${userNode.id}`, source: 'root', target: userNode.id, animated: false }, eds));

      setMessage('');
    }
  };
        
        return (
    <div className="flex h-screen w-full bg-gray-900 text-gray-100 font-sans">
      {/* Left Panel: Thought Flow Graph */}
      <div className="w-1/2 h-full border-r border-gray-700">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          fitView
          className="bg-gray-800"
        >
          <Background color="#4a5568" gap={16} />
          <Controls />
          <Panel position="top-left" className="p-2 bg-gray-900 rounded-md text-sm border border-gray-700">
            Cognitive Flow Graph
          </Panel>
        </ReactFlow>
            </div>
            
      {/* Right Panel: Control & Cognitive Stream */}
      <div className="w-1/2 h-full flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-gray-700 bg-gray-800">
          <h1 className="text-2xl font-bold text-cyan-400">ArchE Visual Cognitive Debugger</h1>
          <p className="text-md text-gray-400">ResonantiA Protocol v4.0</p>
          <div className="mt-2 flex justify-between text-sm">
            <div>
              Status: 
              <span className={`ml-2 font-semibold ${isConnected ? 'text-green-400' : 'text-red-400'}`}>
                {isConnected ? 'LIVE' : 'DISCONNECTED'}
              </span>
            </div>
            <div className="text-gray-500">
              Session ID: {sessionId || 'N/A'}
              </div>
            </div>
            <div className="mt-3">
              <button
                onClick={() => setPlaybookMode(!playbookMode)}
                className={`px-4 py-2 rounded-md font-semibold transition-colors ${
                  playbookMode 
                    ? 'bg-green-600 text-white' 
                    : 'bg-gray-600 text-gray-300 hover:bg-gray-500'
                }`}
              >
                {playbookMode ? '🔧 Playbook Mode' : '💬 Chat Mode'}
              </button>
            </div>
          </div>

        {/* Cognitive Stream */}
        <div className="flex-grow p-4 overflow-y-auto bg-gray-900">
          <CognitiveStream events={cognitiveStream} />
              </div>

        {/* Input Area */}
        <div className="p-4 border-t border-gray-700 bg-gray-800">
                <textarea
            className="w-full p-3 bg-gray-700 rounded-md focus:outline-none focus:ring-2 focus:ring-cyan-500 text-gray-100 placeholder-gray-400"
            rows={4}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder={playbookMode ? "Ask a question to generate a dynamic playbook..." : "Enter your directive for ArchE..."}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
              }
            }}
                />
                <button 
                  onClick={sendMessage} 
            disabled={!isConnected || !message}
            className="w-full mt-2 p-3 bg-cyan-600 hover:bg-cyan-700 disabled:bg-gray-600 rounded-md font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:ring-offset-2 focus:ring-offset-gray-800"
          >
{playbookMode ? 'Generate Playbook' : 'Send Directive'}
                </button>
            </div>
          </div>
        </div>
      );
    };

    export default Chat; 