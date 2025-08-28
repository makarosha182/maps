#!/bin/bash

# Sivas Tourism Advisor Startup Script

echo "🏛️  Sivas Tourism Advisor - Starting Service"
echo "================================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "   Please run: python3 -m venv venv"
    echo "   Then: source venv/bin/activate"
    echo "   Then: pip install -r requirements.txt"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "   Please copy env_example.txt to .env"
    echo "   And add your Claude API key"
    exit 1
fi

# Check if data exists
if [ ! -f "scraped_data/sivas_content.json" ]; then
    echo "⚠️  Scraped data not found. Running scraper first..."
    python scraper.py
    python vector_store.py
fi

# Check if vector database exists
if [ ! -d "vector_db" ]; then
    echo "⚠️  Vector database not found. Creating..."
    python vector_store.py
fi

echo "🚀 Starting Sivas Tourism Advisor..."
echo "   Open your browser: http://localhost:8000"
echo "   Press Ctrl+C to stop"
echo ""

# Start the service
python main.py
