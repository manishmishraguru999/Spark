@echo off
REM BEAST pipeline launcher. Use Task Scheduler with an "At log on" trigger.
cd /d "%~dp0"
if not exist venv\Scripts\python.exe (
  echo venv not found. See README Step 3.
  pause
  exit /b 1
)
:loop
venv\Scripts\python.exe run_pipeline.py --config config.yaml
echo Pipeline stopped. Restarting in 30 seconds...
timeout /t 30 /nobreak >nul
goto loop
