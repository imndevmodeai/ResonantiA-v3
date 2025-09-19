import React from 'react';
import { VCDRichEvent } from '../types';
import { EventCard } from './EventCard';

interface CognitiveStreamProps {
  events: VCDRichEvent[];
}

export const CognitiveStream: React.FC<CognitiveStreamProps> = ({ events }) => {
  return (
    <div className="space-y-4">
      {events.map((event) => (
        <EventCard key={event.event_id} event={event} />
      ))}
    </div>
  );
};




