# pages/05_analisi_avanzata.py

import sys
import os

# Configura in modo dinamico PYTHONPATH per importare modulo cruscotto_pmi
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(BASE_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from cruscotto_pmi.utils import estrai_aziende_anni_disponibili, filtra_bilanci, calcola_kpi

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Configurazione pagina
st.set_page_config(layout="wide")

# Sidebar per navigazione
st.sidebar.title("📊 Analisi Avanzata")
sezione = st.sidebar.radio(
    "Seleziona sezione",
    ("DuPont", "Z-Score", "Radar KPI", "Heatmap")
)

# Verifica struttura bilanci
bilanci = st.session_state.get("bilanci")
if not isinstance(bilanci, dict) or not bilanci:
    st.sidebar.error("⚠️ La struttura dei bilanci non è valida. Caricali di nuovo in Home.")
    st.stop()

# Avviso su dati demo
for (azienda, anno) in bilanci.keys():
    if azienda.lower().startswith("demo"):
        st.sidebar.warning("⚠️ I dati demo potrebbero non supportare completamente il modulo Analisi Avanzata. Considera di caricare bilanci reali.")
        break

# Selezione azienda/anno
aziende_disponibili, anni_disponibili = estrai_aziende_anni_disponibili(bilanci)
azienda_sel = st.sidebar.selectbox("Azienda", aziende_disponibili)
anno_sel = st.sidebar.selectbox("Anno", sorted(anni_disponibili, reverse=True))

# Filtra bilancio
try:
    bilanci_selezionati = filtra_bilanci(bilanci, azienda_sel, [anno_sel])
    if not isinstance(bilanci_selezionati, list):
        raise TypeError("filtra_bilanci non ha restituito una lista")
    if not bilanci_selezionati:
        raise IndexError
    bilancio = bilanci_selezionati[0]
except IndexError:
    st.error(f"Nessun bilancio trovato per {azienda_sel} anno {anno_sel}.")
    st.stop()
except Exception as e:
    st.error(f"Errore in filtraggio bilanci: {e}")
    st.stop()

# Determina DataFrame unico o dict di DataFrame
if isinstance(bilancio, pd.DataFrame):
    ce = att = pas = bilancio
else:
    ce = bilancio.get("ce")
    att = bilancio.get("att")
    pas = bilancio.get("pas")

# Funzione di estrazione valori aggiornata con st.error per diagnosi

def estrai_valore(df, parole_chiave):
    if not isinstance(df, pd.DataFrame):
        st.error("Il dato passato non è un DataFrame: controllo di debug fallito.")
        return None
    descr_cols = [c for c in df.columns if c.lower() in ['voce', 'attività', 'passività e patrimonio netto']]
    if not descr_cols:
        st.error(f"Colonna descrittiva non trovata. Colonne disponibili: {df.columns.tolist()}")
        return None
    colonna = descr_cols[0]
    for p in parole_chiave:
        try:
            match = df[df[colonna].str.contains(p, case=False, na=False)]
        except Exception as e:
            st.error(f"Errore during estrai_valore match: {e}")
            continue
        if not match.empty:
            return match['Importo (€)'].values[0]
    st.error(f"Voce non trovata tra parole chiave {parole_chiave} nella colonna {colonna}")
    return None

# Sezione DuPont
if sezione == "DuPont":
    st.header("📊 Analisi DuPont")
    utile_netto = estrai_valore(ce, ["utile", "risultato d'esercizio"])
    ricavi = estrai_valore(ce, ["ricavi", "valore della produzione"])
    attivo_totale = att['Importo (€)'].sum() if isinstance(att, pd.DataFrame) else None
    patrimonio_netto = estrai_valore(pas, ["patrimonio netto"])

    if not all([utile_netto, ricavi, attivo_totale, patrimonio_netto]):
        st.warning("⚠️ Mancano voci essenziali per DuPont.")
    else:
        margine = utile_netto / ricavi
        rotazione = ricavi / attivo_totale
        leva = attivo_totale / patrimonio_netto
        roe = margine * rotazione * leva

        fig = go.Figure(data=[go.Bar(
            x=["Margine", "Rotazione", "Leva", "ROE"],
            y=[margine, rotazione, leva, roe],
            text=[f"{v:.2%}" for v in [margine, rotazione, leva, roe]],
            textposition="outside"
        )])
        fig.update_layout(title="ROE Scomposizione (DuPont)", yaxis_tickformat=".0%")
        st.plotly_chart(fig, use_container_width=True)

# Sezione Z-Score
elif sezione == "Z-Score":
    st.header("🧮 Z-Score di Altman")
    a_circolante = estrai_valore(att, ["attivo circolante"])
    debiti_brevi = estrai_valore(pas, ["debiti a breve"])
    utile_ope = estrai_valore(ce, ["ebit", "risultato operativo"])
    tot_att = att['Importo (€)'].sum() if isinstance(att, pd.DataFrame) else None
    vend = estrai_valore(ce, ["ricavi"])
    prop_net = estrai_valore(pas, ["patrimonio netto"])

    if not all([a_circolante, debiti_brevi, utile_ope, tot_att, vend, prop_net]):
        st.warning("⚠️ Dati insufficienti per Z-Score.")
    else:
        try:
            z = (1.2*(a_circolante-debiti_brevi)/tot_att +
                 1.4*utile_ope/tot_att +
                 3.3*utile_ope/tot_att +
                 0.6*prop_net/debiti_brevi +
                 1.0*vend/tot_att)
            st.metric("Altman Z-Score", f"{z:.2f}")
            if z < 1.81:
                st.error("🔴 Alto rischio di insolvenza")
            elif z < 2.99:
                st.warning("🟠 Rischio moderato")
            else:
                st.success("🟢 Basso rischio")
        except Exception as e:
            st.error(f"Errore calcolo Z-Score: {e}")

# Sezione Radar KPI
elif sezione == "Radar KPI":
    st.header("📉 Radar Chart KPI")
    kpi_res = calcola_kpi([bilancio])
    if isinstance(kpi_res, dict) and kpi_res.get("Errore"):
        st.error(f"Errore calcolo KPI: {kpi_res.get('Errore')}")
        st.stop()
    try:
        df_kpi = pd.DataFrame(kpi_res, index=[0]) if isinstance(kpi_res, dict) else pd.DataFrame(kpi_res)
        row = df_kpi.iloc[0]
        labels = [k for k in row.index if k not in ['Azienda', 'Valutazione']]
        values = [row[k] for k in labels]
        values += values[:1]; labels += labels[:1]
        radar = go.Figure(go.Scatterpolar(r=values, theta=labels, fill='toself'))
        radar.update_layout(polar=dict(radialaxis=dict(visible=True)))
        st.plotly_chart(radar, use_container_width=True)
    except Exception as e:
        st.error(f"Errore visualizzazione Radar KPI: {e}")

# Sezione Heatmap
else:
    st.header("🌡️ Heatmap Indicatori")
    heat_data = []
    error_entries = []
    for y in sorted(anni_disponibili):
        try:
            df_b = filtra_bilanci(bilanci, azienda_sel, [y])[0]
            kpi_row = calcola_kpi([df_b])
            if isinstance(kpi_row, dict) and kpi_row.get("Errore"):
                error_entries.append((y, kpi_row.get("Errore")))
                continue
            if not isinstance(kpi_row, dict):
                raise TypeError("Formato KPI non valido")
            heat_data.append(kpi_row)
        except Exception as e:
            error_entries.append((y, str(e)))
            continue
    # Mostra errori specifici
    for year, msg in error_entries:
        st.error(f"Anno {year}: {msg}")
    # Verifica struttura heat_data
    if not isinstance(heat_data, list):
        st.error("Errore nella struttura dati per Heatmap.")
        st.stop()
    if heat_data:
        df_heat = pd.DataFrame(heat_data).set_index('Azienda').T
        st.dataframe(df_heat.style.background_gradient(axis=1))
    else:
        st.info("Heatmap non disponibile: nessun dato valido.")
''
