'use client';
import React, { useRef, useState } from 'react';
import MessageList from './MessageList';
import ChatInput from './ChatInput';
import useWebSocket from './useWebSocket';
import Canvas from '../canvas/Canvas';

const Chat = () => {
  const { 
    messages, 
    sendMessage, 
    nodes, 
    edges, 
    onNodesChange, 
    onEdgesChange, 
    onConnect,
    connectionStatus 
  } = useWebSocket('ws://localhost:3006');
  
  const inputRef = useRef<HTMLTextAreaElement | null>(null);
  const [isCanvasVisible, setIsCanvasVisible] = useState(false);

  const handleSendMessage = (message: string) => {
    sendMessage(message);
    if (inputRef.current) {
      inputRef.current.focus();
    }
  };

  const toggleCanvas = () => {
    setIsCanvasVisible(!isCanvasVisible);
  };

  const getConnectionStatusColor = () => {
    switch (connectionStatus) {
      case 'connected':
        return 'text-green-600 bg-green-100';
      case 'disconnected':
        return 'text-red-600 bg-red-100';
      case 'error':
        return 'text-orange-600 bg-orange-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getConnectionStatusIcon = () => {
    switch (connectionStatus) {
      case 'connected':
        return '🟢';
      case 'disconnected':
        return '🔴';
      case 'error':
        return '🟡';
      default:
        return '⚪';
    }
  };

  return (
    <div className="flex h-screen">
      <div className={`flex flex-col ${isCanvasVisible ? 'w-1/2' : 'w-full'}`}>
        <div className="flex items-center justify-between p-4 border-b bg-white shadow-sm">
          <div className="flex items-center space-x-3">
            <h1 className="text-xl font-bold text-gray-800">ArchE Chat</h1>
            <div className={`px-2 py-1 rounded-full text-xs font-medium ${getConnectionStatusColor()}`}>
              <span className="mr-1">{getConnectionStatusIcon()}</span>
              {connectionStatus}
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <div className="text-sm text-gray-500">
              {nodes.length} nodes, {edges.length} connections
            </div>
            <button
              className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
              onClick={toggleCanvas}
            >
              {isCanvasVisible ? 'Hide' : 'Show'} Canvas
            </button>
          </div>
        </div>
        <MessageList messages={messages} />
        <ChatInput onSendMessage={handleSendMessage} ref={inputRef} />
      </div>
      {isCanvasVisible && (
        <div className="w-1/2 border-l bg-gray-50">
          <div className="p-2 bg-white border-b">
            <h3 className="text-sm font-medium text-gray-700">Interactive Thought Graph</h3>
            <p className="text-xs text-gray-500">Drag nodes, zoom, and explore ArchE's cognitive processes</p>
          </div>
          <Canvas
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
          />
        </div>
      )}
    </div>
  );
};

export default Chat;
