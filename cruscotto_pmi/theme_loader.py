import streamlit as st
from PIL import Image

def applica_stile_personalizzato():
    percorso_css = "assets/theme.css"  # nuovo nome coerente
    try:
        with open(percorso_css) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"⚠️ File di stile non trovato in '{percorso_css}'.")

def mostra_logo_sidebar():
    logo_path = "assets/logo.png"
    try:
        logo = Image.open(logo_path)
        st.sidebar.image(logo, width=180)
    except FileNotFoundError:
        st.sidebar.warning("⚠️ Logo non trovato in 'assets/logo.png'.")

def imposta_layout_base():
    st.set_page_config(page_title="CruscottoPMI", layout="wide")
    applica_stile_personalizzato()
    mostra_logo_sidebar()
