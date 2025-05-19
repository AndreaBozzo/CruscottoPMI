
# 📊 CruscottoPMI

**CruscottoPMI** è un'applicazione interattiva costruita con Python e Streamlit per l'analisi economico-finanziaria di **Piccole e Medie Imprese** (PMI).  
Permette di caricare bilanci in formato Excel, analizzare KPI chiave, confrontare più aziende e generare report PDF professionali.

[![Version](https://img.shields.io/badge/version-v0.6-blue)](https://github.com/AndreaBozzo/CruscottoPMI/releases)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://cruscottopmi.streamlit.app/)

> 🎯 **Clicca sul badge "Open in Streamlit" qui sopra per aprire subito la demo online.**  
> Non serve installare nulla: puoi provare il Cruscotto direttamente dal browser.

---

---

## 🚀 Funzionalità v0.7

- ✅ Caricamento intelligente file Excel (riconosce nomi fogli e colonne anche non standard)
- 🧠 KPI con badge dinamici, benchmarking e commenti automatici
- 📉 Analisi YoY e confronto multi-anno / multi-azienda
- 📊 Heatmap, radar, gauge, e dashboard interattive
- 📤 Esportazione PDF + Excel con grafici e sintesi
- 🧪 Modalità Demo completa per esplorare l’app
- ⚙️ Architettura modulare e scalabile

---

## 🗂 Struttura Multipagina (v0.7)

- `00_home.py`: Home page, caricamento file o attivazione demo
- `01_scheda_azienda.py`: Riepilogo visivo bilancio + KPI core
- `02_dashboard_confronto.py`: KPI comparativi multi-azienda
- `03_confronto_voci.py`: Confronto dettagliato voci CE/SP
- `04_analisi_yoy.py`: Analisi variazioni % YoY
- `05_analisi_avanzata.py`: Heatmap, radar, KPI sintetici
- `06_export.py`: Generazione report PDF/Excel personalizzati

---

- Python 3.9–3.12
- Tutte le dipendenze sono elencate in [`requirements.txt`](requirements.txt)

Consulta [`requirements.txt`](requirements.txt) per la lista aggiornata delle dipendenze.

---

## ▶️ Come eseguire l'app

- PDF dinamici con logo, grafici (radar, gauge, heatmap) e commenti KPI
- Excel report per KPI, bilancio e variazioni YoY
- ZIP esportabile contenente tutti i file generati

---

## 🧪 Modalità Demo

La modalità demo consente di esplorare tutte le funzionalità con dati fittizi (DemoCorp & SampleSpa).

---

Oppure apri `00_home.py` da un IDE (es. VSCode) e avvia Streamlit.

Realizzato da **Andrea Bozzo**  
📁 [GitHub Repository](https://github.com/AndreaBozzo/CruscottoPMI)  
🌐 [App Online](https://cruscottopmi.streamlit.app/)

---

## 🏷 Versione

**v0.7 – 19 maggio 2025**
