
import React, { useState, useCallback } from 'react';
import { StageCard } from './components/StageCard';
import { SymbolCodex } from './components/SymbolCodex';
import { generateObjectivePipeline } from './services/objectiveGenerator';
import type { StageResult } from './types';
import { CodeIcon, FingerprintIcon, ZapIcon } from './components/icons';

const App: React.FC = () => {
    const [query, setQuery] = useState<string>("Who would win in a boxing match between Mike Tyson in his prime (circa 1986-1988, age 20-22) and George Foreman in his prime (circa 1973-1974, age 24-25)?");
    const [pipeline, setPipeline] = useState<StageResult[] | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);

    const handleGenerate = useCallback(() => {
        if (!query.trim()) {
            setError("Query cannot be empty.");
            return;
        }
        setIsLoading(true);
        setError(null);
        setPipeline(null);

        setTimeout(() => {
            try {
                const results = generateObjectivePipeline(query);
                setPipeline(results);
            } catch (e) {
                setError("Failed to generate objective. Please try again.");
                console.error(e);
            } finally {
                setIsLoading(false);
            }
        }, 1200); // Simulate processing time
    }, [query]);

    return (
        <div className="min-h-screen bg-gray-900 text-gray-200 font-sans flex flex-col items-center p-4 sm:p-6 lg:p-8">
            <main className="w-full max-w-7xl mx-auto flex flex-col lg:flex-row gap-8">
                {/* Left Side: Input and Codex */}
                <div className="lg:w-1/3 lg:sticky lg:top-8 self-start flex flex-col gap-8">
                    <header className="w-full text-center lg:text-left">
                         <h1 className="text-3xl sm:text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-cyan-400 mb-2">
                             Objective Generation Engine
                         </h1>
                         <p className="text-gray-400">
                             Visualizing the Pattern Crystallization Meta-Process
                         </p>
                    </header>

                    <div className="bg-gray-800/50 rounded-lg p-6 border border-gray-700 backdrop-blur-sm">
                        <label htmlFor="query-input" className="block text-sm font-medium text-gray-300 mb-2">
                            Enter Raw Query
                        </label>
                        <textarea
                            id="query-input"
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            className="w-full h-40 bg-gray-900 border border-gray-600 rounded-md p-3 text-gray-200 focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500 transition duration-200 resize-none"
                            placeholder="e.g., Analyze the economic impact of AI..."
                        />
                        <button
                            onClick={handleGenerate}
                            disabled={isLoading}
                            className="w-full mt-4 bg-cyan-600 hover:bg-cyan-500 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-bold py-3 px-4 rounded-lg flex items-center justify-center transition-all duration-300 transform hover:scale-105"
                        >
                            {isLoading ? (
                                <>
                                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                    </svg>
                                    Crystallizing...
                                </>
                            ) : (
                                <>
                                    <ZapIcon className="h-5 w-5 mr-2" />
                                    Crystallize Objective
                                </>
                            )}
                        </button>
                        {error && <p className="text-red-400 mt-2 text-sm">{error}</p>}
                    </div>
                    
                    <SymbolCodex />
                </div>

                {/* Right Side: Results */}
                <div className="lg:w-2/3 flex flex-col gap-4">
                    {!pipeline && !isLoading && (
                        <div className="flex flex-col items-center justify-center h-full min-h-[500px] bg-gray-800/30 rounded-lg border-2 border-dashed border-gray-700 p-8 text-center">
                            <FingerprintIcon className="h-16 w-16 text-gray-600 mb-4" />
                            <h2 className="text-xl font-semibold text-gray-400">Awaiting Query Crystallization</h2>
                            <p className="text-gray-500 mt-2">Enter a query and click "Crystallize Objective" to see the 8-stage process.</p>
                        </div>
                    )}
                    {isLoading && (
                         <div className="flex flex-col items-center justify-center h-full min-h-[500px] text-center">
                            <div className="relative">
                                <div className="w-24 h-24 border-4 border-cyan-500 border-dashed rounded-full animate-spin"></div>
                                <CodeIcon className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 h-10 w-10 text-cyan-400"/>
                            </div>
                            <p className="text-lg mt-6 font-semibold text-cyan-300">Applying Pattern Crystallization Meta-Process...</p>
                         </div>
                    )}
                    {pipeline && (
                        <>
                             <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {pipeline.slice(0, 8).map((stage) => (
                                    <StageCard key={stage.stageNumber} stage={stage} />
                                ))}
                            </div>
                            <div className="mt-4">
                                <StageCard stage={pipeline[8]} isFinal={true} />
                            </div>
                        </>
                    )}
                </div>
            </main>
        </div>
    );
};

export default App;
