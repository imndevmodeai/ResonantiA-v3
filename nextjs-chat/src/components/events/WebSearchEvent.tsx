import React from 'react';
import { VCDRichEvent } from '../../types';

interface WebSearchEventProps {
  event: VCDRichEvent;
}

export const WebSearchEvent: React.FC<WebSearchEventProps> = ({ event }) => {
  return (
    <div className="space-y-3">
      <p className="text-sm">{event.description}</p>
      {event.links && event.links.length > 0 && (
        <div className="space-y-2">
          {event.links.map((link, index) => (
            <a 
              key={index} 
              href={link.url} 
              target="_blank" 
              rel="noopener noreferrer" 
              className="block p-2 bg-gray-700 hover:bg-gray-600 rounded-md transition-colors"
            >
              <p className="font-semibold text-cyan-400">{link.title}</p>
              <p className="text-xs text-gray-400">{link.url}</p>
              <p className="text-sm text-gray-300 mt-1">{link.description}</p>
            </a>
          ))}
        </div>
      )}
    </div>
  );
};




