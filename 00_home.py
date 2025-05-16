
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
if "file_caricati" not in st.session_state:
    st.session_state["file_caricati"] = []

def carica_demo_avanzata():
    from cruscotto_pmi.utils import genera_df_yoy

    aziende = ["DemoCorp"]
    anni = [2022, 2023]
    bilanci_dict = {}

    for azienda in aziende:
        for anno in anni:
            f = 1 if anno == 2022 else 1.1

            df = pd.DataFrame([
                ("Ricavi", 1_000_000*f, "Conto Economico"),
                ("EBIT", 150_000*f, "Conto Economico"),
                ("Spese operative", 700_000*f, "Conto Economico"),
                ("Ammortamenti", 50_000*f, "Conto Economico"),
                ("Oneri finanziari", 10_000*f, "Conto Economico"),
                ("Utile netto", 80_000*f, "Conto Economico"),
                ("Disponibilità liquide", 400_000*f, "Attivo"),
                ("Totale attivo", 1_000_000*f, "Attivo"),
                ("Debiti a breve", 200_000*f, "Passivo"),
                ("Patrimonio netto", 400_000*f, "Passivo"),
                ("Totale passivo", 1_000_000*f, "Passivo"),
            ], columns=["Voce", "Importo (€)", "Tipo"])
            df["Azienda"] = azienda
            df["Anno"] = anno

            bilanci_dict[(azienda, anno)] = df

    st.session_state["bilanci"] = bilanci_dict
    st.session_state["modalita_demo"] = True
    st.session_state["file_caricati"] = ["DemoCorp_2022", "DemoCorp_2023"]
    st.session_state["df_voci"] = pd.concat(bilanci_dict.values(), ignore_index=True)

    try:
        df_yoy = genera_df_yoy(
            bilanci_dict[("DemoCorp", 2022)],
            bilanci_dict[("DemoCorp", 2023)],
            2022, 2023,
            azienda="DemoCorp"
        )
        st.session_state["df_yoy"] = df_yoy
    except Exception as e:
        st.session_state["df_yoy"] = pd.DataFrame()
        st.warning(f"⚠️ Errore nella generazione dell'analisi YoY demo: {e}")

# ---- UI SELEZIONE MODALITÀ ----
st.markdown("### 🧭 Selezione modalità")
col1, col2 = st.columns(2)

with col1:
    st.markdown("<div class='box'>", unsafe_allow_html=True)
    demo_mode = st.checkbox("🧪 Modalità Demo", value=st.session_state["modalita_demo"])
    st.markdown("<p style='font-size:0.9rem;'>Utilizza dati predefiniti per due anni di DemoCorp. Ideale per test e presentazioni.</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='box'>", unsafe_allow_html=True)
    uploaded_files = None
    if not demo_mode:
        uploaded_files = st.file_uploader("📁 Carica file Excel di bilancio (uno per anno)", type=["xlsx"], accept_multiple_files=True)
        st.markdown("<p style='font-size:0.9rem;'>Ogni file deve contenere un singolo foglio con le colonne: <code>Tipo</code>, <code>Voce</code>, <code>Importo (€)</code>, <code>Azienda</code>, <code>Anno</code>.</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---- LOGICA ----
if demo_mode:
    st.success("🧪 Modalità demo attiva – Dati simulati DemoCorp 2022 e 2023.")
    carica_demo_avanzata()

elif uploaded_files:
    bilanci_dict = {}
    nomi_file = []

if uploaded_files:
    for f in uploaded_files:
        try:
            df = load_excel(f)
            if df.empty:
                continue

            # Estrazione azienda
            azienda = df["Azienda"].iloc[0] if "Azienda" in df.columns else f.name.replace(".xlsx", "").rsplit("_", 1)[0]

            # Estrazione anno (robusta)
            if "Anno" in df.columns and not df["Anno"].isnull().all():
                anni_presenti = df["Anno"].unique()
                if len(anni_presenti) == 1:
                    anno = int(anni_presenti[0])
                else:
                    st.warning(f"⚠️ File {f.name} contiene più anni: {anni_presenti}. Uso il primo.")
                    anno = int(anni_presenti[0])
            else:
                try:
                    anno = int(f.name.replace(".xlsx", "").rsplit("_", 1)[-1])
                except:
                    anno = -1

            bilanci_dict[(azienda, anno)] = df
            st.write("✅ Salvato bilancio:", (azienda, anno), "righe:", len(df))
            nomi_file.append(f.name)

        except Exception as e:
            st.error(f"Errore nel file {f.name}: {e}")


    # ---- Session State updates
    st.session_state["bilanci"] = bilanci_dict
    st.session_state["modalita_demo"] = False
    st.session_state["file_caricati"] = nomi_file

    if bilanci_dict:
        st.session_state["df_voci"] = pd.concat(bilanci_dict.values(), ignore_index=True)
    else:
        st.session_state["df_voci"] = pd.DataFrame()

    st.session_state["df_yoy"] = pd.DataFrame()  # reset YOY demo residuals

    # ---- YOY generation: find 2 anni consecutivi per stessa azienda
    try:
        from cruscotto_pmi.utils import genera_df_yoy
        aziende_presenti = set(k[0] for k in bilanci_dict)
        for azienda in aziende_presenti:
            anni = sorted([k[1] for k in bilanci_dict if k[0] == azienda])
            if len(anni) >= 2:
                y1, y2 = anni[:2]
                df_yoy = genera_df_yoy(
                    bilanci_dict[(azienda, y1)],
                    bilanci_dict[(azienda, y2)],
                    y1, y2,
                    azienda=azienda
                )
                st.session_state["df_yoy"] = df_yoy
                st.info(f"✅ Analisi YoY generata per {azienda} ({y1}–{y2})")
                break
    except Exception as e:
        st.warning(f"⚠️ Errore nella generazione automatica di df_yoy: {e}")
        st.session_state["df_yoy"] = pd.DataFrame()

# ---- FILE CARICATI VISIBILI ----
if st.session_state.get("file_caricati"):
    st.markdown("### 📂 File attualmente caricati:")
    for nome in st.session_state["file_caricati"]:
        st.write(f"✅ {nome}")

# ---- BENCHMARK ----
st.markdown("---")
st.markdown("### ✏️ Imposta benchmark di confronto")

benchmark_file = st.file_uploader("📥 Carica file CSV benchmark (facoltativo)", type=["csv"])
default_benchmark = {"EBITDA Margin": 15.0, "ROE": 10.0, "ROI": 8.0, "Current Ratio": 1.3}
benchmark = load_benchmark(benchmark_file, default_benchmark)

for kpi in benchmark:
    benchmark[kpi] = st.number_input(kpi, value=float(benchmark[kpi]), step=0.1)
st.session_state["benchmark"] = benchmark
