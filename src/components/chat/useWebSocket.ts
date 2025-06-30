import { useState, useEffect, useCallback } from 'react';
import { addEdge, applyNodeChanges, applyEdgeChanges } from 'reactflow';

const useWebSocket = (url) => {
  const [messages, setMessages] = useState([]);
  const [socket, setSocket] = useState(null);
  const [nodes, setNodes] = useState([
    { id: '1', position: { x: 0, y: 0 }, data: { label: 'ArchE' } },
  ]);
  const [edges, setEdges] = useState([]);

  const onNodesChange = useCallback(
    (changes) => setNodes((nds) => applyNodeChanges(changes, nds)),
    [setNodes]
  );
  const onEdgesChange = useCallback(
    (changes) => setEdges((eds) => applyEdgeChanges(changes, eds)),
    [setEdges]
  );
  const onConnect = useCallback(
    (connection) => setEdges((eds) => addEdge(connection, eds)),
    [setEdges]
  );

  useEffect(() => {
    const ws = new WebSocket(url);

    ws.onopen = () => {
      console.log('connected');
    };

    ws.onmessage = (event) => {
      const message = event.data;
      setMessages((prevMessages) => [...prevMessages, message]);

      // Simple parsing logic for thought trails and SPR activations
      if (message.includes('Thought Trail:')) {
        const newNodeId = (nodes.length + 1).toString();
        const newNode = {
          id: newNodeId,
          position: { x: Math.random() * 400, y: Math.random() * 400 },
          data: { label: message },
        };
        setNodes((nds) => [...nds, newNode]);
        setEdges((eds) => addEdge({ id: `e1-${newNodeId}`, source: '1', target: newNodeId }, eds));
      } else if (message.includes('SPR Activation:')) {
        const newNodeId = (nodes.length + 1).toString();
        const newNode = {
          id: newNodeId,
          position: { x: Math.random() * 400, y: Math.random() * 400 },
          data: { label: message },
        };
        setNodes((nds) => [...nds, newNode]);
        setEdges((eds) => addEdge({ id: `e1-${newNodeId}`, source: '1', target: newNodeId, animated: true }, eds));
      }
    };

    ws.onclose = () => {
      console.log('disconnected');
    };

    setSocket(ws);

    return () => {
      ws.close();
    };
  }, [url, nodes]);

  const sendMessage = (message) => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(message);
    }
  };

  return { messages, sendMessage, nodes, edges, onNodesChange, onEdgesChange, onConnect };
};

export default useWebSocket;
