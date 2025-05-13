# 📊 Cruscotto Finanziario per PMI

![Logo CruscottoPMI](https://raw.githubusercontent.com/AndreaBozzo/CruscottoPMI/main/.github/logo.png)

**CruscottoPMI** è un'applicazione interattiva sviluppata in Streamlit per analizzare i bilanci aziendali su più anni, confrontare aziende e monitorare i principali indicatori di performance (KPI). Ideale per piccole e medie imprese, consulenti e analisti.

---

## ✨ Interfaccia

![Screenshot](https://raw.githubusercontent.com/AndreaBozzo/CruscottoPMI/main/.github/screenshot_home.png)

---

## 🚀 Funzionalità principali

- 📁 Caricamento file Excel strutturati per anno
- 🧪 Modalità demo con aziende simulate
- 📊 Calcolo KPI: EBITDA Margin, ROE, ROI, Current Ratio
- 📈 Analisi variazioni YoY
- 📘 Confronto voci di bilancio
- 📤 Export risultati in Excel e PDF
- ✏️ Personalizzazione benchmark
- 💡 Interfaccia moderna e responsive

---

## 🗂️ Struttura multipagina

| Pagina              | Descrizione                             |
|---------------------|------------------------------------------|
| `00_home.py`        | Caricamento dati, modalità demo, benchmark |
| `pages/01_kpi.py`   | Calcolo e visualizzazione KPI            |
| `pages/02_yoy.py`   | Analisi variazione anno su anno          |
| `pages/03_confronto.py` | Confronto grafico voci bilancio         |
| `pages/04_export.py`| Download Excel e PDF                     |

---

## 📂 Formato file Excel richiesto

Ogni file `.xlsx` deve contenere i seguenti fogli:
- `Conto Economico`
- `Attivo`
- `Passivo`

Con una colonna chiamata `Importo (€)`.

---

## ▶️ Come eseguire

Assicurati di avere Python installato, poi:

```bash
pip install -r requirements.txt
streamlit run 00_home.py
```

---

## ☁️ Deploy su Streamlit Cloud

1. Crea un account su [streamlit.io/cloud](https://streamlit.io/cloud)
2. Collega la tua repo GitHub
3. Imposta come file principale: `00_home.py`
4. Aggiungi il file `.streamlit/config.toml` per un tema personalizzato (già incluso)

---

## 📬 Contatti

Sviluppato da Andrea Bozzo  
📧 andreabozzo92@gmail.com

---

## 📜 Licenza

Distribuito con licenza **MIT**