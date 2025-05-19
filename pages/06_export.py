import streamlit as st
st.set_page_config(layout="wide", page_title="Export Report")
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
from cruscotto_pmi.utils import normalizza_kpi, commento_kpi
from cruscotto_pmi.theme_loader import applica_stile_personalizzato, mostra_logo_sidebar
applica_stile_personalizzato()
mostra_logo_sidebar()

st.title("📤 Esporta Report e Analisi")

# === Recupera dati da sessione
df_kpi_long = st.session_state.get("df_kpi", pd.DataFrame())
df_voci = st.session_state.get("df_voci", pd.DataFrame())
df_yoy = st.session_state.get("df_yoy", pd.DataFrame())
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

st.divider()
st.subheader("📦 Genera il pacchetto")

if st.button("📤 Genera ZIP con PDF e Excel"):
    # === Osservazioni KPI
    osservazioni_kpi = []
    df_kpi_filtered = df_kpi_long[(df_kpi_long["Azienda"] == azienda) & (df_kpi_long["Anno"] == anno)]
    gia_visti = set()
    for row in df_kpi_filtered.itertuples():
        kpi = row.KPI
        if kpi in gia_visti:
            continue
        valore = row.Valore
        soglia = benchmark.get(kpi)
        if soglia is not None and abs(valore - soglia) > 0.1:
            osservazioni_kpi.append(commento_kpi(kpi, valore, soglia))
            gia_visti.add(kpi)


    # === Filtri
    df_kpi = df_kpi_long[
        (df_kpi_long["Azienda"] == azienda) & (df_kpi_long["Anno"] == anno)
    ]

    if inc_voci and "Azienda" in df_voci.columns and "Anno" in df_voci.columns:
        df_voci_export = df_voci[
            (df_voci["Azienda"] == azienda) & (df_voci["Anno"] == anno)
        ]
    else:
        df_voci_export = pd.DataFrame()

    if inc_yoy and "Azienda" in df_yoy.columns and "Anno" in df_yoy.columns:
        df_yoy_export = df_yoy[
            (df_yoy["Azienda"] == azienda) & (df_yoy["Anno"] == anno)
        ]
    else:
        df_yoy_export = pd.DataFrame()

    # === Immagini opzionali in formato (nome, bytes)
    radar_img = []
    if inc_radar:
        try:
            radar_fig = genera_radar_kpi(df_kpi)
            radar_fig.update_layout(margin=dict(l=10,r=10,t=40,b=10), font=dict(size=12))
            radar_img = [("radar.png", radar_fig.to_image(format="png", width=800, height=400))]
        except:
            radar_img = []

    gauge_img = []
    if inc_gauge:
        # genera un gauge per KPI strutturale chiave
        for kpi in ["Current Ratio","Indice liquidità","Equity ratio","Indice indebitamento"]:
            try:
                valore = df_kpi.set_index("KPI")["Valore"].to_dict().get(kpi)
                soglia = benchmark.get(kpi)
                if valore is not None and soglia is not None:
                    fig = grafico_gauge_indice({kpi: valore}, {kpi: soglia})
                    fig.update_layout(margin=dict(l=20,r=20,t=50,b=20), font=dict(size=16))
                    img_bytes = fig.to_image(format="png", width=800, height=300)
                    gauge_img.append((f"gauge_{kpi}.png", img_bytes))
            except:
                continue

    heatmap_img = []
    if inc_heatmap:
        try:
            hm = genera_heatmap_aziende(bilanci)
            heatmap_img = [("heatmap.png", hm.to_image(format="png", width=800, height=400))]
        except:
            heatmap_img = []

    trend_img = []
    if inc_trend:
        try:
            df_tr = df_kpi_long[
                (df_kpi_long["Azienda"] == azienda) & (df_kpi_long["KPI"] == "Indice Sintetico")
            ]
            tr = genera_trend_kpi(df_tr, "Indice Sintetico", benchmark)
            tr.update_layout(margin=dict(l=10,r=10,t=40,b=10), font=dict(size=12))
            trend_img = [("trend.png", tr.to_image(format="png", width=800, height=400))]
        except:
            trend_img = []


    # === Genera PDF
    pdf_bytes = genera_super_pdf(
        azienda,
        anno,
        df_kpi if inc_kpi else pd.DataFrame(),
        benchmark,
        df_voci=df_voci_export,
        df_yoy=df_yoy_export,
        nota=nota,
        osservazioni_kpi=osservazioni_kpi,
        radar_img=radar_img,
        gauge_img=gauge_img,
        heatmap_img=heatmap_img,
        trend_img=trend_img
    )

    # === Excel allegato
    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
        if inc_kpi:
            df_kpi.to_excel(writer, sheet_name="KPI", index=False)
        if inc_voci and not df_voci_export.empty:
            df_voci_export.to_excel(writer, sheet_name="Voci Bilancio", index=False)
        if inc_yoy and not df_yoy_export.empty:
            df_yoy_export.to_excel(writer, sheet_name="YoY", index=False)

    # === ZIP finale
    zip_buffer = BytesIO()
    with ZipFile(zip_buffer, "w") as zip_file:
        zip_file.writestr(f"report_{azienda}_{anno}.pdf", pdf_bytes)
        zip_file.writestr(f"dati_{azienda}_{anno}.xlsx", excel_buffer.getvalue())

    st.download_button(
        "📥 Scarica Pacchetto ZIP",
        zip_buffer.getvalue(),
        file_name=f"analisi_{azienda}_{anno}.zip",
        mime="application/zip"
    )
