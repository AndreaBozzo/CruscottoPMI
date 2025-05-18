@echo off
cd /d "%~dp0"
echo Avvio CruscottoPMI su Streamlit...
start "" python -m streamlit run streamlit_app.py --server.headless false
