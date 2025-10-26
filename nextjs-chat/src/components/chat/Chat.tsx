'use client';
import React, { useState } from 'react';
import MessageList from './MessageList';
import ChatInput from './ChatInput';
import useWebSocket, { LogEntry } from './useWebSocket'; // Import LogEntry type
import Canvas from '../canvas/Canvas';
import ThoughtTrailList from './ThoughtTrailList'; // Import the new component

const Chat = () => {
  const { 
    messages, 
    sendMessage, 
    nodes, 
    edges, 
    onNodesChange, 
    onEdgesChange, 
    onConnect,
    connectionStatus,
    logEntries // Get logEntries from the hook
  } = useWebSocket('ws://localhost:8765');
  
  const [isCanvasVisible, setIsCanvasVisible] = useState(true); // Default to visible

  const handleSendMessage = (message: string) => {
    sendMessage(message);
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
    <div className="flex h-screen bg-gray-100 dark:bg-zinc-900 text-gray-800 dark:text-gray-200">
      {/* Left Panel: Chat and Thought Trail */}
      <div className="flex flex-col w-1/3 border-r border-gray-200 dark:border-zinc-700">
        <div className="p-4 border-b border-gray-200 dark:border-zinc-700">
          <h2 className="text-lg font-semibold">Thought Trail</h2>
          <p className="text-xs text-gray-500">Real-time event stream</p>
        </div>
        <div className="flex-grow overflow-y-auto">
          <ThoughtTrailList logEntries={logEntries} />
        </div>
        <div className="p-4 border-t border-gray-200 dark:border-zinc-700">
            <h2 className="text-lg font-semibold mb-2">Live Chat</h2>
            <div className="h-48 overflow-y-auto bg-white dark:bg-zinc-800 rounded-lg p-2">
                 <MessageList messages={messages} />
            </div>
            <ChatInput onSendMessage={handleSendMessage} />
        </div>
      </div>

      {/* Right Panel: Canvas */}
      <div className="flex flex-col flex-grow">
         <div className="flex items-center justify-between p-4 border-b bg-white dark:bg-zinc-800 shadow-sm">
          <div className="flex items-center space-x-3">
            <h1 className="text-xl font-bold">ArchE Visual Cognitive Debugger</h1>
            <div className={`px-2 py-1 rounded-full text-xs font-medium ${getConnectionStatusColor()}`}>
              <span className="mr-1">{getConnectionStatusIcon()}</span>
              {connectionStatus}
            </div>
          </div>
          <div className="text-sm text-gray-500">
              {nodes.length} nodes, {edges.length} edges
          </div>
        </div>
        <div className="flex-grow bg-gray-50 dark:bg-zinc-900">
            <Canvas
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                onConnect={onConnect}
            />
        </div>
      </div>
    </div>
  );
};

export default Chat;
