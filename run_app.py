import os
import subprocess

# ✅ Imposta PYTHONPATH per permettere gli import da 'src'
os.environ["PYTHONPATH"] = "src"

# ✅ Avvia Streamlit dalla pagina principale
subprocess.run(["streamlit", "run", "00_home.py"])
