# Cruscotto Finanziario per PMI - README

## Descrizione
Applicazione Streamlit per l’analisi finanziaria di PMI attraverso l’importazione di bilanci in formato Excel. Consente il confronto multi-anno e multi-azienda, con calcolo KPI, benchmark, grafici dinamici, esportazioni e classifiche sintetiche.

## Funzionalità principali
- 📂 Caricamento multiplo di bilanci Excel (multi-anno, multi-azienda)
- 📊 Calcolo KPI: EBITDA Margin, ROE, ROI, Current Ratio
- 🧠 Calcolo indice sintetico (normalizzato su 10) per classificare la solidità aziendale
- 🎯 Benchmark personalizzabile da CSV
- 🧾 Evidenziazione condizionale su KPI critici
- 📉 Visualizzazione dinamica di voci di bilancio chiave (Ricavi, Spese Operative, Ammortamenti, MOL...)
- 🏆 Classifica aziende per performance media
- 📤 Esportazione dei risultati in Excel (multi-foglio) e PDF (con logo incluso)

## Esempi di test
Abbiamo incluso nel repository i seguenti file di esempio:

```
📁 dati_test/
├── Alpha_2023.xlsx
├── Alpha_2024.xlsx
├── Beta_2023.xlsx
├── Beta_2024.xlsx
└── benchmark_kpi.csv (opzionale)
```

## Requisiti
- Python >= 3.8
- Streamlit
- Plotly
- Pandas
- ReportLab

## Avvio locale
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Note
Per aggiungere ulteriori aziende o anni, basta nominare i file Excel con il formato: `Azienda_Anno.xlsx` e strutturarli con i fogli:
- `Conto Economico`
- `Attivo`
- `Passivo`

Il file `benchmark_kpi.csv` opzionale deve avere questa struttura:
```csv
KPI,Valore
EBITDA Margin,15.0
ROE,10.0
ROI,8.0
Current Ratio,1.3
```

