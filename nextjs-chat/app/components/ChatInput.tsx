'use client';

import { useStore } from '@/app/store';
import React, { useState } from 'react';

export function ChatInput() {
  const [input, setInput] = useState('');
  const sendMessage = useStore((state) => state.sendMessage);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    sendMessage({
      content: input,
      sender: 'user' as const,
      message_type: 'chat' as const,
    });
    
    setInput('');
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Enter a command... (e.g., /phoenix start)"
        className="w-full p-2 border rounded-md dark:bg-zinc-800 dark:border-zinc-700"
      />
    </form>
  );
}
