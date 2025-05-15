# 📦 Changelog - CruscottoPMI

## [0.3] - Public Preview Release
### Aggiunte
- ✅ Modalità demo multi-anno e multi-azienda con calcolo KPI e bilancio
- ✅ Analisi YoY funzionante con export PDF + Excel
- ✅ Esportazione unificata con selezione KPI, Voci e YoY
- ✅ Integrazione del logo nel PDF
- ✅ Pubblicazione su Streamlit Cloud

### Fix
- 🔧 Risolti conflitti Git su `utils.py`, `04_export.py`, `02_yoy.py`, `03_confronto.py`
- 🔧 Corretta gestione `session_state` in modalità demo

### Tecnologie
- Python 3.9+
- Streamlit
- Pandas, Matplotlib, ReportLab, XlsxWriter

### Link Demo
🔗 [Apri l'app online](https://cruscottopmi-appv3eny73ucrbqzzkdb8ic.streamlit.app/)

---

📍Prossimi step (verso v0.4 / v1.0)
- [ ] UI/UX migliorata
- [ ] Gestione utenti o token
- [ ] Deploy persistente
- [ ] Validazione file bilancio “reale”
