@echo off
cd /d "%~dp0"
echo LivestockChain is starting... Your browser will open http://localhost:8501 
echo Do NOT close this window, or the app will stop.
venv\Scripts\python -m streamlit run app.py
pause
