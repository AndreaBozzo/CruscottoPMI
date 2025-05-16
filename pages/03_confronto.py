
import streamlit as st
import pandas as pd
import plotly.express as px
from cruscotto_pmi.utils import genera_pdf, genera_grafico_voci
from io import BytesIO
from zipfile import ZipFile

st.set_page_config(page_title="Confronto Voci", layout="wide")
st.title("📌 Confronto Dettagliato delle Voci di Bilancio")

df_voci = st.session_state.get("df_voci", pd.DataFrame())

if df_voci.empty or not isinstance(df_voci, pd.DataFrame):
    st.warning("⚠️ Carica prima i dati o genera i KPI.")
    st.stop()

if "Voce" not in df_voci.columns:
    st.warning("⚠️ La colonna 'Voce' non è disponibile. Assicurati che i KPI siano stati generati correttamente.")
    st.stop()

# Selezione aziende e anni
aziende = sorted(df_voci["Azienda"].unique())
anni = sorted(df_voci["Anno"].unique())
voci_disponibili = sorted(df_voci["Voce"].unique())

aziende_sel = st.multiselect("Scegli una o più aziende", aziende, default=aziende)
anni_sel = st.multiselect("Scegli uno o più anni", anni, default=anni)
voci_sel = st.multiselect("Voci da confrontare", voci_disponibili, default=voci_disponibili[:5])

df_filtro = df_voci[
    df_voci["Azienda"].isin(aziende_sel) &
    df_voci["Anno"].isin(anni_sel) &
    df_voci["Voce"].isin(voci_sel)
]

if df_filtro.empty:
    st.warning("⚠️ Nessun dato disponibile per il filtro selezionato.")
    st.stop()

# Grafico a barre per confronto
fig = px.bar(
    df_filtro,
    x="Voce",
    y="Importo (€)",
    color="Azienda",
    barmode="group",
    facet_col="Anno",
    text_auto=".2s",
    height=500
)
fig.update_layout(margin=dict(t=40, b=40), showlegend=True)
st.plotly_chart(fig, use_container_width=True)

# Esportazione
st.subheader("📤 Esporta confronto")

note = st.text_area("Note personali per il report", key="note_confronto")
if st.button("📥 Esporta", key="btn_export_confronto"):
    grafico_voci_buf = genera_grafico_voci(df_filtro)
    pdf_buf = genera_pdf(df_filtro, note, grafico_buf=grafico_voci_buf)

    excel_buf = BytesIO()
    df_filtro.to_excel(excel_buf, index=False)
    excel_buf.seek(0)

    zip_buf = BytesIO()
    with ZipFile(zip_buf, 'w') as zipf:
        zipf.writestr("confronto.pdf", pdf_buf.getvalue())
        zipf.writestr("confronto.xlsx", excel_buf.getvalue())
    zip_buf.seek(0)

    st.download_button("📁 Scarica ZIP", zip_buf.getvalue(), file_name="confronto_voci.zip", key="zip_export_confronto")
