import streamlit as st
st.set_page_config(page_title="Home – Cruscotto PMI", layout="wide")
import pandas as pd
from cruscotto_pmi.data_loader import load_excel, load_benchmark
from cruscotto_pmi.demo import carica_demo_avanzata
from cruscotto_pmi.theme_loader import applica_stile_personalizzato, mostra_logo_sidebar
from cruscotto_pmi.kpi_calculator import calcola_kpi_sessione
from cruscotto_pmi.utils import elabora_bilanci


applica_stile_personalizzato()
mostra_logo_sidebar()

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

# === Helper per anteprima
def mostra_anteprima(df, azienda, anno):
    for tipo in ["CE", "Attivo", "Passivo"]:
        df_tipo = df[df["Tipo"] == tipo]
        if not df_tipo.empty:
            st.markdown(f"**Anteprima – {azienda} ({anno}) – {tipo}:**")
            st.dataframe(df_tipo.head(), use_container_width=True)
        else:
            st.warning(f"⚠️ {tipo} non trovato per {azienda} – {anno}")

# === Upload file Excel ===
with st.container():
    st.subheader("🧾 Carica i tuoi bilanci")
    st.markdown("Carica uno o più file Excel in formato `NomeAzienda_Anno.xlsx`. Ogni file deve contenere almeno i fogli relativi a **Conto Economico**, **Attivo**, e **Passivo**.")

    uploaded_files = st.file_uploader(
        "📥 Trascina qui i file o clicca per selezionare", 
        type=["xlsx"], 
        accept_multiple_files=True
    )

    if uploaded_files:
        file_caricati = {}
        file_ok = 0
        file_ko = 0

        for f in uploaded_files:
            try:
                df, azienda, anno = load_excel(f, debug=True)

                if df is not None and not df.empty:
                    file_caricati[f"{azienda}_{anno}"] = df
                    file_ok += 1
                    st.success(f"✅ Caricato: {azienda} – {anno}")
                    mostra_anteprima(df, azienda, anno)
                else:
                    file_ko += 1
                    st.error(f"❌ Nessun dato utile trovato nel file: {f.name}")
            except Exception as e:
                file_ko += 1
                st.error(f"❌ Errore durante la lettura di `{f.name}`: {e}")

        if file_caricati:
            # 🔄 Salva file raw
            st.session_state["file_caricati"] = file_caricati

            # 🧠 Ricostruisci struttura bilanci per KPI
            bilanci_ristrutturati = elabora_bilanci(file_caricati)
            st.session_state["bilanci"] = bilanci_ristrutturati

            # 📊 Calcola KPI
            benchmark = st.session_state.get("benchmark", {})
            df_kpi = calcola_kpi_sessione(bilanci_ristrutturati, benchmark)
            st.session_state["df_kpi"] = df_kpi

            # 📦 Salva anche il totale (utile per backup o confronto raw)
            df_validi = [df for df in file_caricati.values() if df is not None and not df.empty]
            if df_validi:
                st.session_state["df_totale"] = pd.concat(df_validi, ignore_index=True)

            st.session_state["modalita_demo"] = False

            # ✅ Spostato qui per maggiore coerenza
            st.markdown("➡️ Ora puoi navigare tra i moduli dal menu a sinistra per iniziare l’analisi.")

        st.info(f"📂 Riepilogo: {file_ok} file validi · {file_ko} file con problemi")
        if file_ko > 0:
            st.warning("⚠️ Alcuni file presentano errori o mancano fogli fondamentali.")

# === Benchmark personalizzato globale ===
if not st.session_state.get("modalita_demo", False):
    st.subheader("⚙️ Imposta benchmark di confronto")
    st.markdown("Puoi caricare un file CSV con i tuoi valori di riferimento o usare quelli di default qui sotto.")
    benchmark_file = st.file_uploader("📥 Carica file CSV benchmark (facoltativo)", type=["csv"])

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

    benchmark = load_benchmark(benchmark_file, default_benchmark)

    for kpi, val in benchmark.items():
        benchmark[kpi] = st.number_input(
            label=kpi,
            value=float(val),
            step=0.1,
            help=f"Valore di riferimento per {kpi}"
        )

    st.session_state["benchmark"] = benchmark

# === Footer tecnico ===
with st.expander("ℹ️ Info tecniche"):
    st.markdown("Versione: **v0.7** · Autore: [Andrea Bozzo](https://github.com/AndreaBozzo/CruscottoPMI)")
    st.markdown("Codice sorgente: [GitHub](https://github.com/AndreaBozzo/CruscottoPMI)")
    st.markdown("Powered by **Python + Streamlit**")
