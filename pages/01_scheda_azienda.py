import streamlit as st
import pandas as pd
from cruscotto_pmi.theme_loader import imposta_layout_base
from cruscotto_pmi.utils import genera_badge_kpi, commento_kpi

imposta_layout_base()

st.title("🏢 Scheda Azienda")

# === Selezione azienda/anno
st.subheader("📌 Selezione Azienda e Anno")

bilanci = st.session_state.get("bilanci", {})
if not bilanci:
    st.warning("⚠️ Nessun bilancio disponibile.")
    st.stop()

col1, col2 = st.columns([3, 1])
with col1:
    azienda_sel = st.selectbox("Azienda", sorted({k[0] for k in bilanci}))
with col2:
    anni_disponibili = sorted({k[1] for k in bilanci if k[0] == azienda_sel})
    anno_sel = st.selectbox("Anno", anni_disponibili)

st.divider()

# === Estrai dataframe completo
df = bilanci.get((azienda_sel, anno_sel), {}).get("completo", pd.DataFrame()).copy()
if df.empty:
    st.warning("⚠️ Bilancio vuoto o non in formato corretto.")
    st.stop()

# Filtro robusto per alias e variazioni nei nomi
df_ce = df[df["Tipo"].str.lower().str.strip().isin(["conto economico", "ce"])]
df_att = df[df["Tipo"].str.lower().str.strip().isin(["attivo", "attività"])]
df_pas = df[df["Tipo"].str.lower().str.strip().isin(["passivo", "passività"])]


# === Calcolo indicatori base
ricavi = df_ce[df_ce["Voce"].str.lower().str.contains("ricavi")]["Importo (€)"].sum()
costi = df_ce[df_ce["Voce"].str.lower().str.contains("costi")]["Importo (€)"].sum()
ebitda = ricavi - costi
utile = ebitda * 0.6
attivo = df_att["Importo (€)"].sum()
passivo = df_pas["Importo (€)"].sum()
patrimonio = df_pas[df_pas["Voce"].str.lower().str.contains("patrimonio")]["Importo (€)"].sum()

# === Stato bilancio
st.markdown("### 📋 Stato del Bilancio")
if not df_ce.empty and not df_att.empty and not df_pas.empty:
    st.success("✅ Bilancio completo: tutte le sezioni sono presenti.")
else:
    st.warning("⚠️ Bilancio incompleto: mancano una o più sezioni.")

# === Formattazione €
def format_euro(val):
    try:
        return f"€ {val:,.0f}"
    except:
        return "N/D"

# === Indicatori Conto Economico
st.markdown("### 🧾 Conto Economico")
ce1, ce2, ce3 = st.columns(3)
ce1.metric("📈 Ricavi", format_euro(ricavi))
ce2.metric("💸 Costi", format_euro(costi))
ce3.metric("✅ Utile Stimato", format_euro(utile))

# === Stato Patrimoniale
st.markdown("### 📊 Stato Patrimoniale")
sp1, sp2, sp3 = st.columns(3)
sp1.metric("🏦 Totale Attivo", format_euro(attivo))
sp2.metric("📉 Totale Passivo", format_euro(passivo))
sp3.metric("📊 Patrimonio Netto", format_euro(patrimonio))

# === Profilo impresa (valutazione qualitativa)
st.markdown("### 🧠 Profilo Impresa")
if patrimonio > passivo:
    st.success("🟢 Azienda ben capitalizzata.")
elif patrimonio > (passivo * 0.5):
    st.info("🟡 Azienda con struttura equilibrata.")
else:
    st.warning("🔴 Azienda con elevato indebitamento.")

st.divider()

# === KPI Core
st.subheader("🧮 KPI Core – Performance per anno selezionato")

df_kpi = st.session_state.get("df_kpi", pd.DataFrame())
riga = df_kpi[(df_kpi["Azienda"] == azienda_sel) & (df_kpi["Anno"] == anno_sel)]

if not riga.empty:
    kpi_nomi = [
        "ROE", "ROI", "EBITDA Margin", "Current Ratio",
        "Indice liquidità", "Indice indebitamento",
        "Equity ratio", "Return on Equity", "Indice Sintetico"
    ]

    valori_kpi = riga.set_index("KPI")["Valore"].to_dict()
    benchmark = st.session_state.get("benchmark", {})

    col1, col2, col3 = st.columns(3)
    colonne = [col1, col2, col3]
    kpi_visibili = 0

    for i, kpi in enumerate(kpi_nomi):
        col = colonne[i % 3]
        valore = valori_kpi.get(kpi)
        if valore is not None and pd.notna(valore):
            soglia = benchmark.get(kpi)
            if soglia is not None:
                kpi_visibili += 1
                with col:
                    badge_html = genera_badge_kpi(valore, soglia, unita="%", kpi_nome=kpi)
                    st.markdown(badge_html, unsafe_allow_html=True)
                    commento = commento_kpi(kpi, valore, soglia)
                    st.caption(commento)

    if kpi_visibili == 0:
        st.info("🛈 Nessun dato KPI disponibile per questa azienda/anno.")
else:
    st.warning("⚠️ Nessun KPI disponibile per l'anno selezionato.")

# === Dettaglio voce Conto Economico
with st.expander("🧮 Dettaglio Conto Economico"):
    st.dataframe(df_ce[["Voce", "Importo (€)"]], use_container_width=True)

# === Dettaglio Attivo e Passivo
with st.expander("📚 Stato Patrimoniale"):
    col_att, col_pas = st.columns(2)
    col_att.markdown("#### Attivo")
    col_att.dataframe(df_att[["Voce", "Importo (€)"]], use_container_width=True)
    col_pas.markdown("#### Passivo")
    col_pas.dataframe(df_pas[["Voce", "Importo (€)"]], use_container_width=True)

# === Conclusione introduttiva
st.info("🔍 Puoi ora navigare nei moduli KPI, Confronto, YoY e Analisi Avanzata dal menu a sinistra.")
