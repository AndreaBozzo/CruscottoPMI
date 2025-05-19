import streamlit as st
st.set_page_config(layout="wide", page_title="Confronto Voci di Bilancio")
import pandas as pd
import plotly.express as px
from io import BytesIO
from zipfile import ZipFile
from cruscotto_pmi.theme_loader import applica_stile_personalizzato, mostra_logo_sidebar
applica_stile_personalizzato()
mostra_logo_sidebar()


st.title("📊 Confronto Voci di Bilancio")
st.markdown("Analizza l’andamento delle principali voci tra anni e aziende. Visualizza e confronta valori contabili chiave.")

# === Recupera bilanci dalla sessione
bilanci = st.session_state.get("bilanci", {})
if not bilanci:
    st.warning("⚠️ Nessun bilancio caricato o disponibile in modalità demo.")
    st.stop()

# === Estrai tutti i DataFrame 'completo' o fallback manuale
df_totale = pd.concat(
    [
        entry["completo"]
        if isinstance(entry, dict) and "completo" in entry
        else pd.DataFrame()
        for entry in bilanci.values()
    ],
    ignore_index=True
)

# === Validazione colonne minime
required_cols = ["Azienda", "Anno", "Voce", "Importo (€)"]
if df_totale.empty or not all(col in df_totale.columns for col in required_cols):
    st.warning("⚠️ I dati non contengono le colonne necessarie per il confronto.")
    st.stop()

# === Filtro per tipo (CE, Attivo, Passivo, Tutti)
tipo_sel = st.radio("📂 Tipo di bilancio", ["Conto Economico", "Attivo", "Passivo", "Tutti"], index=3, horizontal=True)
df_voci = df_totale.copy()
if tipo_sel != "Tutti":
    df_voci = df_voci[df_voci["Tipo"] == tipo_sel]

# === Selettori dinamici
aziende_dispo = sorted(df_voci["Azienda"].unique())
anni_dispo = sorted(df_voci["Anno"].unique())
voci_dispo = sorted(df_voci["Voce"].unique())

# Default: top 5 voci più pesanti su totale
top_voci = (
    df_voci.groupby("Voce")["Importo (€)"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
    .index.tolist()
)

st.subheader("📌 Selezione Aziende, Anni e Voci")

col1, col2 = st.columns([2, 3])
with col1:
    aziende_sel = st.multiselect("🏢 Aziende", aziende_dispo, default=aziende_dispo[:1])

with col2:
    anni_sel = st.multiselect("📅 Anni", anni_dispo, default=anni_dispo)

if not aziende_sel or not anni_sel:
    st.warning("⚠️ Seleziona almeno un'azienda e un anno.")
    st.stop()

# Selettore voci sotto
voci_sel = st.multiselect("📄 Voci da confrontare", voci_dispo, default=top_voci)

if not voci_sel:
    st.warning("⚠️ Seleziona almeno una voce.")
    st.stop()

# Suggerimento se troppe selezioni
if len(voci_sel) > 8 or len(anni_sel) > 4:
    st.info("ℹ️ Per una leggibilità ottimale, consigliato selezionare massimo 8 voci o 4 anni.")

st.divider()


# === Filtro finale
df_filtrato = df_voci[
    (df_voci["Azienda"].isin(aziende_sel)) &
    (df_voci["Anno"].isin(anni_sel)) &
    (df_voci["Voce"].isin(voci_sel))
]


if df_filtrato.empty:
    st.warning("⚠️ Nessun dato disponibile per i filtri selezionati.")
    st.stop()

st.divider()

# === Grafico
st.subheader("📊 Confronto tra Voci selezionate")
fig = px.bar(
    df_filtrato,
    x="Voce",
    y="Importo (€)",
    color="Azienda",
    barmode="group",
    facet_col="Anno",
    text_auto='.2s',
    height=500,
)
fig.update_layout(margin=dict(t=60, l=40, r=40, b=40))

st.plotly_chart(fig, use_container_width=True, key="bar_voci")

# === Export ZIP (Excel + PNG)
st.divider()
st.subheader("📦 Esporta risultati")
buffer = BytesIO()
with ZipFile(buffer, "w") as zip_file:
    # Excel
    excel_io = BytesIO()
    df_filtrato.to_excel(excel_io, index=False)
    zip_file.writestr("confronto_voci.xlsx", excel_io.getvalue())

    # PNG del grafico
    try:
        fig_bytes = fig.to_image(format="png")
        zip_file.writestr("grafico_voci.png", fig_bytes)
    except Exception:
        st.warning("⚠️ Impossibile esportare il grafico come immagine (Plotly image engine mancante).")

st.download_button("📥 Scarica confronto (ZIP)", data=buffer.getvalue(), file_name="confronto_voci.zip")
