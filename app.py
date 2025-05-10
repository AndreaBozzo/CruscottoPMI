# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

st.set_page_config(page_title="Cruscotto Finanziario PMI", layout="wide")
st.title("📊 Cruscotto Finanziario per PMI")

uploaded_files = st.file_uploader("Carica uno o più file Excel del bilancio (uno per anno)", type=["xlsx"], accept_multiple_files=True)
benchmark_file = st.file_uploader("Carica file CSV benchmark (facoltativo)", type=["csv"])

# Benchmark di default
benchmark_default = {
    "EBITDA Margin": 15.0,
    "ROE": 10.0,
    "ROI": 8.0,
    "Current Ratio": 1.3
}

# Leggi benchmark personalizzato se presente
if benchmark_file:
    df_benchmark = pd.read_csv(benchmark_file)
    benchmark = {row['KPI']: row['Valore'] for _, row in df_benchmark.iterrows()}
else:
    benchmark = benchmark_default

if uploaded_files:
    bilanci = {}

    for file in uploaded_files:
        try:
            df_ce = pd.read_excel(file, sheet_name="Conto Economico")
            df_attivo = pd.read_excel(file, sheet_name="Attivo")
            df_passivo = pd.read_excel(file, sheet_name="Passivo")
            anno = file.name.split("_")[0] if "_" in file.name else file.name
            bilanci[anno] = {
                "ce": df_ce,
                "attivo": df_attivo,
                "passivo": df_passivo
            }
        except Exception as e:
            st.error(f"Errore nel file {file.name}: {e}")

    tabella_kpi = []

    for anno, dati in sorted(bilanci.items()):
        st.header(f"📅 Bilancio {anno}")
        df_ce = dati["ce"]
        df_attivo = dati["attivo"]
        df_passivo = dati["passivo"]

        st.subheader("Conto Economico")
        st.dataframe(df_ce)

        st.subheader("Stato Patrimoniale - Attivo")
        st.dataframe(df_attivo)

        st.subheader("Stato Patrimoniale - Passivo")
        st.dataframe(df_passivo)

        # Estrazione valori chiave
        try:
            ricavi = df_ce.loc[df_ce["Voce"] == "Ricavi", "Importo (€)"].values[0]
            utile_netto = df_ce.loc[df_ce["Voce"] == "Utile netto", "Importo (€)"].values[0]
            liquidita = df_attivo.loc[df_attivo["Attività"] == "Disponibilità liquide", "Importo (€)"].values[0]
            debiti_brevi = df_passivo.loc[df_passivo["Passività e Patrimonio Netto"] == "Debiti a breve", "Importo (€)"].values[0]
            current_ratio = round(liquidita / debiti_brevi, 2)

            ebit = df_ce.loc[df_ce["Voce"] == "EBIT", "Importo (€)"].values[0]
            ebitda = ebit + df_ce.loc[df_ce["Voce"] == "Spese operative", "Importo (€)"].values[0]  # approssimazione

            patrimonio_netto = df_passivo.loc[df_passivo["Passività e Patrimonio Netto"] == "Patrimonio netto", "Importo (€)"].values[0]
            totale_attivo = df_attivo["Importo (€)"].sum()

            ebitda_margin = round(ebitda / ricavi * 100, 2)
            roe = round(utile_netto / patrimonio_netto * 100, 2)
            roi = round(ebit / totale_attivo * 100, 2)

            # Valutazione sintetica
            valutazione = "Ottima solidità ✅"
            if any([
                ebitda_margin < 10,
                roe < 5,
                roi < 5,
                current_ratio < 1
            ]):
                valutazione = "⚠️ Attenzione: alcuni indici critici"
            if all([
                ebitda_margin < 10,
                roe < 5,
                roi < 5,
                current_ratio < 1
            ]):
                valutazione = "❌ Situazione critica"

            st.markdown(f"### 🧠 Valutazione sintetica: {valutazione}")

            st.markdown("## 📌 Indicatori di Redditività")
            col1, col2, col3 = st.columns(3)
            col1.metric("EBITDA Margin", f"{ebitda_margin} %", delta=f"{ebitda_margin - benchmark['EBITDA Margin']:.2f}%")
            col2.metric("ROE", f"{roe} %", delta=f"{roe - benchmark['ROE']:.2f}%")
            col3.metric("ROI", f"{roi} %", delta=f"{roi - benchmark['ROI']:.2f}%")
            st.metric("Current Ratio", f"{current_ratio}", delta=f"{current_ratio - benchmark['Current Ratio']:.2f}")

            tabella_kpi.append({
                "Anno": anno,
                "EBITDA Margin": ebitda_margin,
                "Benchmark EBITDA": benchmark["EBITDA Margin"],
                "Δ EBITDA": ebitda_margin - benchmark["EBITDA Margin"],
                "ROE": roe,
                "Benchmark ROE": benchmark["ROE"],
                "Δ ROE": roe - benchmark["ROE"],
                "ROI": roi,
                "Benchmark ROI": benchmark["ROI"],
                "Δ ROI": roi - benchmark["ROI"],
                "Current Ratio": current_ratio,
                "Benchmark Current": benchmark["Current Ratio"],
                "Δ Current": current_ratio - benchmark["Current Ratio"],
                "Valutazione": valutazione
            })

            st.markdown("## 📈 Ricavi e Utile Netto")
            bar_fig = px.bar(
                x=["Ricavi", "Utile Netto"],
                y=[ricavi, utile_netto],
                labels={"x": "Voce", "y": "Importo (€)"},
                color=["Ricavi", "Utile Netto"],
                text=[ricavi, utile_netto]
            )
            st.plotly_chart(bar_fig, use_container_width=True)

            st.markdown("## 🧩 Composizione Attivo e Passivo")
            col1, col2 = st.columns(2)

            fig_attivo = px.pie(df_attivo, names="Attività", values="Importo (€)", title="Attivo")
            col1.plotly_chart(fig_attivo, use_container_width=True)

            fig_passivo = px.pie(df_passivo, names="Passività e Patrimonio Netto", values="Importo (€)", title="Passivo")
            col2.plotly_chart(fig_passivo, use_container_width=True)

        except Exception as e:
            st.warning(f"Errore nell'elaborazione del bilancio {anno}: {e}")

    if tabella_kpi:
        st.markdown("## 🧾 Riepilogo KPI vs Benchmark")
        df_kpi_finale = pd.DataFrame(tabella_kpi)

        def evidenzia_valori(row):
            style = []
            style.append("background-color: #f8d7da" if row["EBITDA Margin"] < 10 else "background-color: #d4edda")
            style.append("")
            style.append("")
            style.append("background-color: #f8d7da" if row["ROE"] < 5 else "background-color: #d4edda")
            style.append("")
            style.append("")
            style.append("background-color: #f8d7da" if row["ROI"] < 5 else "background-color: #d4edda")
            style.append("")
            style.append("")
            style.append("background-color: #f8d7da" if row["Current Ratio"] < 1 else "background-color: #d4edda")
            style.append("")
            style.append("")
            style.append("")
            return style

        styled_df = df_kpi_finale.style.format("{:.2f}").apply(evidenzia_valori, axis=1)
        st.dataframe(styled_df, use_container_width=True)
else:
    st.info("Carica almeno un file Excel per iniziare.")
