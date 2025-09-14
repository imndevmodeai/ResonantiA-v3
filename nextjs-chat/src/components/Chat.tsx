    'use client';

    // components/Chat.tsx
    // ResonantiA Protocol v3.1-CA Enhanced Chat Interface

    import React, { useState, useEffect, useRef } from 'react';
    import { ThoughtTrailGraph } from './visualization/ThoughtTrailGraph';
    import { ProtocolFlow } from './visualization/ProtocolFlow';
    import { EnhancedMessage } from '@/types/protocol';
    import Link from 'next/link';

    interface ChatProps {}

    export const Chat: React.FC<ChatProps> = () => {
      const [messages, setMessages] = useState<EnhancedMessage[]>([]);
      const [inputValue, setInputValue] = useState('');
      const [isConnected, setIsConnected] = useState(false);
      const [connectionStatus, setConnectionStatus] = useState('Disconnected');
      const [activeVisualization, setActiveVisualization] = useState<'thought-trail' | 'protocol-flow'>('protocol-flow');
      const wsRef = useRef<WebSocket | null>(null);
      const messagesEndRef = useRef<HTMLDivElement>(null);

      // DRCL UI state
      const [drclRunning, setDrclRunning] = useState(false);
      const [drclStatus, setDrclStatus] = useState<string | null>(null);
      const [drclEnvelope, setDrclEnvelope] = useState<any>(null);
      const [drclValidation, setDrclValidation] = useState<any>(null);
      const [showEnvelope, setShowEnvelope] = useState(false);

      // WebSocket connection setup
      useEffect(() => {
        const connectWebSocket = () => {
          const wsUrl = process.env.WEBSOCKET_URL || 'ws://localhost:8765';
          console.log('🔗 Connecting to ArchE Cognitive Bus:', wsUrl);
          
          wsRef.current = new WebSocket(wsUrl);

          wsRef.current.onopen = () => {
            console.log('✅ Connected to ArchE Cognitive Bus');
            setIsConnected(true);
            setConnectionStatus('Connected - Protocol Active');
          };

          wsRef.current.onmessage = (event) => {
            try {
              const data = JSON.parse(event.data);

              if (data.message_type === 'drcl_status_update') {
                setDrclStatus(data.payload.drclStatus);
                return;
              }

              if (data.message_type === 'drcl_envelope') {
                setDrclEnvelope(data.payload.envelope);
                setDrclValidation(data.payload.validation);
                setDrclStatus('Completed');
                setShowEnvelope(true);
                return;
              }

              const enhancedMessage: EnhancedMessage = data;
              console.log('📨 Received enhanced message:', enhancedMessage);
              
              // Ensure content is always a string
              if (enhancedMessage.content && typeof enhancedMessage.content !== 'string') {
                enhancedMessage.content = JSON.stringify(enhancedMessage.content, null, 2);
              }
              
              setMessages(prev => [...prev, enhancedMessage]);
            } catch (error) {
              // Fallback for non-JSON messages
              console.log('📨 Received raw message:', event.data);
              const fallbackMessage: EnhancedMessage = {
                id: Date.now().toString(),
                content: event.data,
                timestamp: new Date().toISOString(),
                sender: 'arche',
                message_type: 'chat',
                protocol_compliance: false,
                iar: undefined,
                spr_activations: undefined,
                temporal_context: undefined,
                meta_cognitive_state: undefined,
                complex_system_visioning: undefined,
                implementation_resonance: undefined,
                thought_trail: undefined,
                protocol_version: undefined,
                protocol_init: undefined,
                protocol_error: {
                  message: 'Raw non-JSON message received',
                  error: 'parse_error',
                  fallback_mode: true
                }
              };
              setMessages(prev => [...prev, fallbackMessage]);
            }
          };

          wsRef.current.onclose = () => {
            console.log('❌ Disconnected from ArchE Cognitive Bus');
            setIsConnected(false);
            setConnectionStatus('Disconnected - Attempting Reconnect');
            
            // Attempt to reconnect after 3 seconds
            setTimeout(() => {
              if (!isConnected) {
                connectWebSocket();
              }
            }, 3000);
          };

          wsRef.current.onerror = (error) => {
            console.error('🚨 WebSocket error:', error);
            setConnectionStatus('Connection Error');
          };
        };

        connectWebSocket();

        // Cleanup on unmount
        return () => {
          if (wsRef.current) {
            wsRef.current.close();
          }
        };
      }, []);

      // Auto-scroll to bottom when new messages arrive
      useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
      }, [messages]);

      const sendMessage = () => {
        if (!inputValue.trim()) return;

        const userMessage: EnhancedMessage = {
          id: Date.now().toString(),
          content: inputValue,
          timestamp: new Date().toISOString(),
          sender: 'user',
          message_type: 'chat',
          protocol_compliance: true,
          iar: undefined,
          spr_activations: undefined,
          temporal_context: undefined,
          meta_cognitive_state: undefined,
          complex_system_visioning: undefined,
          implementation_resonance: undefined,
          thought_trail: undefined,
          protocol_version: undefined,
          protocol_init: undefined,
          protocol_error: undefined
        };

        // Add user message to local state immediately
        setMessages(prev => [...prev, userMessage]);

        // Send to WebSocket server or fall back to DRCL API
        const socketOpen = wsRef.current && wsRef.current.readyState === WebSocket.OPEN;
        if (socketOpen) {
          const messagePayload = {
            type: 'query',
            payload: inputValue
          };
          wsRef.current!.send(JSON.stringify(messagePayload));
          setInputValue('');
        } else {
          // Fallback: call DRCL API with this query as goal
          (async () => {
            try {
              setDrclRunning(true);
              setDrclStatus('Running DRCL…');
              setShowEnvelope(true);
              const initial_context = {
                goal: inputValue,
                constraints: {
                  ui_entry: [
                    'nextjs-chat/src/components/Chat.tsx'
                  ],
                  schema_path: 'protocol/drcl_envelope.schema.json',
                  workflow_path: 'Happier/workflows/distributed_resonant_corrective_loop.json',
                  single_surface: true
                },
                desired_outputs: [
                  'RISE mode decision',
                  'UI integration plan',
                  'assembled DRCL envelope',
                  'schema validation result'
                ]
              };
              const res = await fetch('/api/drcl', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ initial_context })
              });
              const data = await res.json();
              setDrclEnvelope(data.envelope || data);
              setDrclValidation(data.validation || { valid: true, errors: [] });
              setDrclStatus(res.ok ? 'Completed' : `Error: ${res.status}`);
            } catch (e: any) {
              setDrclStatus(`Error: ${e?.message || 'unknown'}`);
            } finally {
              setDrclRunning(false);
              setInputValue('');
            }
          })();
        }
      };

      const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          sendMessage();
        }
      };

      const getStatusColor = (status: string) => {
        if (status.includes('Connected')) return '#10b981';
        if (status.includes('Error')) return '#ef4444';
        return '#f59e0b';
      };

      const runDrcl = async () => {
        try {
          setDrclRunning(true);
          setDrclStatus('Running DRCL…');
          setShowEnvelope(true);
          const initial_context = {
            goal: inputValue || 'Run DRCL on current interaction',
            constraints: {
              ui_entry: [
                'nextjs-chat/src/components/Chat.tsx'
              ],
              schema_path: 'protocol/drcl_envelope.schema.json',
              workflow_path: 'Happier/workflows/distributed_resonant_corrective_loop.json',
              single_surface: true
            },
            desired_outputs: [
              'RISE mode decision',
              'UI integration plan',
              'assembled DRCL envelope',
              'schema validation result'
            ]
          };
          const res = await fetch('/api/drcl', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ initial_context })
          });
          if (!res.ok) throw new Error(`DRCL request failed: ${res.status}`);
          const data = await res.json();
          console.log('DRCL Response:', data);
          setDrclEnvelope(data.envelope || data);
          setDrclValidation(data.validation || { valid: true, errors: [] });
          setDrclStatus('Completed');
          console.log('Envelope set, showEnvelope should be true');
        } catch (e: any) {
          console.error(e);
          setDrclStatus(`Error: ${e?.message || 'unknown'}`);
        } finally {
          setDrclRunning(false);
        }
      };

      const runDrclViaWs = () => {
        if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;
        wsRef.current.send(JSON.stringify({
          command: 'run_drcl',
          payload: {
            goal: inputValue || 'Run DRCL on current interaction'
          }
        }));
      };

      const renderMessage = (message: EnhancedMessage, index: number) => {
        const isUser = message.sender === 'user';
        const isSystem = message.sender === 'arche' && message.message_type === 'protocol_init';
        
        return (
          <div
            key={`${message.id || 'msg'}-${index}`}
            className={`message ${isUser ? 'user' : isSystem ? 'system' : 'assistant'}`}
          >
            <div className="message-header">
              <span className="sender">
                {isUser ? '🧑 User' : isSystem ? '⚙️ System' : '🤖 ArchE'}
              </span>
              <span className="timestamp">
                {new Date(message.timestamp).toLocaleTimeString()}
              </span>
              {message.protocol_version && (
                <span className="protocol-badge">
                  {message.protocol_version}
                </span>
              )}
            </div>
            
            <div className="message-content">
              {typeof message.content === 'string' ? message.content : JSON.stringify(message.content, null, 2)}
            </div>
            
            {/* Enhanced Protocol Indicators */}
            <div className="protocol-indicators">
              {message.iar && (
                <div className="indicator iar">
                  <span className="label">IAR:</span>
                  <span className={`status ${message.iar.status.toLowerCase()}`}>
                    {message.iar.status}
                  </span>
                  <span className="confidence">
                    {(message.iar.confidence * 100).toFixed(0)}%
                  </span>
                </div>
              )}
              
              {message.spr_activations && message.spr_activations.length > 0 && (
                <div className="indicator sprs">
                  <span className="label">SPRs:</span>
                  <span className="count">{message.spr_activations.length}</span>
                  <span className="spr-list">
                    {message.spr_activations.map(spr => spr.spr_id).join(', ')}
                  </span>
                </div>
              )}
              
              {message.temporal_context && (
                <div className="indicator temporal">
                  <span className="label">⏰ Temporal:</span>
                  <span className="horizon">{message.temporal_context.time_horizon}</span>
                </div>
              )}
              
              {message.meta_cognitive_state && (
                <div className="indicator meta">
                  <span className="label">🧠 Meta:</span>
                  <span className="sirc-phase">{message.meta_cognitive_state.sirc_phase || 'None'}</span>
                </div>
              )}
              
              {message.complex_system_visioning && (
                <div className="indicator complex">
                  <span className="label">🌐 Complex:</span>
                  <span className="scenario">{message.complex_system_visioning.scenario_name}</span>
                </div>
              )}
              
              {message.implementation_resonance && (
                <div className="indicator implementation">
                  <span className="label">🔧 Implementation:</span>
                  <span className="alignment">
                    {(message.implementation_resonance.code_documentation_alignment * 100).toFixed(0)}%
                  </span>
                </div>
              )}
              
              {message.protocol_init && (
                <div className="indicator protocol-init">
                  <span className="label">🧠 Protocol:</span>
                  <span className="status">{message.protocol_init.status}</span>
                </div>
              )}
              
              {message.protocol_error && (
                <div className="indicator protocol-error">
                  <span className="label">⚠️ Error:</span>
                  <span className="error">{message.protocol_error.message}</span>
                </div>
              )}
            </div>
          </div>
        );
      };

      return (
        <div className="chat-container">
          <div className="chat-header">
            <h1 className="text-xl font-bold">
              ArchE - ResonantiA Protocol v3.5-GP
            </h1>
            <div className="header-controls">
              <Link href="/mcp" className="px-3 py-1 bg-gray-700 rounded-md text-sm font-semibold hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-800 focus:ring-white">
                MCP
              </Link>
              <div className="visualization-toggle">
                <button
                  className={activeVisualization === 'protocol-flow' ? 'active' : ''}
                  onClick={() => setActiveVisualization('protocol-flow')}
                >
                  Protocol Flow
                </button>
                <button
                  className={activeVisualization === 'thought-trail' ? 'active' : ''}
                  onClick={() => setActiveVisualization('thought-trail')}
                >
                  Thought Trail
                </button>
              </div>
              <div className="connection-status">
                <div 
                  className="status-indicator"
                  style={{ backgroundColor: getStatusColor(connectionStatus) }}
                />
                <span>{connectionStatus}</span>
              </div>
            </div>
          </div>

          <div className="main-content">
            {/* Chat Messages Panel */}
            <div className="chat-panel">
              <div className="messages-container">
                {messages.map((message, index) => renderMessage(message, index))}
                <div ref={messagesEndRef} />
              </div>

              <div className="input-container">
                <textarea
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder={"Enter your query for ArchE..."}
                  rows={3}
                />
                <button 
                  onClick={sendMessage} 
                  disabled={!inputValue.trim()}
                  className="send-button"
                >
                  Send Query
                </button>
                <button
                  onClick={runDrcl}
                  disabled={drclRunning}
                  className="send-button"
                  style={{ background: 'linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%)' }}
                >
                  {drclRunning ? 'Running DRCL…' : 'Run DRCL'}
                </button>
                <button
                  onClick={runDrclViaWs}
                  disabled={!isConnected}
                  className="send-button"
                  style={{ background: 'linear-gradient(135deg, #f97316 0%, #ea580c 100%)' }}
                >Run DRCL via WS</button>
              </div>
              
              {showEnvelope && (
                <div className="envelope-panel">
                  <div className="envelope-header">
                    <h3>DRCL Envelope (DEBUG: Panel Visible)</h3>
                    <div className="envelope-actions">
                      <span className="status-pill">{drclStatus || 'Idle'}</span>
                      <button onClick={() => setShowEnvelope(false)}>Hide</button>
                    </div>
                  </div>
                  <pre className="envelope-json">{JSON.stringify(drclEnvelope, null, 2)}</pre>
                  {drclValidation && (
                    <div className="validation">
                      <strong>Validation:</strong> {drclValidation.valid ? 'valid' : 'invalid'}
                      {drclValidation.errors && drclValidation.errors.length > 0 && (
                        <ul>
                          {drclValidation.errors.map((e: any, i: number) => (
                            <li key={i}>{typeof e === 'string' ? e : JSON.stringify(e)}</li>
                          ))}
                        </ul>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Visualization Panel */}
            <div className="visualization-panel">
              <h3>
                {activeVisualization === 'protocol-flow' ? 'Protocol Flow Visualization' : 'Thought Trail Visualization'}
              </h3>
              {activeVisualization === 'protocol-flow' ? (
                <ProtocolFlow messages={messages} />
              ) : (
                <ThoughtTrailGraph messages={messages} />
              )}
            </div>
          </div>

          <style jsx>{`
            .chat-container {
              display: flex;
              flex-direction: column;
              height: 100vh;
              background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
              color: white;
              font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }

            .chat-header {
              display: flex;
              justify-content: space-between;
              align-items: center;
              padding: 1rem 2rem;
              background: rgba(0, 0, 0, 0.2);
              border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }

            .chat-header h1 {
              margin: 0;
              font-size: 1.5rem;
              font-weight: 600;
            }

            .header-controls {
              display: flex;
              align-items: center;
              gap: 1rem;
            }

            .visualization-toggle {
              display: flex;
              gap: 0.5rem;
            }

            .visualization-toggle button {
              background: rgba(255, 255, 255, 0.1);
              border: 1px solid rgba(255, 255, 255, 0.2);
              border-radius: 6px;
              padding: 0.5rem 1rem;
              color: white;
              cursor: pointer;
              transition: all 0.2s;
              font-size: 0.9rem;
            }

            .visualization-toggle button.active {
              background: rgba(16, 185, 129, 0.3);
              border-color: #10b981;
            }

            .visualization-toggle button:hover {
              background: rgba(255, 255, 255, 0.2);
            }

            .connection-status {
              display: flex;
              align-items: center;
              gap: 0.5rem;
              font-size: 0.9rem;
            }

            .status-indicator {
              width: 12px;
              height: 12px;
              border-radius: 50%;
              animation: pulse 2s infinite;
            }

            @keyframes pulse {
              0% { opacity: 1; }
              50% { opacity: 0.5; }
              100% { opacity: 1; }
            }

            .main-content {
              display: flex;
              flex: 1;
              overflow: hidden;
            }

            .chat-panel {
              flex: 1;
              display: flex;
              flex-direction: column;
              border-right: 1px solid rgba(255, 255, 255, 0.1);
            }

            .messages-container {
              flex: 1;
              overflow-y: auto;
              padding: 1rem;
              display: flex;
              flex-direction: column;
              gap: 1rem;
            }

            .message {
              background: rgba(255, 255, 255, 0.1);
              border-radius: 8px;
              padding: 1rem;
              backdrop-filter: blur(10px);
            }

            .message.user {
              align-self: flex-end;
              background: rgba(16, 185, 129, 0.2);
              max-width: 70%;
            }

            .message.system {
              background: rgba(59, 130, 246, 0.2);
              border-left: 4px solid #3b82f6;
            }

            .message-header {
              display: flex;
              justify-content: space-between;
              align-items: center;
              margin-bottom: 0.5rem;
              font-size: 0.85rem;
              opacity: 0.8;
            }

            .sender {
              font-weight: 600;
            }

            .protocol-badge {
              background: rgba(139, 92, 246, 0.3);
              padding: 2px 6px;
              border-radius: 4px;
              font-size: 0.75rem;
            }

            .message-content {
              line-height: 1.5;
              margin-bottom: 0.5rem;
            }

            .protocol-indicators {
              display: flex;
              flex-wrap: wrap;
              gap: 0.5rem;
              margin-top: 0.5rem;
            }

            .indicator {
              display: flex;
              align-items: center;
              gap: 0.25rem;
              background: rgba(0, 0, 0, 0.2);
              padding: 0.25rem 0.5rem;
              border-radius: 4px;
              font-size: 0.75rem;
            }

            .indicator.iar .status.success {
              color: #10b981;
            }

            .indicator.iar .status.failure {
              color: #ef4444;
            }

            .indicator.iar .status.partial {
              color: #f59e0b;
            }

            .indicator.sprs {
              background: rgba(139, 92, 246, 0.2);
            }

            .indicator.temporal {
              background: rgba(59, 130, 246, 0.2);
            }

            .indicator.meta {
              background: rgba(168, 85, 247, 0.2);
            }

            .indicator.complex {
              background: rgba(236, 72, 153, 0.2);
            }

            .indicator.implementation {
              background: rgba(245, 158, 11, 0.2);
            }

            .indicator.protocol-init {
              background: rgba(16, 185, 129, 0.2);
            }

            .indicator.protocol-error {
              background: rgba(239, 68, 68, 0.2);
            }

            .input-container {
              padding: 1rem;
              background: rgba(0, 0, 0, 0.2);
              display: flex;
              gap: 1rem;
              align-items: flex-end;
            }

            .input-container textarea {
              flex: 1;
              background: rgba(255, 255, 255, 0.1);
              border: 1px solid rgba(255, 255, 255, 0.2);
              border-radius: 8px;
              padding: 0.75rem;
              color: white;
              resize: vertical;
              min-height: 60px;
            }

            .input-container textarea::placeholder {
              color: rgba(255, 255, 255, 0.6);
            }

            .send-button {
              background: linear-gradient(135deg, #10b981 0%, #059669 100%);
              border: none;
              border-radius: 8px;
              padding: 0.75rem 1.5rem;
              color: white;
              font-weight: 600;
              cursor: pointer;
              transition: all 0.2s;
            }

            .send-button:hover:not(:disabled) {
              transform: translateY(-1px);
              box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
            }

            .send-button:disabled {
              opacity: 0.5;
              cursor: not-allowed;
            }

            .envelope-panel {
              margin: 0 1rem 1rem 1rem;
              background: rgba(0, 100, 200, 0.9);
              border: 2px solid rgba(255, 255, 255, 0.8);
              border-radius: 8px;
              overflow: hidden;
              box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
            }

            .envelope-header {
              display: flex;
              align-items: center;
              justify-content: space-between;
              padding: 0.75rem 1rem;
              background: rgba(255, 255, 255, 0.08);
            }

            .status-pill {
              background: rgba(16,185,129,0.25);
              padding: 0.25rem 0.5rem;
              border-radius: 999px;
              font-size: 0.8rem;
            }

            .envelope-json {
              margin: 0;
              padding: 1rem;
              max-height: 260px;
              overflow: auto;
              background: rgba(0, 0, 0, 0.2);
              font-size: 0.85rem;
              white-space: pre;
            }
          `}</style>
        </div>
      );
    };

    export default Chat; 