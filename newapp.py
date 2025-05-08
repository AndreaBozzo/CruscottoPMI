import streamlit as st
import pandas as pd
import plotlib.express as px
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os

# Configurazione pagina
st.set_page_config(page_title="Cruscotto Finanziario PMI", layout="wide")
st.title("📊 Cruscotto Finanziario per PMI")

# Caricamento file Excel
uploaded_file = st.file_uploader("Carica il file Excel del bilancio", type=["xlsx"])

if uploaded_file:
    # Lettura dei fogli
    df_ce = pd.read_excel(uploaded_file, sheet_name="Conto Economico")
    df_attivo = pd.read_excel(uploaded_file, sheet_name="Attivo")
    df_passivo = pd.read_excel(uploaded_file, sheet_name="Passivo")

    # Mostra i dati caricati
    st.subheader("Conto Economico")
