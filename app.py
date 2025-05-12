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

demo_mode = st.checkbox("🔍 Usa dati di esempio", value=False)
benchmark_file = st.file_uploader("Carica file CSV benchmark (facoltativo)", type=["csv"])
uploaded_files = (
    st.file_uploader("Carica uno o più file Excel del bilancio (uno per anno)",
                     type=["xlsx"], accept_multiple_files=True)
    if not demo_mode else None
)

default_benchmark = {"EBITDA Margin": 15.0, "ROE": 10.0, "ROI": 8.0, "Current Ratio": 1.3}
benchmark = load_benchmark(benchmark_file, default_benchmark)

st.sidebar.markdown("## ⚙️ Modifica Benchmark")
for kpi in benchmark:
    benchmark[kpi] = st.sidebar.number_input(kpi, value=float(benchmark[kpi]), step=0.1)

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
        ("Alpha Srl", 2022): {"ce": demo_ce, "attivo": demo_att, "passivo": demo_pas}
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

for (azi, yr), dfs in bilanci.items():
    row = calcola_kpi(dfs["ce"], dfs["attivo"], dfs["passivo"], benchmark)
    if "Errore" in row:
        st.warning(f"Errore su {azi} {yr}: {row['Errore']}")
        continue
    row.update({"Azienda": azi, "Anno": int(float(yr))})
    tabella_kpi.append(row)
    tabella_voci.append({"Azienda": azi, "Anno": int(float(yr)), **{k: row[k] for k in row if k not in kpi_cols + ["Indice Sintetico", "Valutazione", "Azienda", "Anno"]}})

df_kpi = pd.DataFrame(tabella_kpi)
df_voci = pd.DataFrame(tabella_voci)

if not df_kpi.empty and "Anno" in df_kpi.columns:
    df_kpi["Anno"] = df_kpi["Anno"].astype(int).astype(str)
if not df_voci.empty and "Anno" in df_voci.columns:
    df_voci["Anno"] = df_voci["Anno"].astype(int).astype(str)

st.dataframe(df_kpi)
