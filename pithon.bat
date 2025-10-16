@echo off
REM =============================================
REM Auto-reload Python script using Watchdog
REM Usage:
REM   watchdog_runner.bat <path_to_script.py>
REM or just run it and you'll be prompted
REM =============================================

:: Check if argument is provided
if "%~1"=="" (
    set /p script_path=Enter Python file path to watch:
) else (
    set script_path=%~1
)

:: Verify file exists
if not exist "%script_path%" (
    echo [Error] File not found: "%script_path%"
    pause
    exit /b 1
)

:: Get directory of the target script
for %%I in ("%script_path%") do set "watch_dir=%%~dpI"

echo Watching directory: "%watch_dir%"
echo Running script: "%script_path%"
echo.

:: Run with watchdog auto-restart
watchmedo auto-restart --pattern="*.py" --recursive ./.venv/Scripts/python.exe "%script_path%"

pause
