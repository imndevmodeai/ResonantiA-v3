
import React from 'react';

const codex = {
  "objective_generation_codex": {
    "⟦ ⟧": "Query Intake / Final Assembly",
    "⦅ ⦆": "Feature Extraction / Vector",
    "⊢": "SPR Activation",
    "⊨": "Mandate Selection / Domain Customization",
    "⊧": "Template Assembly",
    "◊": "Zepto Objective (Final Form)",
    "Δ": "Temporal Scope",
    "Ω": "Cognitive Resonance (Mandate)",
    "H": "HistoricalContextualizatioN",
    "T": "TemporalDynamiX",
    "F": "FutureStateAnalysiS",
    "C": "CausalLagDetectioN",
    "E": "EmergenceOverTimE",
    "Tr": "TrajectoryComparisoN",
    "M₆": "Mandate 6: Temporal Resonance",
    "M₉": "Mandate 9: Complex System Visioning"
  }
};

export const SymbolCodex: React.FC = () => {
    return (
        <div className="bg-gray-800/50 rounded-lg p-6 border border-gray-700">
            <h3 className="text-lg font-bold text-gray-200 mb-4">Symbolic Codex</h3>
            <div className="space-y-3 max-h-96 overflow-y-auto pr-2">
                {Object.entries(codex.objective_generation_codex).map(([symbol, meaning]) => (
                    <div key={symbol} className="flex items-start">
                        <code className="w-16 text-center flex-shrink-0 text-lg font-bold text-cyan-400 bg-gray-900 px-2 py-1 rounded-md mr-4">
                            {symbol}
                        </code>
                        <span className="text-sm text-gray-300 leading-tight pt-1">{meaning}</span>
                    </div>
                ))}
            </div>
        </div>
    );
};
