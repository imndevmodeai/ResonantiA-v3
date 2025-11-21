#!/bin/bash
# Start Zepto Web Interface

echo "🚀 Starting Zepto Compression Web Interface..."
echo ""

# Check if Flask is installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "❌ Flask is not installed."
    echo "   Installing Flask..."
    pip install -r zepto_web_requirements.txt
fi

# Check if Zepto module is available
if python3 -c "from Three_PointO_ArchE.zepto_spr_processor import compress_to_zepto" 2>/dev/null; then
    echo "✅ Zepto compression module: Available"
else
    echo "⚠️  Zepto compression module: Not available (app will show error)"
fi

echo ""
echo "📱 Starting Flask server..."
echo "   Access the interface at: http://localhost:5000"
echo "   Press Ctrl+C to stop"
echo ""

python3 zepto_web_app.py

