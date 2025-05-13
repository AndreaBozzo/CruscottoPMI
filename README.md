# 📊 Cruscotto Finanziario per PMI

**Cruscotto Finanziario per PMI** è un'applicazione interattiva sviluppata in Streamlit per analizzare i bilanci aziendali su più anni, confrontare aziende e monitorare i principali indicatori di performance (KPI). È pensato per piccole e medie imprese, consulenti e analisti.

---

## 🚀 Funzionalità principali

- ✅ Caricamento file Excel (uno per anno) con struttura predefinita.
- 🧪 Modalità demo con dati simulati per più aziende.
- ✏️ Personalizzazione dei benchmark KPI.
- 📊 Calcolo KPI: EBITDA Margin, ROE, ROI, Current Ratio, Indice Sintetico.
- 📈 Analisi variazione YoY su KPI selezionati.
- 📘 Confronto visuale tra voci di bilancio.
- 📤 Esportazione risultati in Excel e PDF.

---

## 📁 Struttura multipagina

| Pagina        | Descrizione                                   |
|---------------|-----------------------------------------------|
| `00_home.py`        | Caricamento dati e benchmark              |
| `01_kpi.py`         | Calcolo e visualizzazione KPI             |
| `02_yoy.py`         | Analisi variazione YoY                    |
| `03_confronto.py`   | Confronto grafico voci bilancio           |
| `04_export.py`      | Download Excel e PDF                      |

---

## 📂 Formato atteso file Excel

Ogni file Excel deve contenere **3 fogli** denominati:

- `Conto Economico`
- `Attivo`
- `Passivo`

Ogni foglio deve avere la colonna `Importo (€)` con le voci rilevanti.

---

## ▶️ Come avviare il progetto

1. Installa le dipendenze (in un ambiente virtuale):

```bash
pip install -r requirements.txt
```

2. Avvia Streamlit:

```bash
streamlit run 00_home.py
```

3. Per modalità multipagina, assicurati di avere una struttura come questa:

```
📁 cruscotto_pmi/
├── 00_home.py
├── pages/
│   ├── 01_kpi.py
│   ├── 02_yoy.py
│   ├── 03_confronto.py
│   └── 04_export.py
```

---

## 📬 Contatti

Sviluppato da Andrea Bozzo.  
Per feedback o richieste: `andreabozzo92@gmail.com`

---

## 📜 Licenza

Questo progetto è distribuito con licenza **MIT**.