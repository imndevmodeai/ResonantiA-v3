
import React from 'react';
import { Phase } from '../types';

interface GanttChartProps {
  phases: Phase[];
}

const GANTT_CHART_COLORS = [
    'bg-teal-600',
    'bg-sky-600',
    'bg-indigo-600',
    'bg-purple-600',
    'bg-pink-600',
];

export const GanttChart: React.FC<GanttChartProps> = ({ phases }) => {
    const totalDuration = phases.reduce((max, p) => Math.max(max, p.startWeek + p.duration -1), 0) + 2;

    return (
        <div className="mb-12 p-4 md:p-6 bg-gray-800/50 border border-gray-700/50 rounded-lg shadow-lg backdrop-blur-sm">
            <h2 className="text-2xl font-bold text-white mb-6 text-center">Project Timeline</h2>
            <div className="overflow-x-auto">
                <div className="min-w-[800px]">
                    {/* Header */}
                    <div className="grid text-center text-sm font-semibold text-gray-400 pb-2" style={{ gridTemplateColumns: `150px repeat(${totalDuration}, 1fr)`}}>
                        <div className="sticky left-0 bg-gray-800/50 z-10"></div>
                        {Array.from({ length: totalDuration }, (_, i) => (
                            <div key={i}>W{i + 1}</div>
                        ))}
                    </div>

                    {/* Body */}
                    <div className="space-y-2">
                        {phases.map((phase, index) => (
                            <div key={phase.id} className="grid items-center h-12" style={{ gridTemplateColumns: `150px repeat(${totalDuration}, 1fr)`}}>
                                <div className="text-sm font-medium text-gray-300 truncate pr-2 sticky left-0 bg-gray-800/50 z-10 h-full flex items-center">{phase.title.split(':')[0]}</div>
                                <div 
                                    className={`h-8 rounded-md ${GANTT_CHART_COLORS[index % GANTT_CHART_COLORS.length]} flex items-center justify-center text-white text-xs font-bold relative`}
                                    style={{ 
                                        gridColumnStart: phase.startWeek + 1,
                                        gridColumnEnd: phase.startWeek + phase.duration + 1,
                                    }}
                                >
                                    <span className="z-10">{phase.duration}w</span>
                                    {phase.isOngoing && (
                                        <div className="absolute right-0 top-0 bottom-0 w-8 bg-gradient-to-l from-transparent to-current rounded-r-md"></div>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}
