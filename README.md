# 📊 CruscottoPMI

**Cruscotto Finanziario per PMI** è un'applicazione interattiva sviluppata in **Python + Streamlit** per l'analisi automatizzata dei bilanci aziendali. Consente di caricare file Excel, calcolare KPI, confrontare voci di bilancio tra anni e generare report PDF professionali.

---

## 🚀 Funzionalità principali

- 📈 Calcolo KPI: ROI, ROE, EBITDA Margin, Current Ratio, Indice Sintetico
- 📊 Analisi Voci di Bilancio: visualizzazioni interattive
- 📉 Analisi YoY: variazioni percentuali anno su anno
- 🧪 Modalità Demo: per testare l'app senza caricare file
- 📤 Export: generazione di PDF + Excel in ZIP, con logo e note
- 🧠 Supporto multi-azienda e multi-anno

---

## 🧰 Requisiti

- Python 3.9+
- Streamlit
- Pandas
- Matplotlib
- XlsxWriter
- ReportLab

Installa tutto con:

```bash
pip install -r requirements.txt
```

---

## ▶️ Avvio dell'app

Dalla root del progetto:

```bash
streamlit run 00_home.py
```

---

## 📂 Struttura del progetto

```
CruscottoPMI/
├── assets/                     # Contiene logo visibile nei PDF
├── pages/                      # Moduli multipagina Streamlit
│   ├── 01_kpi.py
│   ├── 02_yoy.py
│   ├── 03_confronto.py
│   ├── 04_export.py
│   └── 05_analisi_avanzata.py
├── src/cruscotto_pmi/         # Funzioni riutilizzabili (utils.py)
├── 00_home.py                 # Pagina iniziale (upload e demo)
├── README.md
└── .gitignore
```

---

## 📄 Esempio di report PDF

Il report esportato include:

- Copertina con titolo, logo e data
- Tabelle con KPI, bilanci e variazioni YoY
- Sezione note personalizzabili
- Logo dell'app integrato

---

## 👨‍💻 Autore

**Andrea Bozzo**  
[GitHub: AndreaBozzo](https://github.com/AndreaBozzo)

---

## 📝 Licenza

Questo progetto è rilasciato sotto licenza **MIT**.

