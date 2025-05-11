# 📘 CHANGELOG - Cruscotto Finanziario per PMI

Tieni traccia delle modifiche, nuove funzionalità e fix implementati nel progetto.

---

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
