#!/usr/bin/env bash
set -e

echo "========================================================"
echo " Starting The Lenny Growth Assistant (Local Dev Mode)  "
echo "========================================================"

# Check if Docker is running for PostgreSQL with pgvector
if command -v docker &> /dev/null; then
    echo "🐳 Starting PostgreSQL + pgvector container..."
    docker compose up -d postgres
    echo "⏳ Waiting for PostgreSQL to become ready..."
    sleep 3
else
    echo "⚠️ Docker not detected. Please ensure a PostgreSQL instance with pgvector is running at localhost:5432."
fi

# Backend Setup
echo "📦 Setting up Python Backend..."
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt

# Run database init & sample ingestion
python3 ../scripts/ingest_transcripts.py --sample

# Launch Backend in background
echo "🚀 Launching FastAPI backend on http://localhost:8000..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Frontend Setup
echo "💻 Setting up React Frontend..."
cd ../frontend
npm install
echo "🚀 Launching Frontend on http://localhost:3000..."
npm run dev &
FRONTEND_PID=$!

echo "========================================================"
echo " ✅ The Lenny Growth Assistant is Live!                 "
echo " 👉 Web Application: http://localhost:3000             "
echo " 👉 API Docs & Health: http://localhost:8000/docs       "
echo "========================================================"

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT
wait
