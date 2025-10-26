'use client';

import React from 'react';
import { MessageList } from './MessageList';
import { ChatInput } from './ChatInput';
import { useStore } from '../store';
import { ProtocolFlow } from './ProtocolFlow';
import { ThoughtTrailGraph } from './ThoughtTrailGraph';
import { Canvas } from './Canvas';

function ChatComponent() {
  const isConnected = useStore((state) => state.isConnected);
  const error = useStore((state) => state.error);

  return (
    <>
      <div className="flex w-full h-screen p-4 space-x-4 bg-gray-50 dark:bg-black">
        {/* Main Chat Panel */}
        <div className="flex flex-col w-2/3 bg-white dark:bg-zinc-900 rounded-xl shadow-lg">
          <div className="p-2 border-b border-gray-200 dark:border-zinc-700 flex justify-between items-center">
            <h1 className="text-lg font-semibold">ArchE VCD</h1>
            <div className="flex items-center space-x-2">
              <span className={`h-3 w-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></span>
              <span>{isConnected ? 'Connected' : 'Disconnected'}</span>
            </div>
          </div>

          <div className="p-4">
            <ProtocolFlow />
          </div>

          {error && <div className="p-4 text-red-500 bg-red-100 dark:bg-red-900/20">{error}</div>}

          <div className="flex-1 p-4 overflow-y-auto">
            <MessageList />
          </div>
          <div className="p-4 border-t border-gray-200 dark:border-zinc-700">
            <ChatInput />
          </div>
        </div>

        {/* Side Panel */}
        <div className="flex flex-col w-1/3 space-y-4">
          <div className="h-1/2">
            <Canvas />
          </div>
          <div className="h-1/2">
            <ThoughtTrailGraph />
          </div>
        </div>
      </div>
    </>
  );
}

export function Chat() {
  return <ChatComponent />;
}
