
import React from 'react';
import { Phase } from '../types';
import { PhaseCard } from './PhaseCard';

interface ProjectPlanProps {
  phases: Phase[];
}

export const ProjectPlan: React.FC<ProjectPlanProps> = ({ phases }) => {
  return (
    <div className="space-y-4">
      {phases.map((phase, index) => (
        <PhaseCard key={phase.id} phase={phase} initialOpen={index === 0} />
      ))}
    </div>
  );
};
