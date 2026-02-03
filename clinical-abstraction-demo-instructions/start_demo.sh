#!/bin/bash

echo "============================================================"
echo "Clinical Abstraction Demo - Starting..."
echo "============================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ Error: Python is not installed"
    echo "Please install Python 3.9 or higher"
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

# Check if dependencies are installed
echo "Checking dependencies..."
if ! $PYTHON_CMD -c "import flask" 2>/dev/null; then
    echo "⚠️  Dependencies not installed. Installing now..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        exit 1
    fi
fi

echo "✓ Dependencies OK"
echo ""

# Check for API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OPENAI_API_KEY environment variable not set"
    echo "You can either:"
    echo "  1. Set it now: export OPENAI_API_KEY='your-key-here'"
    echo "  2. Enter it in the web UI when the app starts"
    echo ""
    read -p "Press Enter to continue..."
fi

echo "Starting servers..."
echo ""

# Start Flask backend in background
echo "Starting Flask backend on port 5000..."
$PYTHON_CMD extraction_backend_openai.py > flask.log 2>&1 &
FLASK_PID=$!

# Wait a moment for Flask to start
sleep 2

# Check if Flask started successfully
if ! ps -p $FLASK_PID > /dev/null; then
    echo "❌ Failed to start Flask backend"
    echo "Check flask.log for details"
    exit 1
fi

# Start HTTP server in background
echo "Starting web server on port 8000..."
$PYTHON_CMD -m http.server 8000 > http.log 2>&1 &
HTTP_PID=$!

# Wait a moment for HTTP server to start
sleep 1

# Check if HTTP server started successfully
if ! ps -p $HTTP_PID > /dev/null; then
    echo "❌ Failed to start HTTP server"
    kill $FLASK_PID 2>/dev/null
    exit 1
fi

echo ""
echo "============================================================"
echo "✓ Demo is running!"
echo "============================================================"
echo ""
echo "Flask Backend: http://localhost:5000"
echo "Web App:       http://localhost:8000/index_ai_clean.html"
echo ""
echo "For Verily Workbench, use:"
echo "  https://workbench.verily.com/app/YOUR-WORKSPACE-ID/proxy/8000/index_ai_clean.html"
echo ""
echo "Logs:"
echo "  Flask:  tail -f flask.log"
echo "  HTTP:   tail -f http.log"
echo ""
echo "Press Ctrl+C to stop all servers"
echo "============================================================"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Stopping servers..."
    kill $FLASK_PID 2>/dev/null
    kill $HTTP_PID 2>/dev/null
    echo "✓ Servers stopped"
    exit 0
}

# Set trap to cleanup on Ctrl+C
trap cleanup SIGINT SIGTERM

# Wait for user to stop
wait
