#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# --- Virtual Camera Check ---
if [ ! -e "/dev/video10" ]; then
    echo "Virtual camera device /dev/video10 not found."
    echo "Attempting to create virtual camera device..."
    
    # Try to create the virtual camera device
    if sudo modprobe v4l2loopback devices=1 video_nr=10 card_label="ArchE_Webcam" exclusive_caps=0 2>/dev/null; then
        echo "✅ Virtual camera device /dev/video10 created successfully!"
    else
        echo "❌ Failed to create virtual camera device."
        echo ""
        echo "Please run this command manually in your terminal:"
        echo "sudo modprobe v4l2loopback devices=1 video_nr=10 card_label=\"ArchE_Webcam\" exclusive_caps=0"
        echo ""
        echo "Alternatively, you can run the web UI without virtual camera support."
        echo "The web interface will still work for preview and configuration."
        echo ""
        read -p "Continue without virtual camera? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Exiting..."
            exit 1
        fi
    fi
else
    echo "✅ Virtual camera device /dev/video10 found."
fi

# --- Python Environment Activation ---
# Navigate to the project root
cd "$SCRIPT_DIR/.."

# Activate the virtual environment
if [ -f "arche_env/bin/activate" ]; then
    echo "Activating ArchE virtual environment..."
    source arche_env/bin/activate
else
    echo "Warning: Virtual environment not found. Using system Python."
fi

# --- Application Launch ---
echo "Starting ArchE Webcam Streaming System Web UI..."
echo "Web interface will be available at: http://localhost:5000"
echo "Press Ctrl+C to stop the server"

# Run the web UI application
python3 "$SCRIPT_DIR/web_ui.py"

# --- Shutdown ---
echo "ArchE Webcam Streaming System has been shut down."
