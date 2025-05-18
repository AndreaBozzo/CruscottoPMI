import streamlit as st
import pandas as pd
from io import BytesIO
from zipfile import ZipFile
from cruscotto_pmi.pdf_generator import genera_super_pdf
from cruscotto_pmi.charts import (
    genera_radar_kpi,
    grafico_gauge_indice,
    genera_heatmap_aziende,
    genera_trend_kpi
)
from cruscotto_pmi.utils import normalizza_kpi

st.set_page_config(layout="wide", page_title="Export Report")
st.title("📤 Esporta Report e Analisi")

# === Recupera dati da sessione
df_kpi_long = st.session_state.get("df_kpi", pd.DataFrame())
df_voci = st.session_state.get("df_voci", pd.DataFrame())
df_yoy = st.session_state.get("df_yoy", pd.DataFrame())
df_totale = st.session_state.get("df_totale", pd.DataFrame())
bilanci = st.session_state.get("bilanci", {})
benchmark = st.session_state.get("benchmark", {})

# === Selezione azienda/anno
opzioni = list(bilanci.keys())
if not opzioni:
    st.warning("⚠️ Nessun bilancio disponibile.")
    st.stop()

azienda_anno = st.selectbox("📌 Seleziona Azienda e Anno", opzioni, format_func=lambda x: f"{x[0]} – {x[1]}")
azienda, anno = azienda_anno

# === Selezione contenuti
st.markdown("### ✅ Scegli cosa includere nel PDF")
col1, col2 = st.columns(2)
with col1:
    inc_kpi = st.checkbox("📊 KPI", value=True)
    inc_yoy = st.checkbox("📉 YoY", value=True)
    inc_voci = st.checkbox("📁 Voci Bilancio", value=False)
with col2:
    inc_radar = st.checkbox("🎯 Radar", value=True)
    inc_gauge = st.checkbox("⏱️ Gauge", value=True)
    inc_heatmap = st.checkbox("🌡️ Heatmap", value=True)
    inc_trend = st.checkbox("📈 Trend", value=False)

# === Note PDF
nota = st.text_area("📝 Aggiungi una nota al report (facoltativo)", placeholder="Analisi, sintesi, valutazione...")

# === Bottone export
st.divider()
st.subheader("📦 Genera il pacchetto")
if st.button("📤 Genera ZIP con PDF e Excel"):

    # === Filtra i dati
    df_kpi = df_kpi_long[(df_kpi_long["Azienda"] == azienda) & (df_kpi_long["Anno"] == anno)]
    df_kpi_norm = normalizza_kpi(df_kpi)

    if "KPI" in df_kpi_norm.columns and "Valore" in df_kpi_norm.columns:
        df_kpi_wide = df_kpi_norm.pivot(index=["Azienda", "Anno"], columns="KPI", values="Valore").reset_index()
    else:
        df_kpi_wide = df_kpi_norm.copy()

    if "Azienda" in df_voci.columns:
        df_voci_export = df_voci[df_voci["Azienda"] == azienda]
    else:
        df_voci_export = df_voci.copy()

    df_yoy_export = df_yoy[df_yoy["Azienda"] == azienda] if not df_yoy.empty and "Azienda" in df_yoy.columns else pd.DataFrame()

    # === Genera grafici
    radar_img = []
    gauge_img = []
    heatmap_img = []
    trend_img = []

    if inc_radar and not df_kpi_wide.empty:
        radar_fig = genera_radar_kpi(df_kpi_wide)
        if radar_fig:
            radar_img.append(("radar.png", radar_fig.to_image(format="png")))

    if inc_gauge and not df_kpi_wide.empty:
        row = df_kpi_wide.iloc[0]
        kpi_strutturali = ["Indice liquidità", "Indice indebitamento", "Equity ratio", "Return on Equity"]
        valori = {k: float(row[k]) for k in kpi_strutturali if k in row and pd.notna(row[k])}
        if valori:
            gauge_fig = grafico_gauge_indice(valori, benchmark)
            if gauge_fig:
                gauge_img.append(("gauge.png", gauge_fig.to_image(format="png")))

    if inc_heatmap and bilanci:
        heatmap_fig = genera_heatmap_aziende(bilanci)
        if heatmap_fig:
            heatmap_img.append(("heatmap.png", heatmap_fig.to_image(format="png")))

    if inc_trend and not df_kpi.empty:
        kpi_corrente = df_kpi["KPI"].iloc[0]
        df_trend = df_kpi_long[(df_kpi_long["KPI"] == kpi_corrente) & (df_kpi_long["Azienda"] == azienda)]
        if not df_trend.empty:
            trend_fig = genera_trend_kpi(df_trend, kpi_corrente, benchmark)
            if trend_fig:
                trend_img.append(("trend.png", trend_fig.to_image(format="png")))

    # === Genera Excel + PDF in memoria
    buffer = BytesIO()
    with ZipFile(buffer, "w") as zip_file:
        # Excel
        excel_io = BytesIO()
        with pd.ExcelWriter(excel_io, engine="xlsxwriter") as writer:
            if inc_kpi:
                df_kpi.to_excel(writer, index=False, sheet_name="KPI")
            if inc_voci:
                df_voci_export.to_excel(writer, index=False, sheet_name="Voci")
            if inc_yoy:
                df_yoy_export.to_excel(writer, index=False, sheet_name="YoY")
        zip_file.writestr("report_dati.xlsx", excel_io.getvalue())

        # PDF
        pdf_bytes = genera_super_pdf(
            azienda, anno,
            df_kpi=df_kpi,
            df_voci=df_voci_export,
            df_yoy=df_yoy_export,
            nota=nota,
            radar_img=radar_img,
            gauge_img=gauge_img,
            heatmap_img=heatmap_img,
            trend_img=trend_img
        )
        zip_file.writestr("report_analisi.pdf", pdf_bytes)

    # Download
    st.success("✅ Report generato con successo!")
    st.download_button("📥 Scarica ZIP", data=buffer.getvalue(), file_name=f"report_{azienda}_{anno}.zip")
