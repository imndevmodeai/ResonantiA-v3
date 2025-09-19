import React from 'react';
import { VCDRichEvent } from '../../types';

interface PhaseEventProps {
  event: VCDRichEvent;
}

export const PhaseEvent: React.FC<PhaseEventProps> = ({ event }) => {
  const isStart = event.event_type === 'phase_start';
  const borderColor = isStart ? 'border-green-500' : 'border-blue-500';
  
  return (
    <div className={`p-3 border-l-4 ${borderColor} bg-gray-700/50`}>
      <p className="font-semibold">{event.title}</p>
      <p className="text-sm">{event.description}</p>
    </div>
  );
};




