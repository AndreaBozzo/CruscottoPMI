# 📊 CruscottoPMI

## 🌐 App online
[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/AndreaBozzo/CruscottoPMI/main/streamlit_app.py)

**CruscottoPMI** è un'applicazione interattiva sviluppata con Python e Streamlit, pensata per l'analisi finanziaria di Piccole e Medie Imprese (PMI).  
Fornisce insight chiari e visualizzazioni efficaci su bilanci, KPI, indicatori strutturali e benchmarking.

## 🚀 Funzionalità principali

- Caricamento multiplo di bilanci in formato Excel
- Analisi KPI e indicatori finanziari
- Benchmark personalizzabile o in modalità demo
- Variazioni YoY e confronto multi-anno o multi-azienda
- Heatmap, radar, gauge e dashboard interattive
- Esportazione in PDF + Excel (singola azienda/anno)
- Modalità demo per utilizzo senza caricamenti

## 🗂 Struttura multipagina

- `00_home.py`: Home page con caricamento dati o demo
- `01_scheda_azienda.py`: Riepilogo anagrafico e visivo del bilancio
- `02_kpi.py`: KPI dinamici, radar e gauge
- `03_confronto.py`: Analisi comparativa voci/aziende
- `04_yoy.py`: Variazioni YoY con opzione export
- `05_analisi_avanzata.py`: Heatmap, radar e confronto strutturale
- `06_export.py`: Generazione PDF + Excel in ZIP

## 📁 Requisiti

Consulta `requirements.txt` per la lista completa.

## 🧪 Modalità demo

La demo consente di esplorare tutte le funzionalità anche senza caricare file Excel.

## 📤 Output

- PDF dinamici con grafici e note
- Report Excel con KPI, bilancio, YoY

## 📌 Autore

Realizzato da Andrea Bozzo  
[GitHub](https://github.com/AndreaBozzo/CruscottoPMI)