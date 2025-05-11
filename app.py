# app.py — Cruscotto Finanziario per PMI

import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from utils import (
    default_benchmark, load_benchmark, load_excel,
    calcola_kpi, evidenzia_valori, genera_pdf
)

st.set_page_config(page_title="Cruscotto Finanziario PMI", layout="wide")
st.title("📊 Cruscotto Finanziario per PMI")

# Inputs
demo_mode = st.checkbox("🔍 Usa dati di esempio", value=False)
benchmark_file = st.file_uploader("Carica file CSV benchmark (facoltativo)", type=["csv"])
uploaded_files = None
if not demo_mode:
    uploaded_files = st.file_uploader("Carica file Excel del bilancio", type=["xlsx"], accept_multiple_files=True)

benchmark = load_benchmark(benchmark_file)

# Benchmark editor
st.sidebar.markdown("## ⚙️ Modifica Benchmark")
for kpi in benchmark:
    benchmark[kpi] = st.sidebar.number_input(kpi, value=float(benchmark[kpi]), step=0.1)

tabella_kpi, tabella_voci, bilanci = [], [], {}
kpi_cols = ["EBITDA Margin", "ROE", "ROI", "Current Ratio"]

if demo_mode:
    st.info("Modalità demo attiva: dati fittizi caricati.")
    from demo_data import demo_ce, demo_att, demo_pas
    bilanci = {("Demo Srl", 2022): {"ce": demo_ce, "attivo": demo_att, "passivo": demo_pas}}
else:
    if uploaded_files:
        for f in uploaded_files:
            try:
                ce, att, pas = load_excel(f)
                parts = f.name.replace(".xlsx", "").split("_")
                azienda, anno = (parts + ["Sconosciuta"])[:2]
                bilanci[(azienda, anno)] = {"ce": ce, "attivo": att, "passivo": pas}
            except Exception as e:
                st.error(f"Errore nel file {f.name}: {e}")

# Calcolo KPI
for (azi, yr), dfs in bilanci.items():
    row = calcola_kpi(dfs["ce"], dfs["attivo"], dfs["passivo"], benchmark)
    if "Errore" in row:
        st.warning(f"Errore su {azi} {yr}: {row['Errore']}")
        continue
    row.update({"Azienda": azi, "Anno": str(int(float(yr)))})
    tabella_kpi.append(row)
    tabella_voci.append({
        "Azienda": azi, "Anno": str(int(float(yr))),
        **{k: row[k] for k in row if k not in kpi_cols + ["Indice Sintetico", "Valutazione", "Azienda", "Anno"]}
    })

df_kpi = pd.DataFrame(tabella_kpi)
df_voci = pd.DataFrame(tabella_voci)

# Dashboard
if not df_kpi.empty:
    df_kpi.sort_values(["Azienda", "Anno"], inplace=True)
    st.dataframe(df_kpi.style.format("{:.2f}", na_rep="-").apply(evidenzia_valori, axis=1), use_container_width=True)

    yoy = (
        df_kpi.groupby("Azienda")
        .apply(lambda g: g.sort_values("Anno").set_index("Anno")[kpi_cols + ["Ricavi"]].pct_change().dropna())
        .reset_index()
        .rename(columns={c: f"Δ% {c}" for c in kpi_cols + ["Ricavi"]})
    )
    st.markdown("## 📉 Variazione Percentuale YoY")
    st.dataframe(yoy, use_container_width=True)

    # Confronti
    st.markdown("## 📘 Confronto voci di bilancio")
    asel = st.multiselect("Filtra per anno", df_voci["Anno"].unique(), default=df_voci["Anno"].unique())
    vs = st.multiselect("Voci", [c for c in df_voci.columns if c not in ["Azienda", "Anno"]], default=["Ricavi", "EBIT"])
    if asel and vs:
        dfb = df_voci[df_voci["Anno"].isin(asel)]
        for v in vs:
            fig = px.bar(dfb, x="Azienda", y=v, color="Anno", barmode="group", title=f"{v} per azienda e anno")
            st.plotly_chart(fig, use_container_width=True)

    # Esporta Excel
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df_kpi.to_excel(writer, sheet_name="KPI", index=False)
        df_voci.to_excel(writer, sheet_name="Bilancio", index=False)
        yoy.to_excel(writer, sheet_name="Δ YoY", index=False)
    st.download_button("📥 Scarica Excel", buffer.getvalue(), file_name="cruscotto_finanziario.xlsx")

    # Esporta PDF
    pdf_buf = genera_pdf(df_kpi)
    st.download_button("📄 Scarica PDF", pdf_buf, file_name="report_finanziario.pdf")
