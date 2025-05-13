
import streamlit as st
import pandas as pd
import plotly.express as px

st.title("📘 Confronto voci di bilancio")

df_voci = st.session_state.get("df_voci", pd.DataFrame())
if df_voci.empty:
    st.warning("⚠️ Carica prima i bilanci.")
    st.stop()

anni = df_voci["Anno"].unique()
anni_sel = st.multiselect("Filtra per anno", anni, default=list(anni))
voci = [c for c in df_voci.columns if c not in ["Azienda", "Anno"]]
voci_sel = st.multiselect("Seleziona voci", voci, default=["Ricavi", "EBIT"])

dfb = df_voci[df_voci["Anno"].isin(anni_sel)]

for voce in voci_sel:
    fig = px.bar(dfb, x="Azienda", y=voce, color="Anno", barmode="group", title=voce)
    st.plotly_chart(fig, use_container_width=True)
