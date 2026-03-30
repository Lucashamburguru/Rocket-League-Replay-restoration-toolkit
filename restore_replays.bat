@echo off
setlocal
color 0b

echo -------------------------------------------------------------------
echo     Rocket League Replay Restorer (v1.0) - Windows Version
echo -------------------------------------------------------------------
echo.

:: Check for python3
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python 3 is not installed or not in PATH.
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

:: Ensure current directory is the script's directory
cd /d "%~dp0"

:: Create default directories if they don't exist
if not exist "input_replays" mkdir input_replays
if not exist "restored_replays" mkdir restored_replays

:: Check for replays
dir /b "input_replays\*.replay" >nul 2>&1
if %errorlevel% neq 0 (
    echo --- No Replays Found ---
    echo.
    echo 1. Put your legacy .replay files into the 'input_replays' folder.
    echo 2. Run this script again.
    echo.
    pause
    exit /b 0
)

:: Run the restorer
python universal_batch_converter.py --input .\input_replays --output .\restored_replays

echo.
echo Operation complete.
echo Copy the files from 'restored_replays' to:
echo Documents\My Games\Rocket League\TAGame\Demos
echo.
pause
