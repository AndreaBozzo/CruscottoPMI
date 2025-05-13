
import streamlit as st
import pandas as pd

st.title("📈 Analisi YoY")

df_kpi = st.session_state.get("df_kpi", pd.DataFrame())
if df_kpi.empty:
    st.warning("⚠️ Carica prima i KPI nella pagina precedente.")
    st.stop()

aziende = sorted(df_kpi["Azienda"].unique())
aziende_sel = st.multiselect("Seleziona aziende", aziende, default=aziende)

kpi_base = ["EBITDA Margin", "ROE", "ROI", "Current Ratio", "Indice Sintetico", "Ricavi"]
kpi_scelti = st.multiselect("Scegli KPI da confrontare", options=kpi_base, default=kpi_base)

for azi in aziende_sel:
    dati = df_kpi[df_kpi["Azienda"] == azi].sort_values("Anno")
    if len(dati) < 2:
        continue
    yoy = dati.set_index("Anno")[kpi_scelti].pct_change().dropna().reset_index()
    yoy.columns = ["Anno"] + [f"Δ% {k}" for k in kpi_scelti]
    st.subheader(f"📊 Variazione % – {azi}")
    st.dataframe(yoy, use_container_width=True)
