📊 Cruscotto Finanziario per PMI
CruscottoPMI è un'applicazione sviluppata in Python con Streamlit, progettata per analizzare, confrontare e monitorare gli indicatori economico-finanziari delle piccole e medie imprese (PMI) in modo intuitivo ed efficiente.

⚙️ Funzionalità principali
📁 Caricamento multiplo di bilanci (uno per anno) da file Excel

📉 Analisi KPI fondamentali: EBITDA Margin, ROE, ROI, Current Ratio

📊 Benchmarking settoriale personalizzabile

🔁 Variazioni YoY calcolate automaticamente

🧮 Indice sintetico normalizzato (scala 0–10)

🧩 Dashboard comparativa per voci di ricavo e costo (es. EBIT, Ammortamenti, MOL)

🖍️ Stile condizionale nei riepiloghi (celle rosse/verde)

📝 Esportazione in PDF e Excel

🧪 Modalità Demo con dati di esempio caricabili

✨ Modularizzazione codice tramite utils.py

💾 Caching intelligente per prestazioni migliorate

📂 Struttura dei file
bash
Copia
Modifica
📦 cruscottopmi/
├── app.py                 # Applicazione principale Streamlit
├── utils.py               # Funzioni ausiliarie e caching
├── requirements.txt       # Dipendenze per l’ambiente virtuale
├── demo/
│   └── file_demo.xlsx     # File demo pre-caricato
├── benchmarks/
│   └── benchmark_esempio.csv
🚀 Avvio dell'app
bash
Copia
Modifica
pip install -r requirements.txt
streamlit run app.py
Per forzare l'avvio su una porta specifica:

bash
Copia
Modifica
streamlit run app.py --server.port 8501
🧪 Modalità Demo
Spunta l'opzione 🔍 Usa dati di esempio all’avvio dell’app per testare tutte le funzionalità senza caricare file.

📎 Requisiti
Il file requirements.txt include tutte le dipendenze essenziali. Alcuni pacchetti chiave:

streamlit

pandas

plotly

reportlab

xlsxwriter

🤝 Autore
Progetto sviluppato da Andrea Bozzo come portfolio interattivo e strumento a supporto di PMI italiane.
