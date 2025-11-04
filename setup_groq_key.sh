#!/bin/bash
# Quick script to add GROQ_API_KEY to .env file

echo "=========================================="
echo "ArchE Groq API Key Setup"
echo "=========================================="
echo ""
echo "Get your API key from: https://console.groq.com/keys"
echo ""
read -p "Enter your Groq API key: " GROQ_KEY

if [ -z "$GROQ_KEY" ]; then
    echo "❌ No API key provided. Exiting."
    exit 1
fi

ENV_FILE="/mnt/3626C55326C514B1/Happier/.env"

# Check if GROQ_API_KEY already exists
if grep -q "GROQ_API_KEY=" "$ENV_FILE"; then
    echo "Updating existing GROQ_API_KEY..."
    sed -i "s/GROQ_API_KEY=.*/GROQ_API_KEY=$GROQ_KEY/" "$ENV_FILE"
else
    echo "Adding GROQ_API_KEY to .env..."
    # Add after ANTHROPIC_API_KEY line
    sed -i "/ANTHROPIC_API_KEY=/a GROQ_API_KEY=$GROQ_KEY" "$ENV_FILE"
fi

echo ""
echo "✅ GROQ_API_KEY added to .env"
echo ""
echo "Testing Groq provider..."
cd /mnt/3626C55326C514B1/Happier
source arche_env/bin/activate
python3 Three_PointO_ArchE/llm_providers/groq_provider.py

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="



