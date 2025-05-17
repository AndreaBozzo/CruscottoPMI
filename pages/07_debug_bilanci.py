import streamlit as st
import pandas as pd

st.set_page_config(page_title="🛠️ Debug Bilanci", layout="wide")

st.title("🧪 DEBUG – Bilanci Caricati")

bilanci = st.session_state.get("bilanci", {})

if not bilanci:
    st.warning("⚠️ Nessun bilancio presente nello stato della sessione.")
    st.stop()

st.write("📦 Chiavi disponibili in bilanci:")
st.write(list(bilanci.keys()))

# Raggruppamento per azienda
aziende = sorted(set(k[0] for k in bilanci))
azienda_sel = st.selectbox("📌 Seleziona azienda", aziende)

anni_disp = sorted([k[1] for k in bilanci if k[0] == azienda_sel])
anno_sel = st.selectbox("📅 Seleziona anno", anni_disp)

df = bilanci.get((azienda_sel, anno_sel))
if df is not None:
    st.markdown(f"### 📄 Dati per {azienda_sel} - {anno_sel}")
    st.dataframe(df, use_container_width=True)
else:
    st.error("Dati non trovati.")