import { useState, useEffect, useCallback, useRef } from 'react';
import {
  addEdge,
  applyNodeChanges,
  applyEdgeChanges,
  Node,
  Edge,
  Connection,
  NodeChange,
  EdgeChange
} from 'reactflow';
import type { EnhancedMessage } from '../types/protocol';

const useWebSocket = (url: string) => {
  const [messages, setMessages] = useState<EnhancedMessage[]>([]);
  const socket = useRef<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const lastNodeId = useRef<string>('root');

  const [nodes, setNodes] = useState<Node[]>([
    { id: 'root', position: { x: 100, y: 100 }, data: { label: 'ArchE Core' } }
  ]);
  const [edges, setEdges] = useState<Edge[]>([]);

  const onNodesChange = useCallback((changes: NodeChange[]) => {
    setNodes((nds) => applyNodeChanges(changes, nds));
  }, []);

  const onEdgesChange = useCallback((changes: EdgeChange[]) => {
    setEdges((eds) => applyEdgeChanges(changes, eds));
  }, []);

  const onConnect = useCallback((connection: Connection) => {
    setEdges((eds) => addEdge(connection, eds));
  }, []);

  // Reusable node/edge creation function
  const addNode = useCallback((id: string, label: string, parentId: string) => {
    const parentNode = nodes.find((n) => n.id === parentId) || nodes[0];
    const xOffset = Math.random() * 300 - 150;
    const yOffset = 100 + Math.random() * 50;

    const position = {
      x: parentNode.position.x + xOffset,
      y: parentNode.position.y + yOffset
    };

    const newNode: Node = {
      id,
      position,
      data: { label },
    };

    const newEdge: Edge = {
      id: `edge-${parentId}-${id}`,
      source: parentId,
      target: id,
    };

    setNodes((prev) => [...prev, newNode]);
    setEdges((prev) => [...prev, newEdge]);
  }, [nodes]);

  useEffect(() => {
    const ws = new WebSocket(url);
    socket.current = ws;

    ws.onopen = () => {
      console.log('✅ WebSocket connection established');
      setIsConnected(true);
      const systemMessage: EnhancedMessage = {
        id: `system_${Date.now()}`,
        content: 'Connection to ArchE Cognitive Bus established.',
        sender: 'arche',
        message_type: 'protocol_init',
        timestamp: new Date().toISOString(),
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
        protocol_error: undefined,
      };
      setMessages((prev) => [...prev, systemMessage]);
    };

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data) as Partial<EnhancedMessage>;
        // Coerce minimal shape
        const coerced: EnhancedMessage = {
          id: (message.id as string) || `msg_${Date.now()}`,
          content: (message.content as string) || String(event.data),
          timestamp: (message.timestamp as string) || new Date().toISOString(),
          sender: message.sender === 'user' ? 'user' : 'arche',
          message_type: message.message_type || 'chat',
          protocol_compliance: Boolean(message.protocol_compliance),
          iar: message.iar,
          spr_activations: message.spr_activations,
          temporal_context: message.temporal_context,
          meta_cognitive_state: message.meta_cognitive_state,
          complex_system_visioning: message.complex_system_visioning,
          implementation_resonance: message.implementation_resonance,
          thought_trail: message.thought_trail,
          protocol_version: message.protocol_version,
          protocol_init: message.protocol_init,
          protocol_error: message.protocol_error,
        };
        setMessages((prev) => [...prev, coerced]);

        // Update reactflow nodes based on message type
        if (coerced.message_type === 'spr') {
          const nodeId = `spr-${coerced.id}-${Date.now()}`;
          addNode(nodeId, `SPR: ${coerced.content}`, lastNodeId.current);
        }
      } catch (error) {
        console.error('Failed to parse WebSocket message:', event.data, error);
        setMessages((prev) => [
          ...prev,
          {
            id: `error_${Date.now()}`,
            content: `Failed to parse message: ${event.data}`,
            sender: 'arche',
            message_type: 'error',
            timestamp: new Date().toISOString(),
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
            protocol_error: { message: 'parse_error', error: 'json_parse_failed', fallback_mode: true },
          }
        ]);
      }
    };

    ws.onclose = () => {
      console.log('WebSocket connection closed');
      setIsConnected(false);
      setMessages((prev) => [
        ...prev,
        {
          id: `system_${Date.now()}`,
          content: 'Connection to ArchE Cognitive Bus lost.',
          sender: 'arche',
          message_type: 'protocol_init',
          timestamp: new Date().toISOString(),
          protocol_compliance: true,
          iar: undefined,
          spr_activations: undefined,
          temporal_context: undefined,
          meta_cognitive_state: undefined,
          complex_system_visioning: undefined,
          implementation_resonance: undefined,
          thought_trail: undefined,
          protocol_version: undefined,
          protocol_init: { message: 'connection_lost', capabilities: [], status: 'disconnected' },
          protocol_error: undefined,
        }
      ]);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setMessages((prev) => [
        ...prev,
        {
          id: `error_${Date.now()}`,
          content: 'A WebSocket error occurred.',
          sender: 'arche',
          message_type: 'error',
          timestamp: new Date().toISOString(),
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
          protocol_error: { message: 'ws_error', error: 'socket_error', fallback_mode: true },
        }
      ]);
    };

    return () => {
      ws.close();
    };
  }, [url, addNode]);

  const sendMessage = (message: string) => {
    if (socket.current && socket.current.readyState === WebSocket.OPEN) {
      const userMessage: EnhancedMessage = {
        id: `user_${Date.now()}`,
        content: message,
        sender: 'user',
        message_type: 'chat',
        timestamp: new Date().toISOString(),
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
        protocol_error: undefined,
      };
      setMessages((prev) => [...prev, userMessage]);

      const nodeId = `user-${Date.now()}`;
      addNode(nodeId, `USER: ${message.substring(0, 50)}...`, 'root');

      socket.current.send(JSON.stringify({ type: 'query', payload: message }));
    } else {
      console.error('WebSocket is not connected.');
      setMessages((prev) => [
        ...prev,
        {
          id: `error_${Date.now()}`,
          content: 'Cannot send message: WebSocket is not connected.',
          sender: 'arche',
          message_type: 'error',
          timestamp: new Date().toISOString(),
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
          protocol_error: { message: 'send_failed', error: 'not_connected', fallback_mode: true },
        }
      ]);
    }
  };

  return {
    messages,
    isConnected,
    sendMessage,
    nodes,
    edges,
    onNodesChange,
    onEdgesChange,
    onConnect
  };
};

export default useWebSocket;

