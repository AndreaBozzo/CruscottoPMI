
import streamlit as st
st.set_page_config(layout="wide", page_title="Analisi Avanzata")
import pandas as pd
from cruscotto_pmi.charts import genera_radar_kpi, grafico_gauge_indice, genera_heatmap_aziende, kpi_card
from cruscotto_pmi.pdf_generator import genera_super_pdf
from cruscotto_pmi.utils import normalizza_kpi, commento_kpi
from cruscotto_pmi.theme_loader import applica_stile_personalizzato, mostra_logo_sidebar
applica_stile_personalizzato()
mostra_logo_sidebar()


st.title("🔍 Analisi Avanzata Aziendale")

# === Recupero dati da sessione
bilanci = st.session_state.get("bilanci", {})
df_totale = st.session_state.get("df_totale", pd.DataFrame())
df_kpi = normalizza_kpi(df_totale)
benchmark = st.session_state.get("benchmark", {})

# Se df_totale è vuoto o None, ricostruiscilo da bilanci
if df_totale is None or df_totale.empty:
    if bilanci:
        df_totale = pd.concat(
        [dati["completo"] if isinstance(dati, dict) and "completo" in dati else dati
         for dati in bilanci.values()], 
        ignore_index=True
    )

        st.session_state["df_totale"] = df_totale
    else:
        df_totale = pd.DataFrame()
        st.session_state["df_totale"] = df_totale

# PATCH: converte da lungo a largo se necessario
if "KPI" in df_totale.columns and "Valore" in df_totale.columns:
    df_kpi = df_totale.pivot(index=["Azienda", "Anno"], columns="KPI", values="Valore").reset_index()
else:
    df_kpi = df_totale.copy()


# === Validazione bilanci
opzioni = list(bilanci.keys())
if not opzioni:
    st.warning("⚠️ Nessun bilancio disponibile.")
    st.stop()

# === Selezione azienda e anno
azienda_anno = st.selectbox("📌 Seleziona Azienda e Anno", opzioni, format_func=lambda x: f"{x[0]} – {x[1]}")
azienda, anno = azienda_anno

# === Recupero KPI azienda+anno
df_kpi_sel = df_kpi[(df_kpi["Azienda"] == azienda) & (df_kpi["Anno"] == anno)]
if df_kpi_sel.empty:
    st.warning("⚠️ Nessun KPI disponibile per questa azienda.")
    st.stop()

st.markdown(f"### 🧾 Analisi per <b>{azienda}</b> – <b>{anno}</b>", unsafe_allow_html=True)
st.divider()

st.subheader("📌 KPI Sintetici")

kpi_base = [
    "ROE", "ROI", "EBITDA Margin", "Indice Sintetico"
]
df_kpi_long = st.session_state.get("df_kpi", pd.DataFrame())
df_sint = df_kpi_long[
    (df_kpi_long["Azienda"] == azienda) &
    (df_kpi_long["Anno"] == anno) &
    (df_kpi_long["KPI"].isin(kpi_base))
]

if not df_sint.empty:
    valori = df_sint.set_index("KPI")["Valore"].to_dict()
    benchmark_valori = {k: benchmark.get(k) for k in kpi_base}

    col1, col2, col3 = st.columns(3)
    colonne = [col1, col2, col3]

    for i, kpi in enumerate(kpi_base):
        valore = valori.get(kpi)
        if valore is not None:
            col = colonne[i % 3]
            with col:
                st.markdown(kpi_card(
                    titolo=kpi,
                    valore=valore,
                    benchmark=benchmark_valori.get(kpi),
                    inverti_colori=False
                ), unsafe_allow_html=True)
else:
    st.info("📭 Nessun KPI sintetico disponibile.")

# === Radar KPI
with st.container():
    st.subheader("🎯 Radar KPI Avanzati")
    radar = genera_radar_kpi(df_kpi_sel)
    if radar is not None:
        st.plotly_chart(radar, use_container_width=True, key="radar_kpi_avz")
    else:
        st.info("Radar non disponibile.")

# === Osservazioni sintetiche sui KPI
    st.markdown("### 💬 Osservazioni automatiche")

    df_kpi_long = st.session_state.get("df_kpi", pd.DataFrame())

    valutazioni = []
    for row in df_kpi_long.itertuples():
        if row.Azienda == azienda and row.Anno == anno:
            kpi = row.KPI
            valore = row.Valore
            soglia = benchmark.get(kpi)
            if soglia is not None:
                gap = valore - soglia
                valutazioni.append((kpi, gap, valore, soglia))

    top_kpi = sorted(valutazioni, key=lambda x: x[1], reverse=True)[:3]
    flop_kpi = sorted(valutazioni, key=lambda x: x[1])[:3]

    if top_kpi:
        st.success("🔝 KPI sopra la soglia")
        for kpi, _, valore, soglia in top_kpi:
            st.markdown(f"- {commento_kpi(kpi, valore, soglia)}")

    if flop_kpi:
        st.warning("⚠️ KPI sotto la soglia")
        for kpi, _, valore, soglia in flop_kpi:
            st.markdown(f"- {commento_kpi(kpi, valore, soglia)}")

    st.divider()


 # === Gauge KPI strutturali ===
st.divider()
st.subheader("⏱️ Indicatori Strutturali (Gauge)")

 # Prendo il DF long dei KPI dalla sessione
df_kpi_long = st.session_state.get("df_kpi", pd.DataFrame())

 # Definisco gli indicatori da mostrare
indicatori = [
     "Indice liquidità",
     "Indice indebitamento",
     "Equity ratio",
     "Return on Equity"
 ]

 # Filtra solo i KPI strutturali per l'azienda e anno correnti
df_struct = df_kpi_long[
     (df_kpi_long["Azienda"] == azienda) &
     (df_kpi_long["Anno"] == anno) &
     (df_kpi_long["KPI"].isin(indicatori))
 ]

if not df_struct.empty:
     # Costruisco un dict {KPI: Valore}
     valori = df_struct.set_index("KPI")["Valore"].to_dict()
     # Genero il gauge passando il dict dei valori e il benchmark
     fig_gauge = grafico_gauge_indice(valori, benchmark)
     if fig_gauge:
         st.plotly_chart(fig_gauge, use_container_width=True, key="gauge_kpi")
     else:
         st.info("Gauge non disponibile (valori fuori range).")
else:
     st.info("Nessun dato strutturale disponibile per i gauge.")

# === Heatmap Voci di Bilancio tra Aziende Caricate ===
st.divider()
st.subheader("🌡️ Heatmap tra le Aziende Caricate")

# genera la heatmap passando il dict bilanci
fig_heat = genera_heatmap_aziende(bilanci)
if fig_heat is not None:
    st.plotly_chart(fig_heat, use_container_width=True, key="heatmap_voci")
else:
    st.info("Heatmap non disponibile.")


# === Export PDF con notast.subheader("📄 Report di Sintesi PDF")
st.subheader("📄 Report di Sintesi PDF")
with st.expander("📤 Esporta Analisi Avanzata in PDF"):
    nota = st.text_area("📝 Aggiungi una nota al PDF", placeholder="Commenti, valutazioni, osservazioni...")

    if st.button("📄 Esporta Report PDF"):
        from io import BytesIO
        buffer = BytesIO()
        df_yoy = st.session_state.get("df_yoy", pd.DataFrame())
        genera_super_pdf(buffer, df_kpi_sel, benchmark, df_yoy, nota=nota)
        buffer.seek(0)
        st.download_button("📥 Scarica Report PDF", buffer, file_name=f"report_analisi_{azienda}_{anno}.pdf")
