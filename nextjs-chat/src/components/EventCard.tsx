import React from 'react';
import { VCDRichEvent } from '../types';
import { CodeExecutionEvent } from './events/CodeExecutionEvent';
import { WebSearchEvent } from './events/WebSearchEvent';
import { ThoughtProcessEvent } from './events/ThoughtProcessEvent';
import { PhaseEvent } from './events/PhaseEvent';
import { SystemMessageEvent } from './events/SystemMessageEvent';

interface EventCardProps {
  event: VCDRichEvent;
}

const renderEventContent = (event: VCDRichEvent) => {
  switch (event.event_type) {
    case 'code_execution':
      return <CodeExecutionEvent event={event} />;
    case 'web_search':
      return <WebSearchEvent event={event} />;
    case 'thought_process':
      return <ThoughtProcessEvent event={event} />;
    case 'phase_start':
    case 'phase_complete':
      return <PhaseEvent event={event} />;
    case 'system_message':
      return <SystemMessageEvent event={event} />;
    default:
      return (
        <div>
          <h4 className="font-bold">{event.title}</h4>
          <p className="text-sm">{event.description}</p>
        </div>
      );
  }
};

export const EventCard: React.FC<EventCardProps> = ({ event }) => {
  return (
    <div className="bg-gray-800 border border-gray-700 rounded-lg p-4 shadow-md animate-fade-in-up">
      <div className="flex justify-between items-start mb-2">
        <div>
          <span className="text-xs font-semibold uppercase text-cyan-400">{event.phase}</span>
          <h3 className="text-lg font-bold text-gray-100">{event.title}</h3>
        </div>
        <span className="text-xs text-gray-500">{new Date(event.timestamp).toLocaleTimeString()}</span>
      </div>
      <div className="text-gray-300">
        {renderEventContent(event)}
      </div>
      {event.tags && (
        <div className="mt-3 flex flex-wrap gap-2">
          {event.tags.map(tag => (
            <span key={tag} className="px-2 py-1 bg-gray-700 text-xs text-gray-400 rounded-full">
              {tag}
            </span>
          ))}
        </div>
      )}
    </div>
  );
};




