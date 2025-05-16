# 📦 Changelog – CruscottoPMI v0.4

## 🚀 Novità principali

- ✅ **Supporto completo per più anni per azienda**
  - I moduli ora gestiscono correttamente bilanci 2022, 2023 (e futuri)
  - Selettori dinamici per anno nei moduli KPI, Scheda Azienda, Confronto

- ✅ **Compatibilità completa con file Excel reali**
  - Parsing anno/azienda da contenuto, con fallback da nome file
  - Nessuna sovrascrittura silenziosa in `session_state["bilanci"]`

- ✅ **Modalità demo migliorata**
  - Nessun errore se `uploaded_files` è `None`
  - Funziona con tutti i moduli inclusi YoY e Analisi Avanzata

- ✅ **Modulo YoY rifatto**
  - Selezione manuale di azienda e due anni qualsiasi
  - Confronto solo se entrambi i bilanci sono validi

- ✅ **Debug avanzato**
  - Modulo `07_debug_bilanci.py` per esplorazione diretta dei dati caricati

## 🐛 Bug risolti

- 🔧 Fix al parsing errato dell’anno nei file (2022 salvato come 2023)
- 🔧 Errore `name_parts` non definito rimosso
- 🔧 Preselezione forzata su `2023` eliminata dai moduli
- 🔧 Crash in demo mode (`NoneType` su `uploaded_files`) eliminato

## 🧱 Compatibilità

- ✅ File `.xlsx` con fogli: Conto Economico, Attivo, Passivo
- ✅ Colonne richieste: `Azienda`, `Anno`, `Voce`, `Importo (€)`
- ✅ Streamlit 1.22+, Pandas, Plotly

---

🎯 Prossima versione: `v0.5` → Focus su multi-azienda YoY, filtri avanzati KPI, refactor PDF.