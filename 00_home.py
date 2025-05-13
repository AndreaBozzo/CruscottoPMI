import sys, os
sys.path.append(os.path.abspath('src'))


import streamlit as st
import pandas as pd
from cruscotto_pmi.utils import load_excel, load_benchmark

st.title("🏠 Cruscotto PMI – Home")

st.markdown("### 📁 Caricamento dati")

# Session state init
if "bilanci" not in st.session_state:
    st.session_state["bilanci"] = {}
if "benchmark" not in st.session_state:
    st.session_state["benchmark"] = {}
if "df_kpi" not in st.session_state:
    st.session_state["df_kpi"] = pd.DataFrame()
if "df_voci" not in st.session_state:
    st.session_state["df_voci"] = pd.DataFrame()

demo_mode = st.checkbox("🔍 Usa dati di esempio", value=False)
benchmark_file = st.file_uploader("📥 Carica file CSV benchmark (facoltativo)", type=["csv"])
uploaded_files = (
    st.file_uploader("📥 Carica file Excel del bilancio (uno per anno)", type=["xlsx"], accept_multiple_files=True)
    if not demo_mode else None
)

default_benchmark = {"EBITDA Margin": 15.0, "ROE": 10.0, "ROI": 8.0, "Current Ratio": 1.3}
benchmark = load_benchmark(benchmark_file, default_benchmark)

st.sidebar.markdown("### ✏️ Modifica Benchmark")
for kpi in benchmark:
    benchmark[kpi] = st.sidebar.number_input(kpi, value=float(benchmark[kpi]), step=0.1)

st.session_state["benchmark"] = benchmark

# DEMO mode
if demo_mode:
    st.info("🧪 Modalità demo attiva – Dati simulati per due aziende su due anni.")
    def gen_dati_demo(nome, base, moltiplicatore):
        ce = pd.DataFrame({
            "Voce": ["Ricavi", "Utile netto", "EBIT", "Spese operative", "Ammortamenti", "Oneri finanziari"],
            "Importo (€)": base
        })
        att = pd.DataFrame({"Attività": ["Disponibilità liquide"], "Importo (€)": [base[0] * 0.12]})
        pas = pd.DataFrame({
            "Passività e Patrimonio Netto": ["Debiti a breve", "Patrimonio netto"],
            "Importo (€)": [base[0] * 0.07, base[0] * 0.4]
        })
        ce_2022 = ce.copy()
        ce_2021 = ce.copy(); ce_2021["Importo (€)"] *= moltiplicatore
        att_2022 = att.copy()
        att_2021 = att.copy(); att_2021["Importo (€)"] *= moltiplicatore
        pas_2022 = pas.copy()
        pas_2021 = pas.copy(); pas_2021["Importo (€)"] *= moltiplicatore
        return {
            (nome, "2022"): {"ce": ce_2022, "attivo": att_2022, "passivo": pas_2022},
            (nome, "2021"): {"ce": ce_2021, "attivo": att_2021, "passivo": pas_2021},
        }

    bilanci = {}
    bilanci.update(gen_dati_demo("Alpha Srl", [1_500_000, 120_000, 180_000, 300_000, 30_000, 15_000], 0.85))
    bilanci.update(gen_dati_demo("Beta Spa", [950_000, 70_000, 95_000, 220_000, 12_000, 8_000], 0.90))
    st.session_state["bilanci"] = bilanci

elif uploaded_files:
    bilanci = {}
    for f in uploaded_files:
        try:
            ce, att, pas = load_excel(f)
            name_parts = f.name.replace(".xlsx", "").split("_")
            azi = name_parts[0] if len(name_parts) >= 1 else "Sconosciuta"
            try:
                yr_str = str(int(float(name_parts[-1]))) if name_parts[-1].isdigit() else "AnnoNonValido"
            except:
                yr_str = "AnnoNonValido"
            bilanci[(azi, yr_str)] = {"ce": ce, "attivo": att, "passivo": pas}
        except Exception as e:
            st.error(f"Errore nel file {f.name}: {e}")
    st.session_state["bilanci"] = bilanci
