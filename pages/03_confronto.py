
import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from zipfile import ZipFile

st.set_page_config(layout="wide", page_title="Confronto Voci di Bilancio")
st.title("📊 Confronto Voci di Bilancio")
st.markdown("Confronta valori economici tra aziende, anni e voci di bilancio. Ogni selezione aggiorna dinamicamente il grafico e i dati esportabili.")

# === Caricamento dati
df_voci = st.session_state.get("df_voci", pd.DataFrame())

if df_voci.empty or "Voce" not in df_voci.columns:
    st.warning("⚠️ La colonna 'Voce' non è disponibile. Assicurati che i KPI siano stati generati correttamente.")
    st.stop()

# === Filtri di selezione
aziende = df_voci["Azienda"].unique().tolist()
anni = sorted(df_voci["Anno"].unique().tolist())
voci_disponibili = sorted(df_voci["Voce"].unique())

azienda_sel = st.multiselect("🏢 Aziende da confrontare", aziende, default=aziende, help="Seleziona una o più aziende")
anno_sel = st.multiselect("📅 Anni da includere", anni, default=anni, help="Puoi confrontare anche più anni contemporaneamente")
voci_sel = st.multiselect("📄 Voci di bilancio da visualizzare", voci_disponibili, default=voci_disponibili[:5], help="Le prime 5 voci vengono selezionate automaticamente")

# === Filtro del DataFrame
df_filtrato = df_voci[
    df_voci["Azienda"].isin(azienda_sel) &
    df_voci["Anno"].isin(anno_sel) &
    df_voci["Voce"].isin(voci_sel)
]

if df_filtrato.empty:
    st.warning("⚠️ Nessun dato disponibile per i filtri selezionati.")
    st.stop()

# === Info dinamica riepilogativa
st.markdown(f"🔍 <b>{len(azienda_sel)}</b> aziende, <b>{len(anno_sel)}</b> anni e <b>{len(voci_sel)}</b> voci selezionate.",
            unsafe_allow_html=True)

# === Badge delle voci selezionate
badges = " ".join([f"<span style='padding:3px 8px;background-color:#eee;border-radius:12px;margin-right:4px'>{v}</span>" for v in voci_sel])
st.markdown(f"🧾 <b>Voci selezionate:</b><br>{badges}", unsafe_allow_html=True)

# === Grafico confronto
fig = px.bar(
    df_filtrato,
    x="Voce",
    y="Importo (€)",
    color="Azienda",
    barmode="group",
    facet_col="Anno",
    title="📊 Confronto per Voce di Bilancio",
    height=500,
)
fig.update_layout(
    xaxis_title="",
    yaxis_title="Importo (€)",
    margin=dict(l=40, r=40, t=80, b=40),
    title_font=dict(size=20, family="Arial"),
    legend_title_text="",
)

st.plotly_chart(fig, use_container_width=True, key="grafico_confronto_voci")
st.divider()

# === Esportazione ZIP
with st.expander("📤 Esporta grafico e dati selezionati"):
    if st.button("📄 Scarica ZIP con Excel + immagine del grafico"):
        buffer = BytesIO()
        with ZipFile(buffer, "w") as zip_file:
            excel_buffer = BytesIO()
            df_filtrato.to_excel(excel_buffer, index=False)
            excel_buffer.seek(0)
            zip_file.writestr("confronto_voci.xlsx", excel_buffer.read())

            img_bytes = fig.to_image(format="png")
            zip_file.writestr("grafico_confronto.png", img_bytes)

        buffer.seek(0)
        st.download_button("📥 Scarica ZIP", buffer, file_name="confronto_voci.zip")
