@echo off
set "VENV_DIR=venv"

if not exist %VENV_DIR% (
    echo Creating Virtual Environment...
    python -m venv %VENV_DIR%
)

echo Syncing libraries...
%VENV_DIR%\Scripts\pip install prompt-toolkit requests --upgrade --quiet

echo Starting...
%VENV_DIR%\Scripts\python.exe _main_.py
pause