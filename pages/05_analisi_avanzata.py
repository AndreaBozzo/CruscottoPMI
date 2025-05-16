
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from cruscotto_pmi.utils import estrai_aziende_anni_disponibili, filtra_bilanci, calcola_kpi, genera_grafico_voci, genera_pdf, genera_grafico_kpi
from io import BytesIO
from zipfile import ZipFile

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

df = df_list[0]
ce = df[df["Tipo"] == "Conto Economico"]
att = df[df["Tipo"] == "Attivo"]
pas = df[df["Tipo"] == "Passivo"]
benchmark = st.session_state.get("benchmark", {})

st.divider()

# --- Analisi DuPont ---
with st.expander("📊 Analisi DuPont"):
    def estrai_valore(df, parole_chiave):
        colonna = next((c for c in df.columns if c.lower() in ['voce', 'attività', 'passività e patrimonio netto']), None)
        if not colonna:
            return None
        for parola in parole_chiave:
            match = df[df[colonna].str.contains(parola, case=False, na=False)]
            if not match.empty:
                return match["Importo (€)"].values[0]
        return None

    utile_netto = estrai_valore(ce, ["utile", "risultato"])
    ricavi = estrai_valore(ce, ["ricavi", "produzione"])
    attivo_totale = att["Importo (€)"].sum()
    patrimonio_netto = estrai_valore(pas, ["patrimonio netto"])

    if not all([utile_netto, ricavi, attivo_totale, patrimonio_netto]):
        st.warning("⚠️ Alcuni valori DuPont non disponibili.")
    else:
        margine_netto = utile_netto / ricavi
        rotazione_attivi = ricavi / attivo_totale
        leva = attivo_totale / patrimonio_netto
        roe = margine_netto * rotazione_attivi * leva

        fig = go.Figure(data=[go.Bar(
            x=["Margine Netto", "Rotazione Attivi", "Leva", "ROE"],
            y=[margine_netto, rotazione_attivi, leva, roe],
            text=[f"{x:.2%}" for x in [margine_netto, rotazione_attivi, leva, roe]],
            textposition="outside"
        )])
        fig.update_layout(title="Scomposizione ROE (DuPont)", yaxis_tickformat=".0%")
        st.plotly_chart(fig, use_container_width=True)

# --- Radar KPI ---
with st.expander("📍 Radar KPI"):
    try:
        kpi_dict = calcola_kpi(ce, att, pas, benchmark)
        if "Errore" in kpi_dict:
            st.error(f"KPI Error: {kpi_dict['Errore']}")
        else:
            row = pd.DataFrame(kpi_dict, index=[0]).iloc[0]
            labels = [k for k in row.index if k not in ['Azienda', 'Valutazione']]
            values = [row[k] for k in labels]
            values += values[:1]; labels += labels[:1]
            radar = go.Figure(go.Scatterpolar(r=values, theta=labels, fill='toself'))
            radar.update_layout(polar=dict(radialaxis=dict(visible=True)))
            st.plotly_chart(radar, use_container_width=True)
    except Exception as e:
        st.error(f"Errore Radar KPI: {e}")

# --- Heatmap KPI ---
with st.expander("🌡️ Heatmap Indicatori"):
    heat_data = []
    error_entries = []

    for y in sorted(anni_disponibili):
        try:
            df_b_list = filtra_bilanci(st.session_state["bilanci"], azienda_sel, [y])
            if not df_b_list:
                raise ValueError("Bilancio non disponibile.")

            df_b = df_b_list[0]
            ce_y = df_b[df_b["Tipo"] == "Conto Economico"]
            att_y = df_b[df_b["Tipo"] == "Attivo"]
            pas_y = df_b[df_b["Tipo"] == "Passivo"]

            if ce_y.empty or att_y.empty or pas_y.empty:
                raise ValueError("Dati incompleti per CE, Attivo o Passivo.")

            row = calcola_kpi(ce_y, att_y, pas_y, benchmark)
            if "Errore" in row:
                raise ValueError(row["Errore"])

            row["Azienda"] = f"{azienda_sel}_{y}"
            heat_data.append(row)

        except Exception as e:
            error_entries.append((y, str(e)))

    for y, msg in error_entries:
        st.error(f"Anno {y}: {msg}")

    if heat_data:
        df_heat = pd.DataFrame(heat_data).set_index("Azienda").T
        df_heat = df_heat.loc[:, ~df_heat.columns.duplicated()]
        st.dataframe(df_heat.style.background_gradient(axis=1))
    else:
        st.info("Nessun dato disponibile per la Heatmap.")

# --- Esportazione ---
df_export = st.session_state.get("df_kpi")
if df_export is not None and not df_export.empty:
    st.subheader("📤 Esporta risultati")

    note = st.text_area("Note personali per il report", key="note_export_modulo_05")
    if st.button("📥 Esporta Report", key="btn_export_modulo_05"):
        grafico_kpi_buf = genera_grafico_kpi(df_export)
        grafico_voci_buf = genera_grafico_voci(st.session_state.get("df_voci", pd.DataFrame()))
        pdf_buf = genera_pdf(df_export, note, grafico_kpi_buf, grafico_voci_buf)

        excel_buf = BytesIO()
        df_export.to_excel(excel_buf, index=False)
        excel_buf.seek(0)

        zip_buf = BytesIO()
        with ZipFile(zip_buf, 'w') as zipf:
            zipf.writestr("report_avanzato.pdf", pdf_buf.getvalue())
            zipf.writestr("kpi_avanzati.xlsx", excel_buf.getvalue())
        zip_buf.seek(0)

        st.download_button("📁 Scarica ZIP", zip_buf.getvalue(), file_name="analisi_avanzata.zip", key="zip_export_modulo_05")
