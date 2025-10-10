import { useState, useEffect, useCallback } from 'react';
import { addEdge, applyNodeChanges, applyEdgeChanges, Node, Edge, NodeChange, EdgeChange, Connection } from 'reactflow';

export interface Message {
  id: string;
  type: 'user' | 'arche' | 'system';
  sender: string;
  content: string;
  timestamp: string;
}

export interface LogEntry {
  id: string;
  timestamp: string;
  content: string;
}

const useWebSocket = (url: string) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [logEntries, setLogEntries] = useState<LogEntry[]>([]);
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected' | 'error'>('disconnected');
  const [nodes, setNodes] = useState<Node[]>([
    { id: '1', type: 'input', position: { x: 100, y: 100 }, data: { label: 'ArchE Core' } },
  ]);
  const [edges, setEdges] = useState<Edge[]>([]);

  const onNodesChange = useCallback(
    (changes: NodeChange[]) => setNodes((nds) => applyNodeChanges(changes, nds)),
    []
  );
  const onEdgesChange = useCallback(
    (changes: EdgeChange[]) => setEdges((eds) => applyEdgeChanges(changes, eds)),
    []
  );
  const onConnect = useCallback(
    (connection: Connection) => setEdges((eds) => addEdge(connection, eds)),
    []
  );

  const addMessage = useCallback((message: Message) => {
    setMessages((prevMessages) => [...prevMessages, message]);
  }, []);

  const addLogEntry = useCallback((entry: LogEntry) => {
    setLogEntries((prevEntries) => [...prevEntries, entry]);
  }, []);
  
  const addNode = useCallback((id: string, label: string, parentId: string) => {
    const newNode: Node = {
      id,
      type: 'default',
      position: { x: Math.random() * 400 + 100, y: Math.random() * 400 + 100 },
      data: { label },
    };
    setNodes((nds) => [...nds, newNode]);

    const newEdge: Edge = {
      id: `e-${parentId}-${id}`,
      source: parentId,
      target: id,
      animated: true,
      style: { stroke: '#60a5fa' },
    };
    setEdges((eds) => addEdge(newEdge, eds));
  }, []);

  useEffect(() => {
    if (!url) return;
    const ws = new WebSocket(url);

    ws.onopen = () => {
      console.log('Connected to ArchE WebSocket server');
      setConnectionStatus('connected');
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type !== 'nexus_event') return;

        const topic = data.event.topic;
        const eventData = data.event.data;

        const chatMessage: Message = {
            id: eventData.timestamp + Math.random(),
            type: 'arche',
            sender: eventData.sender,
            content: eventData.content,
            timestamp: eventData.timestamp,
        };
        addMessage(chatMessage);
        
        if (topic === 'thoughttrail_entry') {
          const { task_id, action_type, timestamp } = eventData;
          const logEntry: LogEntry = {
            id: task_id,
            timestamp: timestamp,
            content: `Action: ${action_type}`,
          };
          addLogEntry(logEntry);
          addNode(task_id, action_type, '1'); // Correctly connect to the root node '1'
        }
      } catch (error) {
        console.error("Failed to process WebSocket message:", error);
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
  }, [url, addMessage, addLogEntry, addNode]);

  const sendMessage = (message: string) => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      const formattedMessage = {
          content: message,
          timestamp: new Date().toISOString()
      };
      socket.send(JSON.stringify(formattedMessage));
      addMessage({
        id: new Date().toISOString(),
        type: 'user',
        sender: 'user',
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
    connectionStatus,
    logEntries
  };
};

export default useWebSocket;
