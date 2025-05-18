import streamlit as st
import pandas as pd
from cruscotto_pmi.data_loader import load_excel, load_benchmark
from cruscotto_pmi.demo import carica_demo_avanzata

st.set_page_config(page_title="Home – Cruscotto PMI", layout="wide")
st.title("🏠 Cruscotto Finanziario PMI")
st.markdown("""
Benvenuto nel **Cruscotto Finanziario per PMI**.  
- Esplora la **Dashboard KPI**, selezionando l’indicatore di tuo interesse, verificando il trend multi-anno e confrontandolo tra aziende.  
- Attiva la **Modalità Demo** oppure carica i tuoi bilanci per iniziare l’analisi.
""")

st.divider()

# === Modalità Demo ===
with st.container():
    st.subheader("📊 Modalità Demo")
    st.markdown("Prova tutte le funzionalità del Cruscotto senza dati reali: trend, confronto e snapshot KPI.")
    if st.button("🚀 Avvia Demo"):
        carica_demo_avanzata()
        st.success("Modalità demo attivata con successo. Naviga tra i moduli dal menu a sinistra.")
        st.session_state["modalita_demo"] = True
        st.stop()

st.divider()

# === Upload file Excel ===
with st.container():
    st.subheader("🧾 Carica i tuoi bilanci")
    uploaded_files = st.file_uploader(
        "Carica uno o più file Excel (uno per anno/azienda)", 
        type=["xlsx"], 
        accept_multiple_files=True
    )

    if uploaded_files:
        bilanci = {}
        for f in uploaded_files:
            df = load_excel(f)
            if df is not None:
                nome = f.name.replace(".xlsx", "")
                parts = nome.split("_")
                azienda = parts[0]
                anno = parts[1] if len(parts) > 1 else "Anno?"
                bilanci[(azienda, anno)] = df
        st.session_state["bilanci"] = bilanci
        st.session_state["df_totale"] = pd.concat(bilanci.values(), ignore_index=True)
        st.success("✅ Bilanci caricati correttamente.")
        st.session_state["modalita_demo"] = False

st.divider()


# === Benchmark personalizzato globale ===
if not st.session_state.get("modalita_demo", False):
    st.subheader("⚙️ Imposta benchmark di confronto")
    st.markdown("Puoi caricare un file CSV con i tuoi valori di riferimento o usare quelli di default qui sotto.")
    benchmark_file = st.file_uploader("📥 Carica file CSV benchmark (facoltativo)", type=["csv"])

    # Valori di default per tutti i KPI della dashboard
    default_benchmark = {
        "Indice Sintetico":     60.0,
        "EBITDA Margin":        20.0,
        "ROE":                  15.0,
        "ROI":                  12.0,
        "Current Ratio":        1.5,
        "Indice liquidità":     2.0,
        "Indice indebitamento": 1.2,
        "Equity ratio":         0.4,
        "Return on Equity":     10.0
    }

    # Carica eventuale CSV o usa quelli di default
    from cruscotto_pmi.data_loader import load_benchmark
    benchmark = load_benchmark(benchmark_file, default_benchmark)

    # Per ogni KPI, mostra un number_input per personalizzare
    for kpi, val in benchmark.items():
        benchmark[kpi] = st.number_input(
            label=kpi,
            value=float(val),
            step=0.1,
            help=f"Valore di riferimento per {kpi}"
        )

    # Salva il benchmark customizzato in session_state
    st.session_state["benchmark"] = benchmark

# === Footer tecnico ===
with st.expander("ℹ️ Info tecniche"):
    st.markdown("Versione: **v0.6** · Autore: [Andrea Bozzo](https://github.com/AndreaBozzo/CruscottoPMI)")
    st.markdown("Codice sorgente: [GitHub](https://github.com/AndreaBozzo/CruscottoPMI)")
    st.markdown("Powered by **Python + Streamlit**")
