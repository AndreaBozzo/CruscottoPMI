<<<<<<< HEAD
![Logo](.github/logo.png)

# 📊 Cruscotto Finanziario per PMI

Benvenuto nel Cruscotto Finanziario per PMI – uno strumento interattivo sviluppato in **Python + Streamlit** per analizzare i bilanci aziendali con indicatori, benchmark e visualizzazioni avanzate.
=======
# 📊 CruscottoPMI

**Cruscotto Finanziario per PMI** è un'applicazione interattiva sviluppata in Python e Streamlit per l'analisi automatizzata dei bilanci aziendali. Supporta il caricamento di bilanci in formato Excel, l'elaborazione di KPI, l'analisi delle voci di bilancio, variazioni YoY e l'esportazione completa in PDF ed Excel.
>>>>>>> 0c3ef1b (🚀 Versione stabile - Export completo e layout PDF migliorato)

---

## 🚀 Funzionalità principali

<<<<<<< HEAD
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
  ├── 04_export.py
  └── 05_analisi_avanzata.py
00_home.py
test material
=======
- 📈 **Calcolo KPI**: EBITDA Margin, ROE, ROI, Current Ratio e indice sintetico
- 🧮 **Dashboard Voci di Bilancio**: analisi interattiva delle voci economiche
- 🔁 **Analisi YoY**: variazioni anno su anno tra due bilanci consecutivi
- 🧪 **Modalità Demo**: dati pre-caricati per uso immediato
- 📤 **Esportazione PDF + Excel**: generazione report unificato con logo e note
- 📎 **Compatibilità multi-azienda e multi-anno**

---

## 📂 Struttura del progetto

```
CruscottoPMI/
├── assets/
│   └── logo.png              # Logo visualizzato nel PDF
├── cruscotto_pmi/
│   ├── __init__.py
│   └── utils.py              # Funzioni di analisi, export e PDF
├── pages/
│   ├── 01_kpi.py
│   ├── 02_yoy.py
│   ├── 03_confronto.py
│   ├── 04_export.py
│   └── 05_analisi_avanzata.py
├── 00_home.py                # Home page e caricamento file/demo
├── app.py                    # (opzionale) Avvio multipagina
>>>>>>> 0c3ef1b (🚀 Versione stabile - Export completo e layout PDF migliorato)
```

---

<<<<<<< HEAD
## ⚙️ Requisiti

- Python 3.10+
- Pandas
- Streamlit
- Plotly
=======
## 📦 Requisiti

- Python 3.9+
- Streamlit
- Pandas
- Matplotlib
- XlsxWriter
- ReportLab
>>>>>>> 0c3ef1b (🚀 Versione stabile - Export completo e layout PDF migliorato)

Installa tutto con:

```bash
pip install -r requirements.txt
```

---

<<<<<<< HEAD
## ▶️ Avvio
=======
## ▶️ Avvio dell'app

Assicurati di trovarti nella root del progetto, poi esegui:
>>>>>>> 0c3ef1b (🚀 Versione stabile - Export completo e layout PDF migliorato)

```bash
streamlit run 00_home.py
```

---

<<<<<<< HEAD
## 👤 Autore

Andrea Bozzo  
📫 andreabozzo92@gmail.com  
🔗 [LinkedIn](https://www.linkedin.com/in/andrea-bozzo-/)

---

## 📌 Note finali

Il progetto è in continua espansione. Ogni modulo è pensato per funzionare anche in assenza di file reali, grazie alla modalità demo integrata.
=======
## 📤 Esempio di output

Il report completo include:

- Logo
- Copertina con data
- KPI con indicatori sintetici
- Voci di bilancio formattate
- Analisi YoY
- Note finali utente

---

## 👨‍💻 Autore

**Andrea Bozzo**  
GitHub: [AndreaBozzo](https://github.com/AndreaBozzo)
Linkedin https://www.linkedin.com/in/andrea-bozzo-/
---

## 📝 Licenza

MIT License
>>>>>>> 0c3ef1b (🚀 Versione stabile - Export completo e layout PDF migliorato)
