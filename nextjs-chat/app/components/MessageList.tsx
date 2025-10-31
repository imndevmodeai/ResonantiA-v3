'use client';

import { useStore } from '@/app/store';
import React from 'react';

export function MessageList() {
  const messages = useStore((state) => state.messages);

  return (
    <div className="space-y-4">
      {messages.map((msg) => (
        <div
          key={msg.id}
          className={`flex ${
            msg.sender === 'user' ? 'justify-end' : 'justify-start'
          }`}
        >
          <div
            className={`p-3 rounded-lg max-w-lg ${
              msg.sender === 'user'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-200 text-black dark:bg-zinc-700 dark:text-white'
            }`}
          >
            <p className="font-bold">{msg.sender}</p>
            <p>{msg.content}</p>
            <div className="text-xs text-right mt-1 opacity-75">
              {new Date(msg.timestamp).toLocaleTimeString()}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
