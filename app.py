# Cruscotto Finanziario per PMI – Build aggiornata corretta (demo mode fix)

import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from utils import load_excel, calcola_kpi, load_benchmark

st.set_page_config(page_title="Cruscotto Finanziario PMI", layout="wide")
st.title("📊 Cruscotto Finanziario per PMI")

# ─── INPUT ─────────────────────────────────────────────
demo_mode = st.checkbox("🔍 Usa dati di esempio", value=False)
benchmark_file = st.file_uploader("Carica file CSV benchmark (facoltativo)", type=["csv"])
uploaded_files = (
    st.file_uploader(
        "Carica uno o più file Excel del bilancio (uno per anno)",
        type=["xlsx"], accept_multiple_files=True
    )
    if not demo_mode else None
)

# ─── BENCHMARK DI DEFAULT E EDITOR ─────────────────────
default_benchmark = {"EBITDA Margin": 15.0, "ROE": 10.0, "ROI": 8.0, "Current Ratio": 1.3}
benchmark = load_benchmark(benchmark_file, default_benchmark)

st.sidebar.markdown("## ⚙️ Modifica Benchmark")
for kpi in benchmark:
    benchmark[kpi] = st.sidebar.number_input(kpi, value=float(benchmark[kpi]), step=0.1)

# ─── ELABORAZIONE ─────────────────────────────────────
kpi_cols = ["EBITDA Margin", "ROE", "ROI", "Current Ratio"]
tabella_kpi, tabella_voci, bilanci = [], [], {}

if demo_mode:
    st.info("Modalità demo: dati di esempio caricati.")
    demo_ce = pd.DataFrame({
        "Voce": ["Ricavi", "Utile netto", "EBIT", "Spese operative", "Ammortamenti", "Oneri finanziari"],
        "Importo (€)": [1_200_000, 85_000, 90_000, 200_000, 15_000, 10_000],
    })
    demo_att = pd.DataFrame({"Attività": ["Disponibilità liquide"], "Importo (€)": [110_000]})
    demo_pas = pd.DataFrame({
        "Passività e Patrimonio Netto": ["Debiti a breve", "Patrimonio netto"],
        "Importo (€)": [85_000, 420_000]
    })
    bilanci = {
        ("Alpha Srl", 2022): {"ce": demo_ce, "attivo": demo_att, "passivo": demo_pas},
    }

elif uploaded_files:
    for f in uploaded_files:
        try:
            ce, att, pas = load_excel(f)
            name_parts = f.name.replace(".xlsx", "").split("_")
            azi, yr = (name_parts + ["Sconosciuta"])[0:2]
            bilanci[(azi, yr)] = {"ce": ce, "attivo": att, "passivo": pas}
        except Exception as e:
            st.error(f"Errore nel file {f.name}: {e}")
    st.markdown("## 📘 Confronto voci di bilancio")
    asel = st.multiselect("Filtra per anno", df_voci["Anno"].unique(), default=df_voci["Anno"].unique())
    vs = st.multiselect("Seleziona voci da confrontare", [c for c in df_voci.columns if c not in ["Azienda", "Anno"]], default=["Ricavi", "EBIT"])
    if asel and vs:
        dfb = df_voci[df_voci['Anno'].isin(asel)]
        for v in vs:
            fig = px.bar(dfb, x="Azienda", y=v, color="Anno", barmode="group", title=f"{v} per azienda e anno")
            st.plotly_chart(fig, use_container_width=True)

    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df_kpi.to_excel(writer, sheet_name="KPI", index=False)
        df_voci.to_excel(writer, sheet_name="Bilancio", index=False)
        yoy.to_excel(writer, sheet_name="Δ YoY", index=False)
    st.download_button("📥 Scarica Excel", buffer.getvalue(), file_name="cruscotto_finanziario.xlsx")

    def genera_pdf(df):
        buf = BytesIO()
        c = canvas.Canvas(buf, pagesize=A4)
        width, height = A4
        c.setFont("Helvetica-Bold", 16)
        c.drawString(2*cm, height - 2*cm, "Report Finanziario PMI")
        c.setFont("Helvetica", 10)
        y = height - 3*cm
        for _, row in df.iterrows():
            for key in ["Azienda", "Anno"] + kpi_cols + ["Indice Sintetico", "Valutazione"]:
                c.drawString(2*cm, y, f"{key}: {row[key]}")
                y -= 0.5*cm
            y -= 0.3*cm
            if y < 4*cm:
                c.showPage()
                y = height - 3*cm
        c.save()
        buf.seek(0)
        return buf

    pdf_buf = genera_pdf(df_kpi)
    st.download_button("📄 Scarica PDF", pdf_buf, file_name="report_finanziario.pdf")
