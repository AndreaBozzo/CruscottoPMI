import streamlit as st
import pandas as pd
from cruscotto_pmi.kpi_calculator import calcola_kpi

st.set_page_config(page_title="Scheda Azienda", layout="wide")
st.title("🏢 Scheda Azienda")

bilanci = st.session_state.get("bilanci", {})

if not bilanci:
    st.warning("⚠️ Nessun bilancio disponibile.")
    st.stop()

# Selettori azienda/anno
azienda_sel = st.selectbox("Azienda:", sorted({k[0] for k in bilanci}))
anno_sel = st.selectbox("Anno:", sorted({k[1] for k in bilanci if k[0] == azienda_sel}))

# Recupera il dataframe completo
df = bilanci.get((azienda_sel, anno_sel), {}).get("completo", pd.DataFrame()).copy()

if df.empty:
    st.warning("⚠️ Bilancio vuoto o non in formato corretto.")
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

# === Funzione di formattazione sicura per Euro
def format_euro(val):
    try:
        return f"€ {val:,.0f}"
    except:
        return "N/D"

# === Layout visuale
col1, col2, col3 = st.columns(3)
col1.metric("📈 Ricavi", format_euro(ricavi))
col2.metric("💸 Costi", format_euro(costi))
col3.metric("✅ Utile Stimato", format_euro(utile))

col4, col5, col6 = st.columns(3)
col4.metric("🏦 Totale Attivo", format_euro(attivo))
col5.metric("📉 Totale Passivo", format_euro(passivo))
col6.metric("📊 Patrimonio Netto", format_euro(patrimonio))

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

st.divider()
st.subheader("🧮 KPI Core – Performance per anno selezionato")

from style import kpi_card, PALETTE

# Prendo il DataFrame long dei KPI dalla sessione
df_kpi = st.session_state.get("df_kpi", pd.DataFrame())

# Filtra le righe per azienda_sel e anno_sel (definiti dai tuoi select box)
riga = df_kpi[
    (df_kpi["Azienda"] == azienda_sel) &
    (df_kpi["Anno"] == anno_sel)
]

if not riga.empty:
    # Ordine e icone delle card
    kpi_nomi = [
        "ROE", "ROI", "EBITDA Margin", "Current Ratio",
        "Indice liquidità", "Indice indebitamento",
        "Equity ratio", "Return on Equity", "Indice Sintetico"
    ]
    icone = {
        "ROE": "📈", "ROI": "💹", "EBITDA Margin": "📊", "Current Ratio": "📏",
        "Indice liquidità": "💧", "Indice indebitamento": "💣",
        "Equity ratio": "⚖️", "Return on Equity": "📈", "Indice Sintetico": "⭐"
    }

    # Creo un dizionario {KPI: Valore}
    valori_kpi = riga.set_index("KPI")["Valore"].to_dict()

    # Griglia 3×3 di card
    for i in range(0, len(kpi_nomi), 3):
        cols = st.columns(3)
        for j, nome in enumerate(kpi_nomi[i:i+3]):
            with cols[j]:
                val = valori_kpi.get(nome)
                if val is not None and pd.notna(val):
                    colore = (
                        PALETTE["positivo"] if val > 0 else
                        PALETTE["negativo"] if val < 0 else
                        PALETTE["neutro"]
                    )
                    st.markdown(
                        kpi_card(nome, f"{val:.2f}", colore, icona=icone[nome]),
                        unsafe_allow_html=True
                    )
                else:
                    st.warning(f"🛈 {nome} non disponibile")
else:
    st.info("🛈 Nessun dato KPI disponibile per questa azienda/anno.")


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
