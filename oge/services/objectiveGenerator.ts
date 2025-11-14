
import type { StageResult } from '../types';

const sprKeywordMap: { [key: string]: string } = {
    'historical': 'H', 'emergent': 'E', 'causal': 'C', 'predictive': 'F',
    'predicting': 'F', 'temporal': 'T', 'compare': 'Tr', 'matchup': 'Tr',
    'prime': 'H', 'circa': 'T', 'age': 'T'
};

function getCompression(inputLength: number, outputLength: number): number {
    if (outputLength === 0) return inputLength;
    return parseFloat((inputLength / outputLength).toFixed(2));
}

export function generateObjectivePipeline(query: string): StageResult[] {
    const results: StageResult[] = [];
    let currentInput = query;
    let cumulativeCompression = 1;

    // Stage 1: Feature Extraction
    const temporalMarkers = (query.match(/circa\s+\d{4}-\d{4}|age\s+\d+-\d+/g) || []).join(', ');
    const domainKeywords = ['boxing', 'match', 'prime'].filter(kw => query.toLowerCase().includes(kw)).join(', ');
    const complexityIndicators = ['emergent', 'causal', 'predictive'].filter(kw => query.toLowerCase().includes(kw));
    const sprKeywords = Object.keys(sprKeywordMap).filter(kw => query.toLowerCase().includes(kw));
    const stage1Output = `⦅temporal:[${temporalMarkers}], domain:[${domainKeywords}], complexity:[${complexityIndicators.join(', ')}]⦆`;
    let stageCompression = getCompression(currentInput.length, stage1Output.length);
    cumulativeCompression *= stageCompression;
    results.push({
        stageNumber: 1, title: "Feature Extraction", symbol: "⦅ F ⦆",
        input: `⟦${query}⟧`, output: stage1Output,
        stageCompression: stageCompression, cumulativeCompression: parseFloat(cumulativeCompression.toFixed(2))
    });
    currentInput = stage1Output;

    // Stage 2: TemporalScope Building
    const stage2Output = `Δ⦅explicit:"Historical primes", implicit:"Round-by-round", contextual:"Era differences"⦆`;
    stageCompression = getCompression(currentInput.length, stage2Output.length);
    cumulativeCompression *= stageCompression;
    results.push({
        stageNumber: 2, title: "TemporalScope Building", symbol: "Δ⦅ T ⦆",
        input: currentInput, output: stage2Output,
        stageCompression: stageCompression, cumulativeCompression: parseFloat(cumulativeCompression.toFixed(2))
    });
    currentInput = stage2Output;

    // Stage 3: SPR Activation
    const activatedSprs = [...new Set(sprKeywords.map(kw => sprKeywordMap[kw]))];
    const stage3Output = `⊢` + activatedSprs.join('⊢');
    stageCompression = getCompression(currentInput.length, stage3Output.length);
    cumulativeCompression *= stageCompression;
    results.push({
        stageNumber: 3, title: "SPR Activation", symbol: "⊢ SPR ⊢",
        input: currentInput, output: stage3Output,
        stageCompression: stageCompression, cumulativeCompression: parseFloat(cumulativeCompression.toFixed(2))
    });
    currentInput = stage3Output;

    // Stage 4: Mandate Selection
    const mandates = ['⊨Ω'];
    if (temporalMarkers) mandates.unshift('⊨M₆');
    if (complexityIndicators.length > 0) mandates.unshift('⊨M₉');
    const stage4Output = mandates.join('');
    stageCompression = getCompression(currentInput.length, stage4Output.length);
    cumulativeCompression *= stageCompression;
    results.push({
        stageNumber: 4, title: "Mandate Selection", symbol: "⊨ M ⊨",
        input: currentInput, output: stage4Output,
        stageCompression: stageCompression, cumulativeCompression: parseFloat(cumulativeCompression.toFixed(2))
    });
    currentInput = stage4Output;
    
    // Stage 5: Template Assembly
    const stage5Output = `⊧{Apply_full_spectrum...}`;
    stageCompression = getCompression(currentInput.length, stage5Output.length);
    cumulativeCompression *= stageCompression;
    results.push({
        stageNumber: 5, title: "Template Assembly", symbol: "⊧ T ⊧",
        input: currentInput, output: stage5Output,
        stageCompression: stageCompression, cumulativeCompression: parseFloat(cumulativeCompression.toFixed(2))
    });
    currentInput = stage5Output;
    
    // Stage 6: Domain Customization
    const stage6Output = `⊨{boxing_explanations}`;
    stageCompression = getCompression(currentInput.length, stage6Output.length);
    cumulativeCompression *= stageCompression;
    results.push({
        stageNumber: 6, title: "Domain Customization", symbol: "⊨ D ⊨",
        input: currentInput, output: stage6Output,
        stageCompression: stageCompression, cumulativeCompression: parseFloat(cumulativeCompression.toFixed(2))
    });
    currentInput = stage6Output;
    
    // Stage 7: Final Assembly
    const stage7Output = `⟧{problem_description}⟧`;
    stageCompression = getCompression(currentInput.length, stage7Output.length);
    cumulativeCompression *= stageCompression;
    results.push({
        stageNumber: 7, title: "Final Assembly", symbol: "⟦ PD ⟧",
        input: currentInput, output: stage7Output,
        stageCompression: stageCompression, cumulativeCompression: parseFloat(cumulativeCompression.toFixed(2))
    });
    currentInput = stage7Output;

    // Stage 8: Zepto Objective
    const zeptoSPR = `⟦Q⟧→${results[0].output.slice(0,15)}...→${results[1].output.slice(0,10)}...→${results[2].output}→${results[3].output}→⊧T→⊨D→⟧PD⟧`;
    const finalCumulativeCompression = getCompression(query.length, zeptoSPR.length);
    results.push({
        stageNumber: 8, title: "Zepto Objective", symbol: "◊ Z ◊",
        input: currentInput, output: zeptoSPR,
        stageCompression: getCompression(currentInput.length, zeptoSPR.length), 
        cumulativeCompression: parseFloat(finalCumulativeCompression.toFixed(2))
    });

    // Final Result as a separate "stage" for display
    results.push({
        stageNumber: 9, title: "Crystallized Zepto Objective", symbol: "◊",
        input: query,
        output: zeptoSPR,
        stageCompression: 0, // Not applicable
        cumulativeCompression: parseFloat(finalCumulativeCompression.toFixed(2))
    })

    return results;
}
