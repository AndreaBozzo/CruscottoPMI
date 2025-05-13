
import streamlit as st
import pandas as pd
from cruscotto_pmi.utils import calcola_kpi

st.title("📊 Dashboard KPI")

bilanci = st.session_state.get("bilanci", {})
benchmark = st.session_state.get("benchmark", {})

if not bilanci:
    st.warning("⚠️ Carica prima i bilanci dalla Home.")
    st.stop()

tabella_kpi, tabella_voci = [], []

for (azi, yr), dfs in bilanci.items():
    row = calcola_kpi(dfs["ce"], dfs["attivo"], dfs["passivo"], benchmark)
    if "Errore" in row:
        st.warning(f"Errore su {azi} {yr}: {row['Errore']}")
        continue
    row.update({"Azienda": azi, "Anno": int(float(yr))})
    tabella_kpi.append(row)
    tabella_voci.append({
        "Azienda": azi, "Anno": int(float(yr)),
        **{k: row[k] for k in row if k not in benchmark and k not in ["Indice Sintetico", "Valutazione", "Azienda", "Anno"]}
    })

df_kpi = pd.DataFrame(tabella_kpi)
df_voci = pd.DataFrame(tabella_voci)
df_kpi["Anno"] = df_kpi["Anno"].astype(str)
df_voci["Anno"] = df_voci["Anno"].astype(str)

st.session_state["df_kpi"] = df_kpi
st.session_state["df_voci"] = df_voci

aziende = sorted(df_kpi["Azienda"].unique())
anni = sorted(df_kpi["Anno"].unique())

azienda_sel = st.selectbox("Seleziona azienda", aziende)
anno_sel = st.selectbox("Seleziona anno", anni)

kpi_da_mostrare = {
    "EBITDA Margin": "%", "ROE": "%", "ROI": "%", "Current Ratio": "", "Indice Sintetico": "/100"
}

kpi_scelti = st.multiselect(
    "Scegli i KPI da visualizzare",
    options=list(kpi_da_mostrare.keys()),
    default=list(kpi_da_mostrare.keys())
)

riga = df_kpi[(df_kpi["Azienda"] == azienda_sel) & (df_kpi["Anno"] == anno_sel)]
if not riga.empty:
    st.subheader(f"📈 KPI – {azienda_sel} {anno_sel}")
    col1, col2 = st.columns(2)
    for i, kpi in enumerate(kpi_scelti):
        valore = riga[kpi].values[0]
        unita = kpi_da_mostrare[kpi]
        colore = "🟢" if valore > 10 else "🟡" if valore > 5 else "🔴"
        col = col1 if i % 2 == 0 else col2
        col.markdown(f"**{colore} {kpi}:** `{valore:.2f} {unita}`")
