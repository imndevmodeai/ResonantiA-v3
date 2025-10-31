
import React, { useState } from 'react';
import { Phase } from '../types';
import { SectionComponent } from './Section';
import { ChevronDownIcon } from './icons';

interface PhaseCardProps {
  phase: Phase;
  initialOpen?: boolean;
}

export const PhaseCard: React.FC<PhaseCardProps> = ({ phase, initialOpen = false }) => {
  const [isOpen, setIsOpen] = useState(initialOpen);

  return (
    <div className="border border-gray-700/50 bg-gray-800/50 rounded-lg shadow-lg backdrop-blur-sm overflow-hidden transition-all duration-300">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full p-4 text-left flex justify-between items-center bg-gray-800 hover:bg-gray-700/80 focus:outline-none focus:ring-2 focus:ring-cyan-500"
      >
        <div className="flex items-center">
            <span className="text-xl font-bold text-cyan-400 mr-4">
                {phase.id}
            </span>
            <h2 className="text-lg font-semibold text-white">{phase.title}</h2>
        </div>
        <div className="flex items-center">
            <span className="text-sm text-gray-400 mr-4 hidden sm:block">{phase.duration} Weeks {phase.isOngoing && '(Ongoing)'}</span>
            <ChevronDownIcon
            className={`w-6 h-6 text-gray-400 transform transition-transform duration-300 ${
                isOpen ? 'rotate-180' : ''
            }`}
            />
        </div>
      </button>
      <div
        className={`transition-all duration-500 ease-in-out ${
          isOpen ? 'max-h-[2000px] opacity-100' : 'max-h-0 opacity-0'
        } overflow-hidden`}
      >
        <div className="p-6 border-t border-gray-700/50 space-y-6">
          {phase.sections.map((section) => (
            <SectionComponent key={section.title} title={section.title} items={section.items} />
          ))}
        </div>
      </div>
    </div>
  );
};
