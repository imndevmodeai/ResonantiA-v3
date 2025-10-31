'use client';

import React from 'react';

const phases = [
  'IAR',
  'SPR',
  'Temporal',
  'Meta',
  'Complex',
  'CRDSP',
];

export function ProtocolFlow() {
  const activePhase = 'IAR'; // This will come from the store later

  return (
    <div className="p-4 rounded-lg bg-gray-100 dark:bg-zinc-800 shadow-inner">
      <h2 className="text-lg font-semibold mb-2">Protocol Flow</h2>
      <div className="flex items-center space-x-2">
        {phases.map((phase, index) => (
          <React.Fragment key={phase}>
            <div
              className={`px-3 py-1 rounded-full text-sm font-medium ${
                phase === activePhase
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-200 dark:bg-zinc-700'
              }`}
            >
              {phase}
            </div>
            {index < phases.length - 1 && (
              <div className="flex-1 h-px bg-gray-300 dark:bg-zinc-600"></div>
            )}
          </React.Fragment>
        ))}
      </div>
    </div>
  );
}
