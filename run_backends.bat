@echo off
echo 🚀 Starting Aptitude and JD Generator Backends...

:: Check if venv exists and activate it
if exist venv\Scripts\activate (
    echo 🔧 Activating virtual environment...
    call venv\Scripts\activate
)

python run_all_backends.py
pause
