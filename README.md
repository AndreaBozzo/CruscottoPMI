<p align="center">
  <img src="assets/logo.png" alt="CruscottoPMI Logo" width="250"/>
</p>

# 📊 CruscottoPMI

**CruscottoPMI** è un'applicazione interattiva costruita con Python e Streamlit per l'analisi economico-finanziaria di **Piccole e Medie Imprese** (PMI).  
Permette di caricare bilanci in formato Excel, analizzare KPI chiave, confrontare più aziende e generare report PDF professionali.

[![Version](https://img.shields.io/badge/version-v0.6-blue)](https://github.com/AndreaBozzo/CruscottoPMI/releases)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://cruscottopmi.streamlit.app/)

---

## 🚀 Funzionalità principali

- 📥 **Caricamento Excel** con mappatura intelligente dei fogli
- 📊 **Dashboard KPI** con selezione dinamica azienda/anno
- 📈 **Analisi YoY** delle variazioni % su bilanci pluriennali
- 🧠 **Visualizzazioni avanzate**: Heatmap, Radar, Gauge
- 🧪 **Modalità Demo** per uso immediato anche senza file
- 📝 **Export PDF personalizzabile** con note, grafici e KPI

---

## 📦 Requisiti

- Python 3.9–3.12
- Tutte le dipendenze sono elencate in [`requirements.txt`](requirements.txt)

Installa in locale con:

```bash
pip install -r requirements.txt
```

---

## ▶️ Come eseguire l'app

```bash
streamlit run 00_home.py
```

Oppure apri `00_home.py` da un IDE (es. VSCode) e avvia Streamlit.

---

## 🧪 Modalità Demo

La modalità demo è accessibile dalla Home senza caricare file.  
Include bilanci di esempio (`DemoCorp`, `BetaSpA`) e benchmark.

---

## 🖨️ Export PDF

Genera report professionali con:
- Copertina con logo
- Sezioni selezionabili (Radar, Heatmap, KPI, YoY, ecc.)
- Grafici integrati

---

## 📂 Struttura del progetto

```
CruscottoPMI/
│
├── pages/
│   ├── 00_home.py
│   ├── 01_scheda_azienda.py
│   ├── 02_dashboard_confronto.py
│   └── ...
│
├── cruscotto_pmi/
│   ├── utils.py
│   ├── charts.py
│   └── pdf_generator.py
│
├── assets/
│   └── logo.png
│
├── requirements.txt
└── README.md
```

---

## 📄 Licenza

Progetto open source rilasciato con licenza MIT.

---

## 🙋‍♂️ Autore

Realizzato da [Andrea Bozzo](https://github.com/AndreaBozzo)

---

## 🔜 Roadmap

- [x] v0.6 – Export PDF con grafici integrati
- [ ] v0.7 – Restyling UI/UX e tema grafico custom
- [ ] v1.0 – Simulazioni finanziarie avanzate e deploy pubblico
