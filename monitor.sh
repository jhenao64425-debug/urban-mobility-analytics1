#!/bin/bash
# Monitor script for Urban Mobility Analytics

echo "======================================================"
echo "Urban Mobility Analytics - System Monitor"
echo "======================================================"
echo ""

# Check if collector is running
echo "📊 COLLECTOR STATUS:"
if pgrep -f "src.route_extraction --interval" > /dev/null; then
    COLLECTOR_PID=$(pgrep -f "src.route_extraction --interval")
    echo "✅ Running (PID: $COLLECTOR_PID)"
    echo ""
    echo "📋 Last 5 collections:"
    tail -5 logs/collector_background.log 2>/dev/null || echo "No logs yet"
else
    echo "❌ Not running"
    echo "Start with: python -m src.route_extraction --interval 120 &"
fi

echo ""
echo "---"
echo ""

# Check if dashboard is running
echo "🎨 DASHBOARD STATUS:"
if pgrep -f "streamlit run streamlit_app/app.py" > /dev/null; then
    STREAMLIT_PID=$(pgrep -f "streamlit run streamlit_app/app.py")
    echo "✅ Running (PID: $STREAMLIT_PID)"
    echo "📍 URL: http://localhost:8501"
else
    echo "❌ Not running"
    echo "Start with: python -m streamlit run streamlit_app/app.py &"
fi

echo ""
echo "---"
echo ""

# Database statistics
echo "💾 DATABASE STATUS:"
if [ -f "data/mobility.db" ]; then
    RECORD_COUNT=$(sqlite3 data/mobility.db "SELECT COUNT(*) FROM route_measurements;" 2>/dev/null || echo "0")
    echo "✅ SQLite: $RECORD_COUNT records"
else
    echo "❌ SQLite database not found"
fi

if [ -f "data/raw/route_weather_data.csv" ]; then
    CSV_COUNT=$(wc -l < data/raw/route_weather_data.csv)
    echo "✅ CSV: $CSV_COUNT lines"
else
    echo "❌ CSV backup not found"
fi

echo ""
echo "---"
echo ""

# Log directory
echo "📁 LOGS:"
if [ -d "logs" ]; then
    echo "✅ Logs directory exists"
    if [ -f "logs/collector.log" ]; then
        LAST_ENTRY=$(tail -1 logs/collector.log)
        echo "   $LAST_ENTRY"
    fi
else
    echo "❌ Logs directory not found"
fi

echo ""
echo "======================================================"
echo "Monitor complete"
echo "======================================================"
