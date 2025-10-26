'use client';
import React from 'react';
import { LogEntry } from './useWebSocket';

interface ThoughtTrailListProps {
  logEntries: LogEntry[];
}

const ThoughtTrailList: React.FC<ThoughtTrailListProps> = ({ logEntries }) => {
  return (
    <div className="p-4 space-y-2">
      {logEntries.length === 0 ? (
        <p className="text-sm text-gray-500">No thought trail events yet.</p>
      ) : (
        logEntries.map((entry) => (
          <div key={entry.id} className="p-2 bg-gray-100 dark:bg-zinc-800 rounded-md text-xs">
            <p className="font-mono text-gray-500 dark:text-gray-400">{entry.timestamp}</p>
            <p className="font-semibold text-gray-700 dark:text-gray-300">{entry.content}</p>
          </div>
        ))
      )}
    </div>
  );
};

export default ThoughtTrailList;
