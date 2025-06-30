'use client';
import React, { useRef, useState } from 'react';
import MessageList from './MessageList';
import ChatInput from './ChatInput';
import useWebSocket from './useWebSocket';
import Canvas from '../canvas/Canvas';

const Chat = () => {
  const { messages, sendMessage, nodes, edges, onNodesChange, onEdgesChange, onConnect } = useWebSocket('ws://localhost:3001');
  const inputRef = useRef(null);
  const [isCanvasVisible, setIsCanvasVisible] = useState(false);

  const handleSendMessage = (message) => {
    sendMessage(message);
    if (inputRef.current) {
      inputRef.current.focus();
    }
  };

  const toggleCanvas = () => {
    setIsCanvasVisible(!isCanvasVisible);
  };

  return (
    <div className="flex h-screen">
      <div className={`flex flex-col ${isCanvasVisible ? 'w-1/2' : 'w-full'}`}>
        <div className="flex items-center justify-between p-4 border-b">
          <h1 className="text-xl font-bold">ArchE Chat</h1>
          <button
            className="px-4 py-2 bg-gray-200 rounded-lg"
            onClick={toggleCanvas}
          >
            {isCanvasVisible ? 'Hide' : 'Show'} Canvas
          </button>
        </div>
        <MessageList messages={messages} />
        <ChatInput onSendMessage={handleSendMessage} ref={inputRef} />
      </div>
      {isCanvasVisible && (
        <div className="w-1/2 border-l">
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
