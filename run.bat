@echo off
:: run.bat  –  Setup and launch for Student Skill Barter on Windows

echo.
echo   ⚡  Student Skill Barter – Setup
echo   ─────────────────────────────────────

:: Create venv if missing
if not exist venv (
    echo   Creating virtual environment...
    python -m venv venv
)

:: Activate
call venv\Scripts\activate.bat

:: Install deps
echo   Installing dependencies...
pip install -q -r requirements.txt

:: Check .env
if not exist .env (
    echo.
    echo   ⚠️  No .env file found!
    copy .env.example .env
    echo   .env created from template. Please edit it with your MySQL credentials, then run again.
    pause
    exit /b 1
)

echo.
echo   ✅  All set! Starting server...
echo   Open: http://localhost:5000
echo   Press CTRL+C to stop.
echo.

python app.py
pause
