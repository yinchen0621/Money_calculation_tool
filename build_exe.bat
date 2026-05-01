@echo off
cd /d "%~dp0"
python -m PyInstaller --noconsole --onefile --name "SalaryClock" salary_clock.py
