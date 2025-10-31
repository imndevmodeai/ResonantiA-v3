
import React from 'react';
import { BulletIcon } from './icons';

interface SectionProps {
  title: string;
  items: string[];
}

export const SectionComponent: React.FC<SectionProps> = ({ title, items }) => {
  return (
    <div>
      <h3 className="text-md font-semibold text-cyan-300 mb-3 border-b-2 border-gray-700 pb-1">{title}</h3>
      <ul className="space-y-2">
        {items.map((item, index) => (
          <li key={index} className="flex items-start">
            <span className="text-cyan-400 mr-3 mt-1 flex-shrink-0">
                <BulletIcon className="w-4 h-4" />
            </span>
            <span className="text-gray-300">{item}</span>
          </li>
        ))}
      </ul>
    </div>
  );
};
