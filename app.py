import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
import os

# Funzioni placeholder per testing
def load_excel(file):
    ce = pd.DataFrame({
        "Voce": ["Ricavi", "Utile netto", "EBIT", "Spese operative"],
        "Importo (€)": [100000, 10000, 12000, 40000]
    })
    att = pd.DataFrame({"Attività": ["Disponibilità liquide"], "Importo (€)": [50000]})
    pas = pd.DataFrame({"Passività e Patrimonio Netto": ["Debiti a breve", "Patrimonio netto"], "Importo (€)": [20000, 100000]})
    return ce, att, pas

def load_benchmark(file, default_benchmark):
    return default_benchmark

def calcola_kpi(ce, att, pas, benchmark):
    return {
        "EBITDA Margin": 12.5,
        "ROE": 7.8,
        "ROI": 6.2,
        "Current Ratio": 2.5,
        "Indice Sintetico": 9.1,
        "Valutazione": "Ottima solidità ✅",
        "Ricavi": 100000,
        "EBIT": 12000,
        "Spese Operative": 40000,
        "Ammortamenti": 0,
        "Oneri Finanziari": 0,
        "MOL": 60000,
        "Totale Attivo": 50000,
        "Patrimonio Netto": 100000,
        "Liquidità": 50000,
        "Debiti a Breve": 20000
    }

st.set_page_config(page_title="Cruscotto Finanziario PMI", layout="wide")
st.title("📊 Cruscotto Finanziario per PMI")

demo_mode = st.checkbox("🔍 Usa dati di esempio", value=True)
default_benchmark = {"EBITDA Margin": 15.0, "ROE": 10.0, "ROI": 8.0, "Current Ratio": 1.3}
benchmark = load_benchmark(None, default_benchmark)

kpi_cols = ["EBITDA Margin", "ROE", "ROI", "Current Ratio"]
tabella_kpi, tabella_voci, bilanci = [], [], {}

if demo_mode:
    st.info("Modalità demo: dati di esempio caricati.")
    bilanci = {
        ("Alpha Srl", 2022): load_excel(BytesIO()),
        ("Beta Spa", 2023): load_excel(BytesIO())
    }

for (azi, yr), dfs in bilanci.items():
    row = calcola_kpi(*dfs, benchmark)
    row.update({"Azienda": azi, "Anno": str(yr)})
    tabella_kpi.append(row)

df_kpi = pd.DataFrame(tabella_kpi)

if not df_kpi.empty:
    st.markdown("## 📈 Andamento KPI Selezionati")
    anni_sel = st.multiselect("Seleziona anni", df_kpi["Anno"].unique(), default=list(df_kpi["Anno"].unique()))
    kpi_sel = st.multiselect("Seleziona KPI da visualizzare", kpi_cols, default=["EBITDA Margin", "ROE"])

    if anni_sel and kpi_sel:
        df_filtered = df_kpi[df_kpi["Anno"].isin(anni_sel)]
        for kpi in kpi_sel:
            fig = px.line(df_filtered, x="Anno", y=kpi, color="Azienda", markers=True, title=f"Andamento {kpi}")
            st.plotly_chart(fig, use_container_width=True)
