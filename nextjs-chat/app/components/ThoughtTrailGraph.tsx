'use client';

import { useStore } from '@/app/store';
import React from 'react';

export function ThoughtTrailGraph() {
  const logEntries = useStore((state) => state.logEntries);

  return (
    <div className="p-4 rounded-lg bg-gray-100 dark:bg-zinc-800 shadow-inner h-full overflow-y-auto">
      <h2 className="text-lg font-semibold mb-2">Thought Trail</h2>
      <div className="space-y-2">
        {logEntries.length === 0 && (
          <p className="text-gray-500">No thought trail events yet.</p>
        )}
        {logEntries.map((entry) => (
          <div key={entry.id} className="text-sm p-2 rounded bg-gray-200 dark:bg-zinc-700">
            <span className="font-mono text-xs opacity-75">{new Date(entry.t).toLocaleTimeString()}</span>
            <span className={`ml-2 font-semibold ${
                entry.severity === 'error' ? 'text-red-500' : 
                entry.severity === 'warn' ? 'text-yellow-500' :
                entry.severity === 'success' ? 'text-green-500' : ''
            }`}>[{entry.severity || 'info'}]</span>
            <div className="ml-2 mt-1">
              <div className="font-medium">{entry.msg}</div>
              {entry.meta && (
                <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                  {entry.meta.action_type && <span>Action: {entry.meta.action_type}</span>}
                  {entry.meta.inputs && <span className="ml-2">Input: {JSON.stringify(entry.meta.inputs)}</span>}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
