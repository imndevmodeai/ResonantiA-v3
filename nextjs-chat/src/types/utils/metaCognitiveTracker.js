"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.MetaCognitiveTracker = void 0;
class MetaCognitiveTracker {
    static async track(content) {
        return {
            metacognitive_shift_active: this.detectMetacognitiveShift(content),
            sirc_phase: this.detectSIRCPhase(content),
            crc_active: this.detectCRC(content),
            dissonance_detected: this.detectDissonance(content),
            correction_applied: this.extractCorrection(content)
        };
    }
    static detectMetacognitiveShift(content) {
        const shiftPatterns = [
            /metacognitive\s*shift/i,
            /metacognitive\s*shifT/i,
            /pause.*analysis/i,
            /rethink.*approach/i,
            /correct.*course/i
        ];
        return shiftPatterns.some(pattern => pattern.test(content));
    }
    static detectSIRCPhase(content) {
        const sircPatterns = {
            'Intent Deconstruction': /intent\s*deconstruction|deconstruct.*intent/i,
            'Resonance Mapping': /resonance\s*mapping|map.*resonance/i,
            'Blueprint Generation': /blueprint\s*generation|generate.*blueprint/i,
            'Harmonization Check': /harmonization\s*check|harmonize.*plan/i,
            'Integrated Actualization': /integrated\s*actualization|actualize.*plan/i
        };
        for (const [phase, pattern] of Object.entries(sircPatterns)) {
            if (pattern.test(content)) {
                return phase;
            }
        }
        return undefined;
    }
    static detectCRC(content) {
        const crcPatterns = [
            /cognitive\s*reflection\s*cycle/i,
            /crc/i,
            /reflect.*thought/i,
            /examine.*trail/i
        ];
        return crcPatterns.some(pattern => pattern.test(content));
    }
    static detectDissonance(content) {
        const dissonancePatterns = [
            /dissonance/i,
            /contradiction/i,
            /inconsistency/i,
            /error.*detected/i,
            /misalignment/i
        ];
        return dissonancePatterns.some(pattern => pattern.test(content));
    }
    static extractCorrection(content) {
        const correctionPatterns = [
            /correction[:\s]*([^.\n]+)/i,
            /fix[:\s]*([^.\n]+)/i,
            /adjustment[:\s]*([^.\n]+)/i,
            /revision[:\s]*([^.\n]+)/i
        ];
        for (const pattern of correctionPatterns) {
            const match = content.match(pattern);
            if (match)
                return match[1] || match[0];
        }
        return undefined;
    }
}
exports.MetaCognitiveTracker = MetaCognitiveTracker;
