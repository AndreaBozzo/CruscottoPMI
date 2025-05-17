
import streamlit as st
import pandas as pd
import plotly.express as px
from cruscotto_pmi.charts import genera_radar_kpi, grafico_gauge_indice, genera_heatmap_aziende
from cruscotto_pmi.pdf_generator import genera_super_pdf

st.set_page_config(layout="wide", page_title="Analisi Avanzata")
st.title("🔍 Analisi Avanzata Aziendale")

# === Controllo dati ===
bilanci = st.session_state.get("bilanci", {})
benchmark = st.session_state.get("benchmark", {})

opzioni = list(bilanci.keys())
if not opzioni:
    st.info("⚠️ Nessun bilancio disponibile. Carica almeno un file o attiva la modalità demo.")
    st.stop()

azienda_anno = st.selectbox("📌 Seleziona Azienda e Anno", opzioni, format_func=lambda x: f"{x[0]} – {x[1]}")
if azienda_anno is None:
    st.info("⚠️ Nessun bilancio selezionato.")
    st.stop()

azienda, anno = azienda_anno
df = bilanci.get((azienda, anno), None)
if df is None:
    st.warning("⚠️ Bilancio non trovato.")
    st.stop()

# === Intestazione dinamica
st.markdown(f"### 🧾 Analisi per <b>{azienda}</b> – <b>{anno}</b>", unsafe_allow_html=True)
st.divider()

# === Radar KPI Avanzati ===
with st.container():
    st.subheader("🎯 Radar KPI Avanzati")
    radar = genera_radar_kpi(df)
    if radar is not None:
        st.plotly_chart(radar, use_container_width=True, key="radar_kpi_avz")
    else:
        st.info("Nessun radar disponibile.")
    st.divider()

# === Gauge Indicatori Strutturali ===
with st.container():
    st.subheader("⏱️ Indicatori Strutturali (Gauge)")
    try:
        gauge = grafico_gauge_indice(df, benchmark)
        if gauge is not None:
            st.plotly_chart(gauge, use_container_width=True, key="gauge_kpi_avz")
        else:
            st.warning("⚠️ Gauge non disponibile: nessun indicatore strutturale calcolabile per questi dati.")

    except Exception as e:
        st.info(f"Errore nella generazione del gauge: {e}")
    st.divider()

# === Heatmap Bilanci Caricati ===
with st.container():
    st.subheader("🌡️ Heatmap tra le Aziende Caricate")
    heatmap = genera_heatmap_aziende(bilanci)
    if heatmap is not None:
        st.plotly_chart(heatmap, use_container_width=True, key="heatmap_avz")
    else:
        st.info("Heatmap non disponibile (dati insufficienti).")
    st.divider()

# === Esportazione
with st.expander("📤 Esporta Analisi Avanzata"):
    nota = st.text_area("📝 Aggiungi una nota al PDF", placeholder="Commenti, valutazioni, approfondimenti...")
    if st.button("📄 Esporta Report PDF"):
        from io import BytesIO
        buffer = BytesIO()
        df_yoy = st.session_state.get("df_yoy", pd.DataFrame())
        genera_super_pdf(buffer, df, benchmark, df_yoy, nota=nota)
        buffer.seek(0)
        st.download_button("📥 Scarica Report PDF", buffer, file_name=f"report_analisi_{azienda}_{anno}.pdf")
