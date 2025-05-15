import streamlit as st
import pandas as pd
import os, sys
sys.path.append(os.path.abspath("src"))
from cruscotto_pmi.utils import load_excel, load_benchmark

st.set_page_config(page_title="🏠 Cruscotto Finanziario – Home", layout="wide")

# ---- STILE ----
st.markdown("""
<style>
.hero {
    padding: 2rem;
    background-color: #f5f7fa;
    border-radius: 0.75rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    margin-bottom: 2rem;
}
.hero h1 {
    font-size: 2.5rem;
    color: #333;
    margin-bottom: 0.5rem;
}
.hero p {
    font-size: 1.1rem;
    color: #555;
}
.box {
    padding: 1.5rem;
    border-radius: 0.5rem;
    background-color: #ffffff;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class='hero'>
    <h1>📊 Cruscotto Finanziario per PMI</h1>
    <p>Analizza i bilanci aziendali in modo smart. Carica i tuoi file o esplora i dati demo.</p>
</div>
""", unsafe_allow_html=True)

# ---- INIT SESSION STATE ----
if "bilanci" not in st.session_state:
    st.session_state["bilanci"] = {}
if "benchmark" not in st.session_state:
    st.session_state["benchmark"] = {}
if "df_kpi" not in st.session_state:
    st.session_state["df_kpi"] = pd.DataFrame()
if "df_voci" not in st.session_state:
    st.session_state["df_voci"] = pd.DataFrame()
if "modalita_demo" not in st.session_state:
    st.session_state["modalita_demo"] = False

# ---- FUNZIONE DEMO AVANZATA ----
def carica_demo_avanzata():
    bilanci = {}
    aziende = ["DemoCorp"]
    anni = [2022, 2023]
    for azienda in aziende:
        for anno in anni:
            fattore = 1 if anno == 2022 else 1.12
            ce = pd.DataFrame({
                "Voce": ["Ricavi", "EBIT", "Spese operative", "Utile netto"],
                "Importo (€)": [1000000 * fattore, 150000 * fattore, 700000 * fattore, 80000 * fattore]
            })
            att = pd.DataFrame({
                "Attività": ["Attivo circolante", "Totale attivo"],
                "Importo (€)": [400000 * fattore, 1000000 * fattore]
            })
            pas = pd.DataFrame({
                "Passività e Patrimonio Netto": ["Debiti a breve", "Patrimonio netto", "Totale passivo"],
                "Importo (€)": [200000 * fattore, 400000 * fattore, 1000000 * fattore]
            })
            bilanci[(azienda, anno)] = {"ce": ce, "att": att, "pas": pas}
    st.session_state["bilanci"] = bilanci
    st.session_state["benchmark"] = {
        "EBITDA Margin": 15.0,
        "ROE": 10.0,
        "ROI": 8.0,
        "Current Ratio": 1.3
    }
    st.session_state["modalita_demo"] = True

<<<<<<< HEAD
=======
    # Calcolo YoY demo da bilanci demo
    df_ce_2022 = bilanci[("DemoCorp", 2022)]["ce"]
    df_ce_2023 = bilanci[("DemoCorp", 2023)]["ce"]
    df_yoy = df_ce_2022.merge(df_ce_2023, on="Voce", suffixes=(" 2022", " 2023"))
    df_yoy["Anno Precedente"] = df_yoy["Importo (€) 2022"]
    df_yoy["Anno Attuale"] = df_yoy["Importo (€) 2023"]
    df_yoy["Variazione %"] = ((df_yoy["Anno Attuale"] - df_yoy["Anno Precedente"]) / df_yoy["Anno Precedente"]) * 100
    st.session_state["df_yoy"] = df_yoy[["Voce", "Anno Precedente", "Anno Attuale", "Variazione %"]]
>>>>>>> 0c3ef1b (🚀 Versione stabile - Export completo e layout PDF migliorato)

# ---- UI SELEZIONE MODALITÀ ----
st.markdown("### 🧭 Selezione modalità")
col1, col2 = st.columns(2)

with col1:
    st.markdown("<div class='box'>", unsafe_allow_html=True)
    demo_mode = st.checkbox("🧪 Modalità Demo", value=st.session_state["modalita_demo"])
    st.markdown("""
    <p style='font-size:0.9rem;'>Utilizza dati predefiniti per due anni di DemoCorp. Ideale per test e presentazioni.</p>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='box'>", unsafe_allow_html=True)
    uploaded_files = None
    if not demo_mode:
        uploaded_files = st.file_uploader("📁 Carica file Excel di bilancio (uno per anno)", type=["xlsx"], accept_multiple_files=True)
        st.markdown("""
        <p style='font-size:0.9rem;'>Ogni file deve contenere i fogli: <code>Conto Economico</code>, <code>Attivo</code> e <code>Passivo</code>.</p>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---- LOGICA ----
if demo_mode:
    st.success("🧪 Modalità demo attiva – Dati simulati DemoCorp 2022 e 2023.")
    carica_demo_avanzata()

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
            bilanci[(azi, yr_str)] = {"ce": ce, "att": att, "pas": pas}
        except Exception as e:
            st.error(f"Errore nel file {f.name}: {e}")
    st.session_state["bilanci"] = bilanci
    st.session_state["modalita_demo"] = False
<<<<<<< HEAD

=======
>>>>>>> 0c3ef1b (🚀 Versione stabile - Export completo e layout PDF migliorato)
# ---- BENCHMARK ----
st.markdown("---")
st.markdown("### ✏️ Imposta benchmark di confronto")

benchmark_file = st.file_uploader("📥 Carica file CSV benchmark (facoltativo)", type=["csv"])
default_benchmark = {"EBITDA Margin": 15.0, "ROE": 10.0, "ROI": 8.0, "Current Ratio": 1.3}
benchmark = load_benchmark(benchmark_file, default_benchmark)

for kpi in benchmark:
    benchmark[kpi] = st.number_input(kpi, value=float(benchmark[kpi]), step=0.1)
st.session_state["benchmark"] = benchmark
