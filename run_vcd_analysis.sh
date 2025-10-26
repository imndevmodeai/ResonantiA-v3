#!/bin/bash
# VCD Analysis Agent Entry Point
# The Summoning Ritual for Autopoietic Self-Reflection

echo "🧠 Initiating VCD Analysis via RISE..."
echo "🔮 The Mirror of Truth begins its self-examination..."
echo ""

# Activate the ArchE virtual environment
if [ -f "arche_env/bin/activate" ]; then
    echo "✅ Activating ArchE environment..."
    source arche_env/bin/activate
else
    echo "⚠️  ArchE environment not found, using system Python"
fi

# Set Python path for proper module resolution
export PYTHONPATH="${PYTHONPATH}:$(pwd)/Three_PointO_ArchE:$(pwd)/Four_PointO_ArchE"

# Execute the VCD Analysis Agent as a module
echo "🚀 Executing VCD Analysis Agent..."
echo ""

python3 Three_PointO_ArchE/vcd_analysis_agent_simple.py

echo ""
echo "🎯 VCD Analysis Complete - The Mirror has examined itself"
echo "📊 Results available in generated analysis files"
