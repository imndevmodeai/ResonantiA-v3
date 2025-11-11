#!/bin/bash
# Deployment script for Abstraction Framework

set -e

echo "🚀 Deploying Abstraction Framework..."

# Extract archive
if [ -f "abstraction_framework.tar.gz" ]; then
    tar xzf abstraction_framework.tar.gz
    echo "✅ Archive extracted"
fi

# Organize by use case
echo "📁 Framework structure:"
echo "  Skin Level:   docs/01_SKIN_LEVEL/"
echo "  Bones Level:  docs/02_BONES_LEVEL/"
echo "  Muscle Level: docs/03_MUSCLE_LEVEL/"
echo "  Soul Level:   docs/04_SOUL_LEVEL/"

# Copy code to appropriate location
echo "📋 Production code available in: code/"

# Import SPRs
echo "📌 SPRs available in: spr/"

echo "✅ Deployment complete!"
echo ""
echo "Quick Start:"
echo "  1. Read: docs/01_SKIN_LEVEL/ (for problem solving)"
echo "  2. Study: docs/02_BONES_LEVEL/ (for universal patterns)"
echo "  3. Understand: docs/03_MUSCLE_LEVEL/ (for mechanisms)"
echo "  4. Integrate: docs/04_SOUL_LEVEL/ (for consciousness)"
