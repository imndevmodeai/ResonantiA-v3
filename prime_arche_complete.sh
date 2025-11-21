#!/bin/bash
#
# ArchE Complete Priming Script
# ==============================
# Executes the ArchE unified priming sequence (arche_unified_init.py)
# This is the COMPLETE version with all advanced features:
# - Zepto Compression/Decompression with full file ingestion
# - Auto-ingestion of PRIME protocol
# - Zepto-compressed SPR file handling
# - Protocol chunk loading for ACO
# - SPR Auto-Priming System
# - Session Auto-Capture System
# - Autopoietic Learning Loop
# - ThoughtTrail Monitoring
#
# ResonantiA Protocol v3.5-GP
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${CYAN}╔══════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                                                                      ║${NC}"
echo -e "${CYAN}║        ⚡ ARCHÉ COMPLETE PRIMING SEQUENCE ⚡                         ║${NC}"
echo -e "${CYAN}║        ResonantiA Protocol v3.5-GP - Unified System               ║${NC}"
echo -e "${CYAN}║                                                                      ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Get script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$SCRIPT_DIR"

echo -e "${GREEN}📂 Project Root:${NC} $PROJECT_ROOT"
echo ""

# ============================================================================
# STEP 1: NAVIGATE TO PROJECT ROOT
# ============================================================================
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}📁 Step 1: Navigating to project root...${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

cd "$PROJECT_ROOT" || {
    echo -e "${RED}❌ Failed to change to project root directory${NC}"
    exit 1
}

echo -e "${GREEN}✅ Changed to: $(pwd)${NC}"
echo ""

# ============================================================================
# STEP 2: CHECK PREREQUISITES
# ============================================================================
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}🔍 Step 2: Checking prerequisites...${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Check if arche_unified_init.py exists
if [ ! -f "$PROJECT_ROOT/arche_unified_init.py" ]; then
    echo -e "${RED}❌ Error: arche_unified_init.py not found!${NC}"
    echo "   Expected location: $PROJECT_ROOT/arche_unified_init.py"
    exit 1
fi
echo -e "${GREEN}✅ arche_unified_init.py found${NC}"

# Check virtual environment
if [ ! -d "$PROJECT_ROOT/arche_env" ]; then
    echo -e "${YELLOW}⚠️  Warning: arche_env virtual environment not found!${NC}"
    echo "   Expected location: $PROJECT_ROOT/arche_env"
    echo ""
    echo "   The priming script will attempt to use system Python."
    echo "   For best results, create the virtual environment:"
    echo "   cd $PROJECT_ROOT"
    echo "   python3 -m venv arche_env"
    echo "   source arche_env/bin/activate"
    echo "   pip install -r requirements.txt"
    echo ""
else
    echo -e "${GREEN}✅ Virtual environment found${NC}"
    
    # Activate virtual environment
    echo -e "${BLUE}   Activating arche_env...${NC}"
    source "$PROJECT_ROOT/arche_env/bin/activate" || {
        echo -e "${YELLOW}⚠️  Failed to activate virtual environment, continuing with system Python${NC}"
    }
    
    if [ -n "$VIRTUAL_ENV" ]; then
        echo -e "${GREEN}✅ Virtual environment activated${NC}"
        echo -e "${BLUE}   Python: $(which python3)${NC}"
        echo -e "${BLUE}   Python version: $(python3 --version)${NC}"
    fi
fi

# Check Python availability
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Error: python3 not found in PATH${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python3 available: $(which python3)${NC}"

# Check for PRIME protocol file (optional but recommended)
PRIME_PROTOCOL_FILE="$PROJECT_ROOT/PRIME_ARCHE_PROTOCOL_3.5-GP.md"
if [ -f "$PRIME_PROTOCOL_FILE" ]; then
    echo -e "${GREEN}✅ PRIME protocol file found${NC}"
else
    echo -e "${YELLOW}⚠️  PRIME protocol file not found (optional)${NC}"
    echo "   Expected: $PRIME_PROTOCOL_FILE"
    echo "   The system will continue but may have limited protocol context."
fi

echo ""

# ============================================================================
# STEP 3: EXECUTE UNIFIED PRIMING SEQUENCE
# ============================================================================
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}🚀 Step 3: Executing ArchE Unified Priming Sequence...${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "${MAGENTA}📋 Complete Priming Features:${NC}"
echo -e "${BLUE}   • Zepto Compression/Decompression System${NC}"
echo -e "${BLUE}   • PRIME Protocol Auto-Ingestion${NC}"
echo -e "${BLUE}   • SPR Auto-Priming System${NC}"
echo -e "${BLUE}   • Session Auto-Capture System${NC}"
echo -e "${BLUE}   • Autopoietic Learning Loop${NC}"
echo -e "${BLUE}   • ThoughtTrail Monitoring${NC}"
echo ""
echo -e "${BLUE}   Running: python3 arche_unified_init.py${NC}"
echo ""

# Execute the unified priming script
python3 arche_unified_init.py
PRIMING_EXIT_CODE=$?

echo ""

# ============================================================================
# STEP 4: CHECK RESULTS
# ============================================================================
if [ $PRIMING_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║        ✅ COMPLETE PRIMING SEQUENCE COMPLETED SUCCESSFULLY ✅        ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # Check if results file was created
    RESULTS_FILE="$PROJECT_ROOT/arche_unified_init_results.json"
    if [ -f "$RESULTS_FILE" ]; then
        echo -e "${BLUE}📊 Priming results saved to:${NC} arche_unified_init_results.json"
        echo ""
        echo -e "${BLUE}📝 Detailed summary:${NC}"
        python3 -c "
import json
import sys
try:
    with open('arche_unified_init_results.json', 'r') as f:
        results = json.load(f)
    
    # Count successful directives
    directives = results.get('directives', {})
    successful = sum(1 for d in directives.values() 
                     if isinstance(d, dict) and d.get('status') in ['initialized', 'activated', 'connected', 'already_activated', 'detected'])
    total = len(directives)
    
    print(f\"   {successful}/{total} directives successfully initialized\")
    print(\"\")\n    
    # Display each directive status
    for name, directive in directives.items():
        if isinstance(directive, dict):
            status = directive.get('status', 'unknown')
            emoji = '✅' if status in ['initialized', 'activated', 'connected', 'already_activated', 'detected'] else '❌'
            print(f\"   {emoji} {name}: {status}\")
            
            # Show additional details for key directives
            if name == 'zepto_system' and 'compression_ratio' in directive:
                print(f\"      Compression Ratio: {directive['compression_ratio']:.2f}x\")
            if name == 'spr_priming' and 'sprs_loaded' in directive:
                print(f\"      SPRs Loaded: {directive['sprs_loaded']}\")
            if name == 'session_capture' and 'output_dir' in directive:
                print(f\"      Output Directory: {directive['output_dir']}\")
            if name == 'thought_trail' and 'trail_length' in directive:
                print(f\"      Trail Length: {directive['trail_length']}\")
            
            # Show errors if any
            if 'error' in directive and directive['error']:
                print(f\"      ⚠️  Error: {directive['error'][:100]}...\")
        else:
            print(f\"   ⚠️  {name}: Invalid directive format\")
    
    # Show initialized objects
    initialized = results.get('initialized_objects', {})
    if initialized:
        print(\"\")
        print(\"   📦 Initialized Objects:\")
        for obj_name, obj_status in initialized.get('references', {}).items():
            if obj_status:
                print(f\"      ✅ {obj_name}\")
            else:
                print(f\"      ❌ {obj_name} (not initialized)\")
    
except FileNotFoundError:
    print(\"   ⚠️  Results file not found\")
except json.JSONDecodeError as e:
    print(f\"   ⚠️  Could not parse results JSON: {e}\")
except Exception as e:
    print(f\"   ⚠️  Error parsing results: {e}\")
    sys.exit(1)
" 2>/dev/null || echo -e "${YELLOW}   Could not parse results file${NC}"
    else
        echo -e "${YELLOW}⚠️  Results file not found at expected location${NC}"
    fi
    
    # Check for log file
    LOG_FILE="$PROJECT_ROOT/arche_unified_init.log"
    if [ -f "$LOG_FILE" ]; then
        echo ""
        echo -e "${BLUE}📋 Full log available at:${NC} arche_unified_init.log"
    fi
    
    echo ""
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}🎯 ArchE Unified System is fully primed and ready! 🎯${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${CYAN}💡 Next Steps:${NC}"
    echo -e "${BLUE}   • All systems are initialized and stored in global namespace${NC}"
    echo -e "${BLUE}   • Zepto compression/decompression is ready for file operations${NC}"
    echo -e "${BLUE}   • SPR Auto-Priming System is active${NC}"
    echo -e "${BLUE}   • Session Auto-Capture is monitoring${NC}"
    echo -e "${BLUE}   • Autopoietic Learning Loop is engaged${NC}"
    echo -e "${BLUE}   • ThoughtTrail Monitoring is tracking cognitive processes${NC}"
    echo ""
    
    exit 0
else
    echo -e "${RED}╔══════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║              ❌ COMPLETE PRIMING SEQUENCE FAILED ❌                ║${NC}"
    echo -e "${RED}╚══════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}💡 Check the logs for details:${NC}"
    echo -e "   ${BLUE}arche_unified_init.log${NC} - Full unified priming sequence log"
    echo -e "   ${BLUE}arche_unified_init_results.json${NC} - Detailed results (if created)"
    echo ""
    echo -e "${YELLOW}🔍 Common Issues:${NC}"
    echo -e "   • Virtual environment not activated properly"
    echo -e "   • Missing dependencies (check requirements.txt)"
    echo -e "   • PRIME protocol file not found (optional but recommended)"
    echo -e "   • SPR definitions file missing or corrupted"
    echo -e "   • File permissions issues"
    echo ""
    exit $PRIMING_EXIT_CODE
fi


65440........................................................................