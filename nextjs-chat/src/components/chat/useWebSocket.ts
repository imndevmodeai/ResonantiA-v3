import { useState, useEffect, useCallback } from 'react';
import { addEdge, applyNodeChanges, applyEdgeChanges, Node, Edge, NodeChange, EdgeChange, Connection } from 'reactflow';

interface Message {
  id: string;
  type: 'user' | 'system' | 'cli_output' | 'cli_error' | 'cli_complete' | 'welcome' | 'query_received';
  content: string;
  timestamp: string;
  raw?: any;
}

const useWebSocket = (url: string) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected' | 'error'>('disconnected');
  const [nodes, setNodes] = useState<Node[]>([
    { id: '1', position: { x: 0, y: 0 }, data: { label: 'ArchE' } },
  ]);
  const [edges, setEdges] = useState<Edge[]>([]);

  const onNodesChange = useCallback(
    (changes: NodeChange[]) => setNodes((nds) => applyNodeChanges(changes, nds)),
    [setNodes]
  );
  const onEdgesChange = useCallback(
    (changes: EdgeChange[]) => setEdges((eds) => applyEdgeChanges(changes, eds)),
    [setEdges]
  );
  const onConnect = useCallback(
    (connection: Connection) => setEdges((eds) => addEdge(connection, eds)),
    [setEdges]
  );

  const addMessage = useCallback((message: Message) => {
    setMessages((prevMessages) => [...prevMessages, message]);
  }, []);

  const addNode = useCallback((label: string, type: string = 'thought') => {
    const newNodeId = (nodes.length + 1).toString();
    const newNode: Node = {
      id: newNodeId,
      position: { x: Math.random() * 400, y: Math.random() * 400 },
      data: { label, type },
      style: {
        background: type === 'spr' ? '#ff6b6b' : '#4ecdc4',
        color: 'white',
        border: '2px solid #2c3e50',
        borderRadius: '8px',
        padding: '10px',
        fontSize: '12px',
        maxWidth: '200px',
        wordWrap: 'break-word'
      }
    };
    setNodes((nds) => [...nds, newNode]);
    
    const newEdge: Edge = {
      id: `e1-${newNodeId}`,
      source: '1',
      target: newNodeId,
      animated: type === 'spr',
      style: {
        stroke: type === 'spr' ? '#ff6b6b' : '#4ecdc4',
        strokeWidth: 2
      }
    };
    setEdges((eds) => addEdge(newEdge, eds));
  }, [nodes.length]);

  useEffect(() => {
    const ws = new WebSocket(url);

    ws.onopen = () => {
      console.log('Connected to ArchE WebSocket server');
      setConnectionStatus('connected');
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('Received message:', data);

        switch (data.type) {
          case 'welcome':
            addMessage({
              id: Date.now().toString(),
              type: 'system',
              content: `🎉 ${data.message}`,
              timestamp: data.timestamp
            });
            break;

          case 'query_received':
            addMessage({
              id: Date.now().toString(),
              type: 'system',
              content: `🔍 Processing query: "${data.query}"`,
              timestamp: data.timestamp
            });
            break;

          case 'cli_output':
            const output = data.data as string;
            addMessage({
              id: Date.now().toString(),
              type: 'cli_output',
              content: output,
              timestamp: data.timestamp
            });

            if (output.includes('Thought Trail:') || output.includes('🧠')) {
              const thoughtMatch = output.match(/🧠\s*(.*?)(?:\n|$)/);
              if (thoughtMatch) {
                addNode(thoughtMatch[1], 'thought');
              }
            }

            if (output.includes('SPR Activation:') || output.includes('📖')) {
              const sprMatch = output.match(/📖\s*(.*?)(?:\n|$)/);
              if (sprMatch) {
                addNode(sprMatch[1], 'spr');
              }
            }

            if (output.includes('WORKFLOW') || output.includes('🎯')) {
              const workflowMatch = output.match(/🎯\s*(.*?)(?:\n|$)/);
              if (workflowMatch) {
                addNode(`Workflow: ${workflowMatch[1]}`, 'workflow');
              }
            }

            if (output.includes('EVOLUTION') || output.includes('🧠')) {
              const evolutionMatch = output.match(/🧠\s*(.*?)(?:\n|$)/);
              if (evolutionMatch) {
                addNode(`Evolution: ${evolutionMatch[1]}`, 'evolution');
              }
            }
            break;

          case 'cli_error':
            addMessage({
              id: Date.now().toString(),
              type: 'cli_error',
              content: `❌ Error: ${data.data}`,
              timestamp: data.timestamp
            });
            break;

          case 'cli_complete':
            addMessage({
              id: Date.now().toString(),
              type: 'system',
              content: `✅ Command completed (exit code: ${data.exitCode})`,
              timestamp: data.timestamp
            });
            break;

          case 'pong':
            break;

          default:
            addMessage({
              id: Date.now().toString(),
              type: 'system',
              content: data.data || JSON.stringify(data),
              timestamp: data.timestamp || new Date().toISOString()
            });
            break;
        }
      } catch (error) {
        const plainMessage = event.data as string;
        addMessage({
          id: Date.now().toString(),
          type: 'system',
          content: plainMessage,
          timestamp: new Date().toISOString()
        });
      }
    };

    ws.onclose = () => {
      console.log('Disconnected from ArchE WebSocket server');
      setConnectionStatus('disconnected');
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setConnectionStatus('error');
    };

    setSocket(ws);

    return () => {
      ws.close();
    };
  }, [url, addMessage, addNode]);

  const sendMessage = (message: string) => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      const queryMessage = {
        type: 'query',
        data: message,
        timestamp: new Date().toISOString()
      };
      socket.send(JSON.stringify(queryMessage));
      addMessage({
        id: Date.now().toString(),
        type: 'user',
        content: message,
        timestamp: new Date().toISOString()
      });
    }
  };

  return { 
    messages, 
    sendMessage, 
    nodes, 
    edges, 
    onNodesChange, 
    onEdgesChange, 
    onConnect,
    connectionStatus 
  };
};

export default useWebSocket;
