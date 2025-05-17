
import sys
import os

# Aggiunge src/ al path per import cruscotto_pmi.*
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

import streamlit as st

# Reindirizza alla pagina principale multipagina
st.switch_page("pages/00_home.py")
