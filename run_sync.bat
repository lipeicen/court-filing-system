@echo off
cd /d C:\court-auto-filing
call venv\Scripts\activate.bat
python sync_filing_status.py
pause
