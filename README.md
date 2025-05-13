![Logo](.github/logo.png)

# 📊 Cruscotto Finanziario per PMI

Benvenuto nel Cruscotto Finanziario per PMI – uno strumento interattivo sviluppato in **Python + Streamlit** per analizzare i bilanci aziendali con indicatori, benchmark e visualizzazioni avanzate.

---

## 🚀 Funzionalità principali

- ✅ **Caricamento file Excel** con CE, Attivo e Passivo
- 🧪 **Modalità Demo** integrata (DemoCorp 2022–2023 con variazioni)
- 📈 Analisi **KPI chiave**: ROE, ROI, Current Ratio, EBITDA Margin
- 📊 Modulo **DuPont**, **Z-Score di Altman**
- 📉 Grafico **Radar KPI** e **Heatmap temporale**
- 🔁 Analisi **Year-over-Year**
- 📎 Confronto tra aziende/anni multipli
- 📝 Esportazione report in PDF/Excel

---

## 🧪 Modalità Demo

Non hai bilanci reali da caricare? Attiva la modalità demo direttamente nella home!

```bash
DemoCorp 2022:
  Ricavi: 1.000.000 €
  Utile netto: 80.000 €
DemoCorp 2023:
  Ricavi: 1.120.000 €
  Utile netto: 89.600 €
```

La demo è **completa** e compatibile con tutti i moduli, utile per:
- test funzionali
- demo live
- colloqui e portfolio

---

## 📁 Struttura dei file

```
src/
  cruscotto_pmi/
    ├── utils.py
    └── ...
pages/
  ├── 01_kpi.py
  ├── 02_yoy.py
  ├── 03_confronto.py
  └── 05_analisi_avanzata.py
00_home.py
```

---

## ⚙️ Requisiti

- Python 3.10+
- Pandas
- Streamlit
- Plotly

Installa tutto con:

```bash
pip install -r requirements.txt
```

---

## ▶️ Avvio

```bash
streamlit run 00_home.py
```

---

## 👤 Autore

Andrea Bozzo  
📫 andreabozzo92@gmail.com  
🔗 [LinkedIn](https://www.linkedin.com/in/andrea-bozzo-/)

---

## 📌 Note finali

Il progetto è in continua espansione. Ogni modulo è pensato per funzionare anche in assenza di file reali, grazie alla modalità demo integrata.
