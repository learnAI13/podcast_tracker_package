#!/bin/bash
# Start all components of the 1-Click Podcast Guest Tracker

echo "Starting 1-Click Podcast Guest Tracker System"
echo "============================================="

# Check if mock LLM server is already running
if curl -s http://localhost:8080/health > /dev/null; then
    echo "✅ LLM server is already running"
else
    echo "🚀 Starting mock LLM server..."
    python /workspace/mock_llm_server.py > /tmp/llm_server.log 2>&1 &
    sleep 2
    if curl -s http://localhost:8080/health > /dev/null; then
        echo "✅ LLM server started successfully"
    else
        echo "❌ Failed to start LLM server"
        exit 1
    fi
fi

# Check if web app is already running
if curl -s http://localhost:12000/ > /dev/null; then
    echo "✅ Web app is already running"
else
    echo "🚀 Starting web app..."
    python /workspace/web_app.py > /tmp/web_app.log 2>&1 &
    sleep 2
    if curl -s http://localhost:12000/ > /dev/null; then
        echo "✅ Web app started successfully"
    else
        echo "❌ Failed to start web app"
        exit 1
    fi
fi

echo ""
echo "🎉 System is now running!"
echo "Web interface: https://work-1-bnbvcbisukylyyhn.prod-runtime.all-hands.dev"
echo "LLM server: http://localhost:8080"
echo ""
echo "You can use the CLI with:"
echo "  ./run_analyzer.py \"Guest Name\" \"Guest URL\" \"Host Channel URL\""
echo ""
echo "Or run the example script:"
echo "  ./run_example.sh"