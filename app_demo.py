
# app.py

import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

from utils import render_voci_dashboard

# Impostazioni pagina
st.set_page_config(page_title="Cruscotto Finanziario PMI", layout="wide")
st.title("📊 Cruscotto Finanziario per PMI")

# Simulazione minima per test struttura
demo_mode = True

if demo_mode:
    st.info("Modalità demo attiva")
    df_voci = pd.DataFrame([
        {"Azienda": "Alpha Srl", "Anno": "2022", "Ricavi": 1200000, "EBIT": 90000, "Oneri Finanziari": 10000},
        {"Azienda": "Beta Spa", "Anno": "2022", "Ricavi": 1750000, "EBIT": 130000, "Oneri Finanziari": 12000},
        {"Azienda": "Alpha Srl", "Anno": "2023", "Ricavi": 1400000, "EBIT": 110000, "Oneri Finanziari": 8000},
        {"Azienda": "Beta Spa", "Anno": "2023", "Ricavi": 1850000, "EBIT": 150000, "Oneri Finanziari": 9000},
    ])

    render_voci_dashboard(df_voci)
else:
    st.warning("⚠️ Caricamento dati reali non ancora implementato.")
