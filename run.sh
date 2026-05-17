#!/usr/bin/env bash
# run.sh  –  One-shot setup + launch for Student Skill Barter
# Usage:  bash run.sh

set -e
cd "$(dirname "$0")"

echo ""
echo "  ⚡  Student Skill Barter – Setup"
echo "  ─────────────────────────────────────"

# ── 1. Virtual environment ────────────────────────────────────────
if [ ! -d "venv" ]; then
    echo "  → Creating virtual environment…"
    python3 -m venv venv
fi

# Activate
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null

# ── 2. Dependencies ───────────────────────────────────────────────
echo "  → Installing dependencies…"
pip install -q -r requirements.txt

# ── 3. .env check ─────────────────────────────────────────────────
if [ ! -f ".env" ]; then
    echo ""
    echo "  ⚠️  No .env file found!"
    echo "     Copy .env.example to .env and fill in your MySQL credentials."
    echo ""
    cp .env.example .env
    echo "  → .env created from template. Please edit it now, then run this script again."
    exit 1
fi

# ── 4. Launch ─────────────────────────────────────────────────────
echo ""
echo "  ✅  All set! Starting server…"
echo "  ─────────────────────────────────────"
echo "  Open:  http://localhost:5000"
echo "  CTRL+C to stop"
echo ""

python app.py
