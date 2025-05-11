# app.py - Estratto aggiornato con uso delle funzioni da utils.py

from utils import calcola_kpi_completo, calcola_variazioni_yoy
import streamlit as st
import pandas as pd

# Esempio base di utilizzo
df_kpi = pd.DataFrame()  # Supponiamo che questa venga caricata correttamente prima

kpi_cols = ["EBITDA Margin", "ROE", "ROI", "Current Ratio"]
df_variazioni = calcola_variazioni_yoy(df_kpi, kpi_cols)
if not df_variazioni.empty:
    st.dataframe(df_variazioni)
