# 📘 CHANGELOG - Cruscotto Finanziario per PMI

📦 Changelog – 12 Maggio 2025

✅ Aggiunte

Aggiunto file tests/test_utils.py con test automatici su:

calcola_kpi() con dati realistici e benchmark vuoto

load_excel() da file Excel simulato via BytesIO

load_excel() con fogli mancanti → test su gestione errori

load_benchmark() da file CSV in memoria

Creata struttura di test con pytest

Installata e verificata compatibilità openpyxl, pandas, pytest

Introdotto confronto robusto tra DataFrame con assert_frame_equal

🛠 Refactoring
Refactoring funzione calcola_kpi() con fallback sicuro (.iloc[0] solo se presente)

Corretto comportamento su colonne mancanti o valori assenti

📁 Struttura repository
Creata cartella tests/ con suite pronta per CI

Aggiornato pyproject.toml per supportare testing e packaging

✅ Stato finale: tutti i test passano (pytest -v)

🔒 Pronto per CI/CD o future espansion

## [v1.0.0] - 2025-05-11
### 🔥 Build Completa e Stabile

- Refactoring completo con modularizzazione (`utils.py`).
- KPI calcolati dinamicamente con caching e benchmark editabili da sidebar.
- Importazione multipla di file Excel (uno per anno).
- Modalità Demo con dati fittizi precaricati.
- Dashboard interattiva: filtri per anno, KPI e voci bilancio.
- Calcolo variazione percentuale YoY per KPI e Ricavi.
- Confronto diretto con media di benchmark caricabile da CSV.
- Esportazione:
  - 📄 PDF con logo personalizzato e riepilogo aziendale.
  - 📥 Excel con KPI, YoY, confronto settoriale e voci bilancio.
- Styling condizionale dei KPI (verde/rosso).
- Corretto il problema degli anni in formato decimale → ora visualizzati come stringa.
- Ottimizzazioni su tempo di risposta e compatibilità su Streamlit Cloud.
- Inserita gestione errori più robusta per file Excel malformati.

---

## [v0.9.0] - 2025-05-08
### 🛠 Prima build completa

- Caricamento di bilanci da file Excel.
- Calcolo KPI principali: EBITDA Margin, ROE, ROI, Current Ratio.
- Visualizzazione interattiva con `plotly`.
- Export PDF e Excel statici.
- Classifica aziende su base KPI sintetico.
- Introdotta interfaccia semplificata con `streamlit`.

---

## 📅 Prossimi Step

- [ ] Integrazione backend (es. MongoDB o Google Sheets).
- [ ] Salvataggio configurazioni utente e sessione.
- [ ] Autenticazione e multi-utente.
- [ ] Funzione di upload logo personalizzato.
- [ ] Integrazione via API con altre fonti dati (Bilanci XBRL o ISTAT).

---

*Ultimo aggiornamento: 11 maggio 2025 - Andrea Bozzo*
