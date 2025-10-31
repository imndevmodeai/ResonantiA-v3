import React from 'react';
import ReactMarkdown from 'react-markdown';
import { VCDRichEvent } from '../../types';

interface ThoughtProcessEventProps {
  event: VCDRichEvent;
}

export const ThoughtProcessEvent: React.FC<ThoughtProcessEventProps> = ({ event }) => {
  return (
    <div className="prose prose-invert prose-sm max-w-none">
      <ReactMarkdown>{event.description}</ReactMarkdown>
    </div>
  );
};




