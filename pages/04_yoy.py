
import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from zipfile import ZipFile
from cruscotto_pmi.pdf_generator import genera_pdf_yoy
from cruscotto_pmi.utils import genera_df_yoy

st.set_page_config(layout="wide", page_title="Analisi YoY")
st.title("📈 Analisi Variazioni Percentuali YoY")
st.markdown("Confronta due anni consecutivi per un'azienda e analizza l'evoluzione delle principali voci economico-finanziarie.")

# === Caricamento dati
df_kpi = st.session_state.get("df_kpi", pd.DataFrame())
df_voci = st.session_state.get("df_voci", pd.DataFrame())

if df_kpi.empty or df_voci.empty:
    st.warning("⚠️ Nessun dato disponibile per l'analisi YoY.")
    st.stop()

# === Selezione Azienda e Anni
aziende = sorted(df_kpi["Azienda"].unique())
azienda_sel = st.selectbox("🏢 Seleziona azienda", aziende)
anni_disp = sorted(df_kpi[df_kpi["Azienda"] == azienda_sel]["Anno"].astype(str).unique())

if len(anni_disp) < 2:
    st.warning("⚠️ Sono necessari almeno due anni per confrontare le variazioni YoY.")
    st.stop()

col1, col2 = st.columns(2)
with col1:
    anno1 = st.selectbox("📅 Anno base", anni_disp[:-1])
with col2:
    anno2 = st.selectbox("📅 Anno di confronto", anni_disp[1:])

if anno1 == anno2:
    st.warning("⚠️ Seleziona due anni differenti per visualizzare la variazione.")
    st.stop()

# === Generazione df_yoy
df_yoy = genera_df_yoy(df_kpi, df_voci, azienda_sel, anno1, anno2)
if df_yoy.empty:
    st.warning("⚠️ Nessuna variazione calcolabile per gli anni selezionati.")
    st.stop()

st.session_state["df_yoy"] = df_yoy

# === Info dinamica riepilogativa
st.markdown(f"🔍 Confronto per <b>{azienda_sel}</b> tra <b>{anno1}</b> e <b>{anno2}</b>", unsafe_allow_html=True)
st.divider()

# === Visualizzazione Tabella
with st.container():
    st.subheader("📋 Tabella variazioni %")
    # Fix fondamentale: assicuriamoci che la colonna sia numerica
    df_yoy["Variazione (%)"] = pd.to_numeric(df_yoy["Variazione (%)"], errors="coerce")
    st.dataframe(df_yoy.style.format({"Variazione (%)": "{:+.2f}%"}), use_container_width=True)
    st.divider()

# === Grafico variazioni YoY
fig = px.bar(
    df_yoy,
    x="Voce",
    y="Variazione (%)",
    color="Variazione (%)",
    color_continuous_scale="RdYlGn",
    title="📊 Variazioni percentuali YoY",
    height=500
)
fig.update_layout(
    margin=dict(l=40, r=40, t=60, b=40),
    coloraxis_colorbar=dict(title="%"),
    xaxis_tickangle=-45
)

st.plotly_chart(fig, use_container_width=True, key="grafico_yoy")
st.divider()

# === Esportazione risultati
with st.expander("📤 Esporta risultati YoY"):
    nota = st.text_area("✏️ Inserisci una nota per il report", placeholder="Osservazioni, considerazioni, risultati salienti...")

    if st.button("📄 Esporta in ZIP"):
        buffer = BytesIO()
        with ZipFile(buffer, "w") as zip_file:
            excel_buffer = BytesIO()
            df_yoy.to_excel(excel_buffer, index=False)
            excel_buffer.seek(0)
            zip_file.writestr("analisi_yoy.xlsx", excel_buffer.read())

            pdf_buffer = BytesIO()
            genera_pdf_yoy(pdf_buffer, df_yoy, azienda_sel, anno1, anno2, nota)
            pdf_buffer.seek(0)
            zip_file.writestr("report_yoy.pdf", pdf_buffer.read())

        buffer.seek(0)
        st.download_button("📥 Scarica ZIP", buffer, file_name="report_yoy.zip")
