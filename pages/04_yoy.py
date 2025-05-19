import streamlit as st
st.set_page_config(layout="wide", page_title="Analisi YoY")
import pandas as pd
import plotly.express as px
from cruscotto_pmi.theme_loader import applica_stile_personalizzato, mostra_logo_sidebar
applica_stile_personalizzato()
mostra_logo_sidebar()

st.title("📉 Analisi Variazioni Percentuali YoY")
st.markdown("Confronta le variazioni % anno su anno per ogni voce contabile selezionata.")

# === Recupero dati da sessione
df_kpi = st.session_state.get("df_kpi", pd.DataFrame())
df_voci = st.session_state.get("df_voci", pd.DataFrame())

# === Fallback se df_voci mancante
if df_voci.empty and "bilanci" in st.session_state:
    bilanci = st.session_state["bilanci"]
    df_voci = pd.concat(
        [dati["completo"] for dati in bilanci.values() if isinstance(dati, dict) and "completo" in dati],
        ignore_index=True
    )
    st.session_state["df_voci"] = df_voci

if df_voci.empty:
    st.warning("⚠️ Nessun dato disponibile per analisi YoY.")
    st.stop()

st.subheader("📌 Selezione Azienda, Anni e Soglie")

aziende_disponibili = sorted(df_voci["Azienda"].unique())
col1, col2 = st.columns([3, 2])

with col1:
    azienda_sel = st.selectbox("🏢 Azienda", aziende_disponibili)

with col2:
    anni_disponibili = sorted(df_voci[df_voci["Azienda"] == azienda_sel]["Anno"].unique())
    anni_sel = st.multiselect("📅 Anni da confrontare", anni_disponibili, default=anni_disponibili[-2:])

if len(anni_sel) < 2:
    st.warning("⚠️ Seleziona almeno due anni per confrontare le variazioni YoY.")
    st.stop()

# Parametri soglie
col1, col2 = st.columns([1, 1])
with col1:
    soglia = st.number_input("🎯 Soglia variazione (%)", value=5.0, min_value=0.0, max_value=100.0, step=0.5)
with col2:
    max_voci = st.slider("🔝 Top N voci", min_value=3, max_value=20, value=10)

st.divider()

# === Calcolo YoY %
df = df_voci[df_voci["Azienda"] == azienda_sel]
df = df[df["Anno"].isin(anni_sel)]

# Raggruppa per Anno + Voce
pivot = df.pivot_table(index="Voce", columns="Anno", values="Importo (€)", aggfunc="sum")
pivot = pivot.sort_index(axis=1)  # ordina gli anni

# Calcolo variazione % tra anni consecutivi
df_yoy = pd.DataFrame()
for i in range(1, len(pivot.columns)):
    anno_prev = pivot.columns[i - 1]
    anno_curr = pivot.columns[i]
    delta = (pivot[anno_curr] - pivot[anno_prev]) / pivot[anno_prev] * 100
    delta = delta.replace([float("inf"), -float("inf")], pd.NA).dropna()
    temp = pd.DataFrame({
        "Voce": delta.index,
        "Anno Iniziale": anno_prev,
        "Anno Finale": anno_curr,
        "Variazione %": delta.values
    })
    df_yoy = pd.concat([df_yoy, temp], ignore_index=True)

# Filtra per soglia e top N
df_yoy["Assoluto"] = df_yoy["Variazione %"].abs()
df_yoy = df_yoy[df_yoy["Assoluto"] >= soglia]
df_yoy = df_yoy.sort_values("Assoluto", ascending=False).head(max_voci)

if df_yoy.empty:
    st.info("ℹ️ Nessuna variazione significativa trovata con la soglia impostata.")
    st.stop()

# === Tabella
st.dataframe(df_yoy.drop(columns="Assoluto"), use_container_width=True)

st.divider()

# === Grafico
st.subheader("📊 Grafico delle Variazioni Percentuali YoY")
fig = px.bar(
    df_yoy,
    x="Voce",
    y="Variazione %",
    color="Anno Finale",
    barmode="group",
    text_auto=".1f",
    height=500,
)
fig.update_layout(
    yaxis_title="Variazione % YoY",
    xaxis_title="Voce",
    margin=dict(t=60, l=40, r=40, b=40)
)

# Linea benchmark se desiderata
if soglia > 0:
    fig.add_shape(type="line", x0=-0.5, x1=len(df_yoy["Voce"].unique())-0.5,
                  y0=soglia, y1=soglia, line=dict(dash="dot", color="green"))
    fig.add_shape(type="line", x0=-0.5, x1=len(df_yoy["Voce"].unique())-0.5,
                  y0=-soglia, y1=-soglia, line=dict(dash="dot", color="red"))
    fig.add_annotation(x=0, y=soglia, text="Soglia +", showarrow=False, yshift=10, font=dict(size=10))
    fig.add_annotation(x=0, y=-soglia, text="Soglia –", showarrow=False, yshift=-10, font=dict(size=10))

st.plotly_chart(fig, use_container_width=True, key="grafico_yoy")
