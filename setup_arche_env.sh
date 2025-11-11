#!/bin/bash
# Setup script for arche_env virtual environment
# Installs Project Chimera dependencies

echo "🧬 Setting up arche_env for Project Chimera..."

# Activate virtual environment
source arche_env/bin/activate

# Install XAI dependencies for Project Illumination
echo "📦 Installing XAI dependencies (shap, lime)..."
pip install shap>=0.42.0 lime>=0.2.0

# Verify installation
echo "✅ Verifying installations..."
python -c "import shap; print(f'SHAP version: {shap.__version__}')" 2>/dev/null || echo "⚠️  SHAP not installed"
python -c "import lime; print('LIME installed successfully')" 2>/dev/null || echo "⚠️  LIME not installed"

echo ""
echo "✅ Setup complete!"
echo "📝 To activate the environment in the future, run:"
echo "   source arche_env/bin/activate"

