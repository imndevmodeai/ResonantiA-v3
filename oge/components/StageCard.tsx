
import React from 'react';
import type { StageResult } from '../types';
import { ArrowDownIcon } from './icons';

interface StageCardProps {
    stage: StageResult;
    isFinal?: boolean;
}

const renderContent = (content: string) => {
    return (
        <code className="block w-full text-left text-sm bg-gray-900 text-cyan-300 p-3 rounded-md overflow-x-auto whitespace-pre-wrap break-words">
            {content}
        </code>
    );
};

export const StageCard: React.FC<StageCardProps> = ({ stage, isFinal = false }) => {
    if (isFinal) {
        return (
            <div className="bg-gradient-to-br from-cyan-900/50 to-purple-900/50 rounded-lg p-6 border border-cyan-500 shadow-2xl shadow-cyan-500/10">
                <div className="flex items-center mb-4">
                    <span className="text-3xl font-bold text-cyan-300 mr-4">{stage.symbol}</span>
                    <div>
                        <h3 className="text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-300 to-purple-300">
                            {stage.title}
                        </h3>
                        <p className="text-sm text-gray-400">Final Crystallized Form</p>
                    </div>
                </div>
                 <div className="mt-4">
                    <p className="text-xs text-gray-400 mb-1 uppercase font-semibold">Original Query</p>
                    <p className="text-sm text-gray-300 p-3 bg-gray-900/50 rounded-md border border-gray-700">{stage.input}</p>
                </div>
                <div className="mt-4">
                    <p className="text-xs text-gray-400 mb-1 uppercase font-semibold">Zepto SPR</p>
                    {renderContent(stage.output)}
                </div>
                <div className="mt-6 flex justify-end items-baseline gap-2">
                    <span className="text-gray-400">Total Compression Ratio:</span>
                    <span className="text-2xl font-bold text-cyan-300">{stage.cumulativeCompression.toLocaleString()} : 1</span>
                </div>
            </div>
        );
    }
    
    return (
        <div className="bg-gray-800/60 rounded-lg p-4 border border-gray-700 transition-all duration-300 hover:border-cyan-600 hover:shadow-lg hover:shadow-cyan-900/20">
            <div className="flex justify-between items-start mb-3">
                <div className="flex items-center">
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center mr-3">
                        <span className="font-bold text-cyan-400">{stage.stageNumber}</span>
                    </div>
                    <div>
                        <h3 className="font-bold text-gray-200">{stage.title}</h3>
                        <p className="text-xs text-gray-400">{stage.symbol}</p>
                    </div>
                </div>
                <div className="text-right">
                    <span className="text-xs text-gray-400 block">Compression</span>
                    <span className="font-semibold text-cyan-400">{stage.stageCompression.toLocaleString()}:1</span>
                </div>
            </div>

            <div className="flex flex-col gap-2">
                <div>
                     <p className="text-xs text-gray-500 mb-1 flex items-center"><ArrowDownIcon className="h-3 w-3 mr-1"/>Input</p>
                     <div className="text-xs text-gray-400 bg-gray-900/50 p-2 rounded overflow-x-auto whitespace-nowrap">{stage.input}</div>
                </div>
                <div>
                    <p className="text-xs text-gray-400 mb-1 uppercase font-semibold">Output</p>
                    {renderContent(stage.output)}
                </div>
            </div>
        </div>
    );
};
