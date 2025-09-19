import React from 'react';
import { VCDRichEvent } from '../../types';

interface SystemMessageEventProps {
  event: VCDRichEvent;
}

export const SystemMessageEvent: React.FC<SystemMessageEventProps> = ({ event }) => {
  return (
    <div className="p-2 text-center text-xs text-gray-500 italic">
      <p>{event.description}</p>
    </div>
  );
};




