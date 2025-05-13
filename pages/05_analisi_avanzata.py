# pages/05_analisi_avanzata.py

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import sys
import os

# ✅ Inserimento dinamico del path alla cartella src/
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, "..", "src"))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from cruscotto_pmi.utils import estrai_aziende_anni_disponibili, filtra_bilanci, calcola_kpi

st.set_page_config(layout="wide")
st.title("📈 Analisi Avanzata")
st.markdown("Analisi finanziaria approfondita: DuPont, Z-Score, radar KPI e altro.")

# --- Recupero dati dal session_state
if "bilanci" not in st.session_state or not st.session_state["bilanci"]:
    st.warning("⚠️ Carica prima almeno un bilancio nella sezione Home.")
    st.stop()

# --- Selezione dinamica
aziende_disponibili, anni_disponibili = estrai_aziende_anni_disponibili(st.session_state["bilanci"])

azienda_sel = st.selectbox("Seleziona azienda", aziende_disponibili)
anno_sel = st.selectbox("Seleziona anno", sorted(anni_disponibili, reverse=True))

# --- Filtro del bilancio selezionato
df_filtrato = filtra_bilanci(st.session_state["bilanci"], azienda_sel, [anno_sel])
df = df_filtrato[0] if df_filtrato else None

if df is None or df.empty:
    st.error("Nessun dato disponibile per l'azienda e l'anno selezionati.")
    st.stop()

st.divider()

# --- Analisi DuPont ---
with st.expander("📊 Analisi DuPont"):
    st.markdown("Scomposizione del ROE: utile netto, margine operativo, rotazione attivi, leva finanziaria.")

    def estrai_valore(df, parole_chiave):
        for parola in parole_chiave:
            match = df[df['Voce'].str.contains(parola, case=False, na=False)]
            if not match.empty:
                return match['Importo (€)'].values[0]
        return None

    utile_netto = estrai_valore(df, ["utile", "risultato d'esercizio"])
    ricavi = estrai_valore(df, ["ricavi", "valore della produzione"])
    attivo_totale = estrai_valore(df, ["totale attivo"])
    patrimonio_netto = estrai_valore(df, ["patrimonio netto"])

    if not all([utile_netto, ricavi, attivo_totale, patrimonio_netto]):
        st.warning("⚠️ Alcune voci necessarie (utile, ricavi, attivo, patrimonio) non sono state trovate.")
    else:
        margine_netto = utile_netto / ricavi
        rotazione_attivi = ricavi / attivo_totale
        leva_finanziaria = attivo_totale / patrimonio_netto
        roe = margine_netto * rotazione_attivi * leva_finanziaria

        labels = ["Margine Netto", "Rotazione Attivi", "Leva Finanziaria", "ROE"]
        valori = [margine_netto, rotazione_attivi, leva_finanziaria, roe]

        fig = go.Figure(data=[go.Bar(
            x=labels,
            y=valori,
            text=[f"{v:.2%}" for v in valori],
            textposition="outside"
        )])
        fig.update_layout(title="Scomposizione ROE (DuPont)", yaxis_tickformat=".0%")
        st.plotly_chart(fig, use_container_width=True)

# --- Z-Score di Altman ---
with st.expander("🧮 Z-Score di Altman"):
    st.markdown("Calcolo dello Z-Score classico per imprese manifatturiere private (formula originale).")

    attivo_circolante = estrai_valore(df, ["attivo circolante"])
    passivo_corrente = estrai_valore(df, ["debiti a breve", "passivo corrente"])
    utile_operativo = estrai_valore(df, ["ebit", "risultato operativo"])
    capitale_totale = attivo_totale
    vendite = ricavi
    capitale_proprio = patrimonio_netto

    if not all([attivo_circolante, passivo_corrente, utile_netto, capitale_totale, vendite, capitale_proprio]):
        st.warning("Dati insufficienti per il calcolo dello Z-Score.")
    else:
        z_score = (
            1.2 * (attivo_circolante - passivo_corrente) / capitale_totale +
            1.4 * utile_netto / capitale_totale +
            3.3 * utile_operativo / capitale_totale +
            0.6 * capitale_proprio / passivo_corrente +
            1.0 * vendite / capitale_totale
        )

        st.metric(label="Altman Z-Score", value=f"{z_score:.2f}")
        if z_score < 1.81:
            st.error("Zona Rossa: alto rischio di insolvenza")
        elif z_score < 2.99:
            st.warning("Zona Grigia: rischio medio")
        else:
            st.success("Zona Sicura: basso rischio")

# --- Radar Chart KPI ---
with st.expander("📉 Radar Chart KPI"):
    st.markdown("Visualizzazione comparata dei KPI su scala normalizzata.")

    kpi_df = calcola_kpi([df])
    if kpi_df is not None and not kpi_df.empty:
        kpi_values = kpi_df.iloc[0].drop("Azienda")
        categories = list(kpi_values.index)
        values = kpi_values.values.tolist()
        values += values[:1]
        categories += categories[:1]

        radar = go.Figure()
        radar.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name=azienda_sel
        ))
        radar.update_layout(polar=dict(radialaxis=dict(visible=True)), showlegend=True)
        st.plotly_chart(radar, use_container_width=True)
    else:
        st.info("KPI non disponibili per l'azienda selezionata.")

# --- Heatmap Indicatori ---
with st.expander("🌡️ Heatmap Indicatori"):
    st.markdown("Panoramica dei principali KPI su scala temporale.")

    bilanci_filtrati = filtra_bilanci(st.session_state["bilanci"], azienda_sel, sorted(anni_disponibili))
    kpi_df_multi = calcola_kpi(bilanci_filtrati)

    if kpi_df_multi is not None and not kpi_df_multi.empty:
        kpi_df_multi.set_index("Azienda", inplace=True)
        heatmap_data = kpi_df_multi.T
        st.dataframe(heatmap_data.style.background_gradient(cmap='RdYlGn', axis=1))
    else:
        st.info("Impossibile generare la heatmap: KPI mancanti.")

