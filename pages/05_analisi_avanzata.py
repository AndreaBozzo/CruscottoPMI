import sys
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(BASE_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from cruscotto_pmi.utils import estrai_aziende_anni_disponibili, filtra_bilanci, calcola_kpi, genera_grafico_voci, genera_pdf

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("📈 Analisi Avanzata")
st.markdown("Analisi finanziaria approfondita: DuPont, Z-Score, radar KPI e altro.")

if "bilanci" not in st.session_state or not st.session_state["bilanci"]:
    st.warning("⚠️ Carica prima almeno un bilancio nella sezione Home.")
    st.stop()

aziende_disponibili, anni_disponibili = estrai_aziende_anni_disponibili(st.session_state["bilanci"])
azienda_sel = st.selectbox("Seleziona azienda", aziende_disponibili)
anno_sel = st.selectbox("Seleziona anno", sorted(anni_disponibili, reverse=True))

df_list = filtra_bilanci(st.session_state["bilanci"], azienda_sel, [anno_sel])
if not df_list:
    st.error("Nessun bilancio disponibile per azienda e anno selezionati.")
    st.stop()

bilancio = df_list[0]
ce = bilancio["ce"]
att = bilancio["att"]
pas = bilancio["pas"]
benchmark = st.session_state.get("benchmark", {})

st.divider()

# --- Analisi DuPont ---
with st.expander("📊 Analisi DuPont"):
    def estrai_valore(df, parole_chiave):
        colonne_possibili = ['voce', 'attività', 'passività e patrimonio netto']
        colonna = next((col for col in df.columns if col.lower() in colonne_possibili), None)
        if not colonna:
            st.error(f"Colonna descrittiva non trovata. Colonne disponibili: {df.columns.tolist()}")
            return None
        for parola in parole_chiave:
            match = df[df[colonna].str.contains(parola, case=False, na=False)]
            if not match.empty:
                return match['Importo (€)'].values[0]
        st.error(f"Valore non trovato per parole chiave: {parole_chiave}")
        return None

    utile_netto = estrai_valore(ce, ["utile", "risultato d'esercizio"])
    ricavi = estrai_valore(ce, ["ricavi", "valore della produzione"])
    attivo_totale = att["Importo (€)"].sum()
    patrimonio_netto = estrai_valore(pas, ["patrimonio netto"])

    if not all([utile_netto, ricavi, attivo_totale, patrimonio_netto]):
        st.warning("⚠️ Alcune voci necessarie non sono state trovate.")
    else:
        margine_netto = utile_netto / ricavi
        rotazione_attivi = ricavi / attivo_totale
        leva_finanziaria = attivo_totale / patrimonio_netto
        roe = margine_netto * rotazione_attivi * leva_finanziaria

        fig = go.Figure(data=[go.Bar(
            x=["Margine Netto", "Rotazione Attivi", "Leva Finanziaria", "ROE"],
            y=[margine_netto, rotazione_attivi, leva_finanziaria, roe],
            text=[f"{v:.2%}" for v in [margine_netto, rotazione_attivi, leva_finanziaria, roe]],
            textposition="outside"
        )])
        fig.update_layout(title="Scomposizione ROE (DuPont)", yaxis_tickformat=".0%")
        st.plotly_chart(fig, use_container_width=True)

# --- Radar KPI ---
with st.expander("📍 Radar KPI"):
    try:
        df_kpi = calcola_kpi(ce, att, pas, benchmark)
        row = pd.DataFrame(df_kpi, index=[0]).iloc[0]
        labels = [k for k in row.index if k not in ['Azienda', 'Valutazione']]
        values = [row[k] for k in labels]
        values += values[:1]; labels += labels[:1]
        radar = go.Figure(go.Scatterpolar(r=values, theta=labels, fill='toself'))
        radar.update_layout(polar=dict(radialaxis=dict(visible=True)))
        st.plotly_chart(radar, use_container_width=True)
    except Exception as e:
        st.error(f"Errore nella generazione del radar KPI: {e}")

# Sezione Heatmap
    else:
     st.header("🌡️ Heatmap Indicatori")
    heat_data = []
    error_entries = []
    for y in sorted(anni_disponibili):
        try:
            df_b = filtra_bilanci(st.session_state["bilanci"], azienda_sel, [y])[0]
            ce_y = df_b["ce"]
            att_y = df_b["att"]
            pas_y = df_b["pas"]
            benchmark = st.session_state["benchmark"]
            kpi_row = calcola_kpi(ce_y, att_y, pas_y, benchmark)
            kpi_row["Azienda"] = f"{azienda_sel}_{y}"  # 🔧 rende univoca la colonna
            heat_data.append(kpi_row)
        except Exception as e:
            error_entries.append((y, str(e)))
            continue
    # Mostra errori specifici
    for year, msg in error_entries:
        st.error(f"Anno {year}: {msg}")
    if not isinstance(heat_data, list):
        st.error("Errore nella struttura dati per Heatmap.")
        st.stop()
    if heat_data:
        df_heat = pd.DataFrame(heat_data).set_index('Azienda').T
        df_heat = df_heat.loc[:, ~df_heat.columns.duplicated()]  # 🔧 elimina duplicati
        st.dataframe(df_heat.style.background_gradient(axis=1))
    else:
        st.info("Heatmap non disponibile: nessun dato valido.")
df_export = st.session_state.get("df_kpi")  # o df_confronto / df_avanzata
if df_export is not None and not df_export.empty:
    st.subheader("📤 Esporta risultati")

    note = st.text_area("Note personali per il report", key="note_export_modulo_X")
    if st.button("📥 Esporta Report", key="btn_export_modulo_X"):

        grafico_kpi_buf = genera_grafico_kpi(df_export)
        grafico_voci_buf = genera_grafico_voci(st.session_state.get("df_voci", pd.DataFrame()))

        pdf_buf = genera_pdf(df_export, note, grafico_kpi_buf, grafico_voci_buf)

        excel_buf = BytesIO()
        df_export.to_excel(excel_buf, index=False)
        excel_buf.seek(0)

        zip_buf = BytesIO()
        with ZipFile(zip_buf, 'w') as zipf:
            zipf.writestr("report.pdf", pdf_buf.getvalue())
            zipf.writestr("export.xlsx", excel_buf.getvalue())
        zip_buf.seek(0)

        st.download_button("📁 Scarica ZIP", zip_buf.getvalue(), file_name="report.zip", key="zip_export_modulo_X")
