# Enhanced Ask_Arche Migration Guide v2.0

## 🚀 What's New in Enhanced v2.0

The enhanced unified entry point (`ask_arche_enhanced_v2.py`) includes:

### ✅ **Quantum Processing Verification**
- Automatically checks for Qiskit availability
- Verifies quantum utility functions
- Shows quantum processing status
- Uses quantum normalization when available

### ✅ **Cursor Environment Auto-Detection**
- Automatically detects if running in Cursor
- Checks multiple environment indicators
- Calculates detection confidence
- Logs all detection indicators

### ✅ **LLM Provider Auto-Configuration**
- Automatically configures LLM provider for Cursor ArchE
- Sets environment variables for system-wide defaults
- Updates config for RISE and other components
- Falls back gracefully if not in Cursor

### ✅ **Enhanced Reporting**
- Includes environment detection results
- Shows quantum processing status
- Displays LLM provider configuration
- Comprehensive system status

## 📋 Migration Steps

### Option 1: Use Enhanced v2 (Recommended)
```bash
# Use the new enhanced version
python ask_arche_enhanced_v2.py "your query here"
```

### Option 2: Replace Unified (Coming Soon)
The enhanced features will be merged into `ask_arche_unified.py` in a future update.

### Option 3: Environment Variables
```bash
# Manually set provider if auto-detection doesn't work
export ARCHE_LLM_PROVIDER=cursor
python ask_arche_unified.py "your query here"
```

## 🔧 Auto-Detection Details

### Cursor Environment Indicators Checked:
1. `CURSOR_ENABLED` environment variable
2. `CURSOR` environment variable
3. `CURSOR_API_KEY` environment variable
4. `VSCODE_CURSOR` environment variable
5. `TERM_PROGRAM` contains "Cursor"
6. `~/.cursor` directory exists
7. Executable path contains "cursor"
8. Current directory contains "cursor"

### Detection Confidence:
- **High (≥70%)**: Multiple indicators detected
- **Medium (30-69%)**: Some indicators detected
- **Low (<30%)**: Few/no indicators detected

## ⚛️ Quantum Processing Verification

### Checks Performed:
1. Qiskit import availability
2. Quantum utils module import
3. Specific quantum function availability:
   - `superposition_state`
   - `prepare_quantum_state_qiskit`
   - `evolve_flux_qiskit`
   - `detect_entanglement_qiskit`
   - `measure_insight_qiskit`
   - `entangled_state`
   - `compute_multipartite_mutual_information`

### Quantum Status Levels:
- **✅ FULL QUANTUM MODE**: Qiskit + 5+ quantum functions available
- **⚠️ PARTIAL QUANTUM MODE**: Qiskit + <5 functions available
- **⚠️ CLASSICAL SIMULATION MODE**: Quantum utils only (no Qiskit)
- **❌ CLASSICAL MODE ONLY**: No quantum capabilities

## 🔧 LLM Provider Configuration

### Automatic Configuration:
When Cursor is detected:
- Sets `ARCHE_LLM_PROVIDER=cursor`
- Sets `ARCHE_LLM_MODEL=cursor-arche-v1`
- Updates config for all components

### Manual Override:
```bash
export ARCHE_LLM_PROVIDER=google  # or cursor, groq, openai
export ARCHE_LLM_MODEL=gemini-2.0-flash-exp
python ask_arche_enhanced_v2.py "your query"
```

## 📊 Usage Examples

### Basic Usage:
```bash
python ask_arche_enhanced_v2.py "Analyze current AI trends"
```

### With Query:
```bash
python ask_arche_enhanced_v2.py "What are the quantum computing threats to encryption?"
```

### Force Provider (if auto-detection fails):
```bash
ARCHE_LLM_PROVIDER=cursor python ask_arche_enhanced_v2.py "your query"
```

## 🎯 Key Features Comparison

| Feature | ask_arche_unified.py | ask_arche_enhanced_v2.py |
|---------|---------------------|-------------------------|
| CognitiveIntegrationHub | ✅ | ✅ |
| VCD Integration | ✅ | ✅ |
| Quantum Superposition | ✅ | ✅ (Enhanced) |
| 13 Mandates | ✅ | ✅ |
| Tool Inventory | ✅ | ✅ |
| RealArchE Processor | ✅ | ✅ (Enhanced) |
| VCD Analysis Agent | ✅ | ✅ |
| **Quantum Verification** | ❌ | ✅ |
| **Cursor Auto-Detection** | ❌ | ✅ |
| **LLM Auto-Configuration** | ❌ | ✅ |
| **Enhanced Reporting** | ✅ | ✅ (Enhanced) |

## 🔍 Troubleshooting

### Issue: Cursor not detected
**Solution**: Manually set environment variable:
```bash
export CURSOR_ENABLED=1
python ask_arche_enhanced_v2.py "your query"
```

### Issue: Quantum processing not available
**Solution**: Install Qiskit:
```bash
pip install qiskit qiskit-aer
```

### Issue: LLM provider not switching to Cursor
**Solution**: Check detection results in output, or manually set:
```bash
export ARCHE_LLM_PROVIDER=cursor
```

## 📝 Notes

- The enhanced version maintains backward compatibility
- All existing features from `ask_arche_unified.py` are preserved
- New features are additive and don't break existing functionality
- Detection and configuration happen automatically on initialization

## 🚀 Next Steps

1. Test the enhanced version with your queries
2. Verify quantum processing if Qiskit is installed
3. Confirm Cursor auto-detection in your environment
4. Check LLM provider is correctly configured
5. Review enhanced reports for comprehensive system status

---

**Status**: ✅ Ready for use  
**Version**: 2.0  
**Date**: 2025-11-02

