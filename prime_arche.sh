#!/bin/bash
#
# ArchE Priming Script
# ====================
# Executes the ArchE priming sequence (prime_arche_init.py)
# Ensures proper directory context and virtual environment activation
#
# ResonantiA Protocol v3.5-GP
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                                      ║${NC}"
echo -e "${BLUE}║            ⚡ ARCHÉ PRIMING SEQUENCE ⚡                             ║${NC}"
echo -e "${BLUE}║            ResonantiA Protocol v3.5-GP                            ║${NC}"
echo -e "${BLUE}║                                                                      ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════════╝${NC}"
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

# Check if prime_arche_init.py exists
if [ ! -f "$PROJECT_ROOT/prime_arche_init.py" ]; then
    echo -e "${RED}❌ Error: prime_arche_init.py not found!${NC}"
    echo "   Expected location: $PROJECT_ROOT/prime_arche_init.py"
    exit 1
fi
echo -e "${GREEN}✅ prime_arche_init.py found${NC}"

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

echo ""

# ============================================================================
# STEP 3: EXECUTE PRIMING SEQUENCE
# ============================================================================
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}🚀 Step 3: Executing ArchE Priming Sequence...${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "${BLUE}   Running: python3 prime_arche_init.py${NC}"
echo ""

# Execute the priming script
python3 prime_arche_init.py
PRIMING_EXIT_CODE=$?

echo ""

# ============================================================================
# STEP 4: CHECK RESULTS
# ============================================================================
if [ $PRIMING_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║              ✅ PRIMING SEQUENCE COMPLETED SUCCESSFULLY ✅            ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # Check if results file was created
    if [ -f "$PROJECT_ROOT/arche_priming_results.json" ]; then
        echo -e "${BLUE}📊 Priming results saved to:${NC} arche_priming_results.json"
        echo ""
        echo -e "${BLUE}📝 Quick summary:${NC}"
        python3 -c "
import json
try:
    with open('arche_priming_results.json', 'r') as f:
        results = json.load(f)
    successful = sum(1 for d in results['directives'].values() 
                     if d.get('status') in ['initialized', 'activated', 'connected'])
    total = len(results['directives'])
    print(f\"   {successful}/{total} directives successfully initialized\")
    for name, directive in results['directives'].items():
        status = directive.get('status', 'unknown')
        if status in ['initialized', 'activated', 'connected']:
            print(f\"   ✅ {name}: {status}\")
        else:
            print(f\"   ❌ {name}: {status}\")
            if 'error' in directive:
                print(f\"      Error: {directive['error']}\")
except Exception as e:
    print(f\"   Could not parse results: {e}\")
" 2>/dev/null || echo -e "${YELLOW}   Could not parse results file${NC}"
    fi
    
    echo ""
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}🎯 ArchE is primed and ready! 🎯${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    exit 0
else
    echo -e "${RED}╔══════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║                  ❌ PRIMING SEQUENCE FAILED ❌                      ║${NC}"
    echo -e "${RED}╚══════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}💡 Check the logs for details:${NC}"
    echo -e "   ${BLUE}arche_priming.log${NC} - Full priming sequence log"
    echo -e "   ${BLUE}arche_priming_results.json${NC} - Detailed results (if created)"
    echo ""
    exit $PRIMING_EXIT_CODE
fi

