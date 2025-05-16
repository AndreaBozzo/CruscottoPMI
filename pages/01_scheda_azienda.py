
import streamlit as st
import pandas as pd
from cruscotto_pmi.utils import calcola_kpi

st.set_page_config(page_title="Scheda Azienda", layout="wide")
st.title("🧾 Scheda Azienda")

data_bilanci = list(st.session_state.get("bilanci", {}).values())
benchmark = st.session_state.get("benchmark", {})

bilanci_validi = []
for df in data_bilanci:
    if isinstance(df, pd.DataFrame) and {'Azienda', 'Anno', 'Tipo'}.issubset(df.columns):
        df = df.dropna(subset=['Azienda', 'Anno'])
        if not df.empty:
            bilanci_validi.append(df)

if not bilanci_validi:
    st.warning("⚠️ Nessun bilancio valido trovato.")
    st.stop()

# Estrai aziende
aziende = sorted(set(df['Azienda'].iloc[0] for df in bilanci_validi))
azienda_selezionata = st.selectbox("Seleziona azienda", aziende)

# Estrai anni disponibili per l'azienda selezionata
anni_disponibili = sorted({int(df['Anno'].iloc[0]) for df in bilanci_validi if df['Azienda'].iloc[0] == azienda_selezionata})
anno_selezionato = st.selectbox("📅 Seleziona anno", anni_disponibili, index=len(anni_disponibili)-1)

# Filtra il bilancio corretto
df_azienda = next(
    df for df in bilanci_validi
    if df['Azienda'].iloc[0] == azienda_selezionata and int(df['Anno'].iloc[0]) == anno_selezionato
)

df_ce = df_azienda[df_azienda["Tipo"] == "Conto Economico"]
df_att = df_azienda[df_azienda["Tipo"] == "Attivo"]
df_pas = df_azienda[df_azienda["Tipo"] == "Passivo"]

kpi_dict = calcola_kpi(df_ce, df_att, df_pas, benchmark)

st.markdown(f"### 📌 Dati Sintetici - {azienda_selezionata} ({anno_selezionato})")

if "Errore" in kpi_dict:
    st.error(f"⚠️ {kpi_dict['Errore']}")
else:
    col1, col2, col3 = st.columns(3)

    if "Ricavi" in kpi_dict:
        col1.metric("Fatturato", f"€ {int(kpi_dict['Ricavi']):,}")
    if "EBITDA Margin" in kpi_dict:
        col2.metric("EBITDA %", f"{kpi_dict['EBITDA Margin']}%")
    if "ROE" in kpi_dict:
        col3.metric("ROE", f"{kpi_dict['ROE']}%")

    col1, col2, col3 = st.columns(3)
    if "Current Ratio" in kpi_dict:
        col1.metric("Indice Liquidità", kpi_dict['Current Ratio'])
    if "Indice Sintetico" in kpi_dict:
        col2.metric("Indice Indebitamento", f"{kpi_dict['Indice Sintetico']}")
    if "Spese Operative" in kpi_dict:
        col3.metric("Break Even", f"{kpi_dict['Spese Operative']}")

    with st.expander("💬 Commento automatico"):
        st.write(kpi_dict.get("Valutazione", "Dati non completi."))
