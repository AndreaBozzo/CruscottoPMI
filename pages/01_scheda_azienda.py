
import streamlit as st
import pandas as pd
from cruscotto_pmi.kpi_calculator import calcola_kpi

st.set_page_config(page_title="Scheda Azienda", layout="wide")
st.title("🏢 Scheda Azienda")

# === Recupero dati da sessione
bilanci = st.session_state.get("bilanci", {})

if not bilanci:
    st.warning("⚠️ Nessun bilancio caricato o disponibile.")
    st.stop()

# === Selezione Azienda e Anno
opzioni = list(bilanci.keys())
azienda_anno = st.selectbox("📌 Seleziona Azienda e Anno", opzioni, format_func=lambda x: f"{x[0]} – {x[1]}")

azienda, anno = azienda_anno
df = bilanci.get((azienda, anno), pd.DataFrame())

if df.empty:
    st.warning("⚠️ Bilancio vuoto.")
    st.stop()

# === Separazione per tipo
df_ce = df[df["Tipo"].str.lower() == "conto economico"]
df_att = df[df["Tipo"].str.lower() == "attivo"]
df_pas = df[df["Tipo"].str.lower() == "passivo"]

# === KPI base (ricavi, costi, patrimonio, utile stimato)
ricavi = df_ce[df_ce["Voce"].str.lower().str.contains("ricavi")]["Importo (€)"].sum()
costi = df_ce[df_ce["Voce"].str.lower().str.contains("costi")]["Importo (€)"].sum()
ebitda = ricavi - costi
utile = ebitda * 0.6
attivo = df_att["Importo (€)"].sum()
passivo = df_pas["Importo (€)"].sum()
patrimonio = df_pas[df_pas["Voce"].str.lower().str.contains("patrimonio")]["Importo (€)"].sum()

# === Validazione contenuti
completo = not df_ce.empty and not df_att.empty and not df_pas.empty

# === Badge validazione
with st.container():
    st.markdown(f"### 📋 Stato del Bilancio")
    if completo:
        st.success("✅ Bilancio completo: tutte le sezioni sono presenti.")
    else:
        st.warning("⚠️ Bilancio incompleto: mancano una o più sezioni.")

# === Layout visuale
col1, col2, col3 = st.columns(3)
col1.metric("📈 Ricavi", f"€ {ricavi:,.0f}")
col2.metric("💸 Costi", f"€ {costi:,.0f}")
col3.metric("✅ Utile Stimato", f"€ {utile:,.0f}")

col4, col5, col6 = st.columns(3)
col4.metric("🏦 Totale Attivo", f"€ {attivo:,.0f}")
col5.metric("📉 Totale Passivo", f"€ {passivo:,.0f}")
col6.metric("📊 Patrimonio Netto", f"€ {patrimonio:,.0f}")

# === Box Profilo Impresa
with st.container():
    st.markdown("### 🧠 Profilo Impresa")
    if patrimonio > passivo:
        st.success("🟢 Azienda ben capitalizzata.")
    elif patrimonio > (passivo * 0.5):
        st.info("🟡 Azienda con struttura equilibrata.")
    else:
        st.warning("🔴 Azienda con elevato indebitamento.")

st.divider()

# === Dettaglio voce Conto Economico
with st.expander("🧾 Dettaglio Conto Economico"):
    st.dataframe(df_ce[["Voce", "Importo (€)"]], use_container_width=True)

# === Dettaglio Attivo e Passivo
with st.expander("📘 Stato Patrimoniale"):
    col_att, col_pas = st.columns(2)
    col_att.markdown("#### Attivo")
    col_att.dataframe(df_att[["Voce", "Importo (€)"]], use_container_width=True)
    col_pas.markdown("#### Passivo")
    col_pas.dataframe(df_pas[["Voce", "Importo (€)"]], use_container_width=True)

# === Conclusione introduttiva
st.info("🔍 Puoi ora navigare nei moduli KPI, Confronto, YoY e Analisi Avanzata dal menu a sinistra.")
