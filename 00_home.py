
import streamlit as st
import pandas as pd
from cruscotto_pmi.data_loader import load_excel, load_benchmark
from cruscotto_pmi.demo import carica_demo_avanzata

st.set_page_config(page_title="Home – Cruscotto PMI", layout="wide")
st.title("🏠 Cruscotto Finanziario PMI")
st.markdown("Benvenuto nel Cruscotto Finanziario per Piccole e Medie Imprese. Esplora l'app in modalità demo oppure carica i tuoi dati per iniziare l'analisi.")

st.divider()

# === Modalità Demo ===
with st.container():
    st.subheader("📊 Modalità Demo")
    st.markdown("Puoi esplorare tutte le funzionalità del Cruscotto senza caricare alcun file. I dati demo simulano due anni di bilancio di una PMI.")
    if st.button("🚀 Avvia Demo"):
        carica_demo_avanzata()
        st.success("Modalità demo attivata con successo. Naviga nei moduli dal menu a sinistra.")
        st.session_state["modalita_demo"] = True
        st.stop()

st.divider()

# === Upload file Excel ===
with st.container():
    st.subheader("🧾 Carica i tuoi bilanci")
    uploaded_files = st.file_uploader("Carica uno o più file Excel (uno per anno/azienda)", type=["xlsx"], accept_multiple_files=True)

    if uploaded_files:
        bilanci = {}
        for file in uploaded_files:
            df = load_excel(file)
            if df is not None:
                nome = file.name.replace(".xlsx", "")
                parts = nome.split("_")
                azienda = parts[0]
                anno = parts[1] if len(parts) > 1 else "Anno?"
                bilanci[(azienda, anno)] = df
        st.session_state["bilanci"] = bilanci
        st.success("✅ Bilanci caricati correttamente.")
        st.session_state["modalita_demo"] = False

st.divider()

# === Benchmark personalizzato ===
if not st.session_state.get("modalita_demo", False):
    st.subheader("⚙️ Imposta benchmark di confronto")
    st.markdown("Puoi caricare un file CSV o usare i valori di default come riferimento per gli indicatori.")
    benchmark_file = st.file_uploader("📥 Carica file CSV benchmark (facoltativo)", type=["csv"])
    default_benchmark = {
        "EBITDA Margin": 15.0,
        "ROE": 10.0,
        "ROI": 8.0,
        "Current Ratio": 1.3
    }
    benchmark = load_benchmark(benchmark_file, default_benchmark)

    for kpi in benchmark:
        benchmark[kpi] = st.number_input(kpi, value=float(benchmark[kpi]), step=0.1)

    st.session_state["benchmark"] = benchmark

st.divider()

# === Footer tecnico
with st.expander("ℹ️ Info tecniche"):
    st.markdown("Versione: **v0.5** · Autore: [Andrea Bozzo](https://github.com/AndreaBozzo/CruscottoPMI)")
    st.markdown("Codice sorgente disponibile su [GitHub](https://github.com/AndreaBozzo/CruscottoPMI)")
    st.markdown("Powered by **Python + Streamlit**")

