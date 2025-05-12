# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from utils import (
    load_benchmark, load_excel, calcola_kpi, evidenzia_kpi, genera_pdf,
    prepare_kpi_dataframe, prepare_voci_dataframe, calculate_yoy, create_excel_report
)

st.set_page_config(page_title="Cruscotto Finanziario PMI", layout="wide")
st.title("📊 Cruscotto Finanziario per PMI")

demo_mode = st.checkbox("🔍 Usa dati di esempio", value=False)
benchmark_file = st.file_uploader("Carica file CSV benchmark (facoltativo)", type=["csv"])
uploaded_files = None
if not demo_mode:
    uploaded_files = st.file_uploader("Carica uno o più file Excel del bilancio (uno per anno)", type=["xlsx"], accept_multiple_files=True)

benchmark = load_benchmark(benchmark_file)

st.sidebar.markdown("## ⚙️ Modifica Benchmark")
for kpi in benchmark:
    benchmark[kpi] = st.sidebar.number_input(kpi, value=float(benchmark[kpi]), step=0.1)

if demo_mode:
    st.info("Modalità demo: dati di esempio caricati.")
    
    demo_ce = pd.DataFrame({
        "Voce": ["Ricavi", "Utile netto", "EBIT", "Spese operative", "Ammortamenti", "Oneri finanziari"],
        "Importo (€)": [1_200_000, 85_000, 90_000, 200_000, 15_000, 10_000],
    })

    demo_att = pd.DataFrame({
        "Attività": ["Disponibilità liquide"],
        "Importo (€)": [110_000]
    })

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
    tabella_voci.append({"Azienda": azi, "Anno": int(float(yr)), **{k: row[k] for k in row if k not in ["Azienda", "Anno", "Valutazione", "Indice Sintetico"]}})

df_kpi = prepare_kpi_dataframe(tabella_kpi)
df_voci = prepare_voci_dataframe(tabella_voci)

if not df_kpi.empty:
    st.dataframe(df_kpi.style.format("{:.2f}").apply(evidenzia_kpi, axis=1), use_container_width=True)

    df_yoy = calculate_yoy(df_kpi)
    st.markdown("## 📉 Variazione Percentuale YoY dei KPI")
    st.dataframe(df_yoy, use_container_width=True)

    st.markdown("## 📘 Confronto voci di bilancio")
    asel = st.multiselect("Filtra per anno", df_voci["Anno"].unique(), default=df_voci["Anno"].unique())
    vs = st.multiselect("Seleziona voci da confrontare", [c for c in df_voci.columns if c not in ["Azienda", "Anno"]], default=["Ricavi", "EBIT"])
    if asel and vs:
        dfb = df_voci[df_voci["Anno"].isin(asel)]
        for v in vs:
            fig = px.bar(dfb, x="Azienda", y=v, color="Anno", barmode="group", title=f"{v} per azienda e anno")
            st.plotly_chart(fig, use_container_width=True)

    st.download_button("📥 Scarica Excel", create_excel_report(df_kpi, df_voci, df_yoy), file_name="cruscotto_finanziario.xlsx")
    st.download_button("📄 Scarica PDF", genera_pdf(df_kpi), file_name="report_finanziario.pdf")
