
import streamlit as st
import pandas as pd
from cruscotto_pmi.kpi_calculator import calcola_kpi
from cruscotto_pmi.charts import (
    grafico_plotly_kpi,
    genera_radar_kpi,
    genera_grafico_kpi,
    grafico_gauge_indice,
    grafico_confronto_indice
)
from cruscotto_pmi.pdf_generator import genera_super_pdf
from io import BytesIO
from zipfile import ZipFile

st.set_page_config(layout="wide", page_title="KPI Aziendali")

st.title("📊 Dashboard KPI Aziendali")
st.markdown("Analizza gli indicatori di performance economico-finanziaria delle aziende selezionate. "
            "Confronta i risultati, visualizza i grafici e genera report completi.")

# === Caricamento bilanci ===
bilanci = st.session_state.get("bilanci", {})

# Fallback modalità demo
if st.session_state.get("modalita_demo", False) and not bilanci:
    bilanci_df = st.session_state.get("bilanci_df", [])
    bilanci = {}
    for df in bilanci_df:
        if {"Azienda", "Anno"}.issubset(df.columns):
            azienda = df["Azienda"].iloc[0]
            anno = int(df["Anno"].iloc[0])
            bilanci[(azienda, anno)] = df
    st.session_state["bilanci"] = bilanci

benchmark = st.session_state.get("benchmark", {})

if not bilanci:
    st.warning("⚠️ Nessun bilancio disponibile.")
    st.stop()

# === Calcolo KPI ===
tabella_kpi = []
tabella_voci = []

for (azi, yr), df in bilanci.items():
    if not isinstance(df, pd.DataFrame) or "Tipo" not in df.columns:
        continue
    try:
        df_ce = df[df["Tipo"] == "Conto Economico"]
        df_att = df[df["Tipo"] == "Attivo"]
        df_pas = df[df["Tipo"] == "Passivo"]
        row = calcola_kpi(df_ce, df_att, df_pas, benchmark)
    except Exception as e:
        st.warning(f"Errore su {azi} {yr}: {e}")
        continue

    if "Errore" in row:
        st.warning(f"Errore su {azi} {yr}: {row['Errore']}")
        continue

    row.update({"Azienda": azi, "Anno": int(float(yr))})
    tabella_kpi.append(row)

    for k, v in row.items():
        if k not in benchmark and k not in ["Indice Sintetico", "Valutazione", "Azienda", "Anno"]:
            tabella_voci.append({
                "Azienda": azi,
                "Anno": int(float(yr)),
                "Voce": k,
                "Importo (€)": v
            })

df_kpi = pd.DataFrame(tabella_kpi)
df_voci = pd.DataFrame(tabella_voci)

if df_kpi.empty:
    st.warning("⚠️ Nessun KPI calcolabile. Verifica i dati caricati o la modalità demo.")
    st.stop()

df_kpi["Anno"] = df_kpi["Anno"].astype(str)
df_voci["Anno"] = df_voci["Anno"].astype(str)

st.session_state["df_kpi"] = df_kpi
st.session_state["df_voci"] = df_voci
df_yoy = st.session_state.get("df_yoy", pd.DataFrame())

# === Tabella KPI ===
with st.container():
    st.subheader("📋 Tabella KPI")
    st.dataframe(df_kpi, use_container_width=True)
    st.divider()

# === Selezione KPI e Valutazione Visiva ===
with st.container():
    st.subheader("🧮 Analisi dettagliata per singola azienda/anno")

    aziende = sorted(df_kpi["Azienda"].unique())
    anni = sorted(df_kpi["Anno"].unique())

    col1, col2 = st.columns(2)
    with col1:
        azienda_sel = st.selectbox("🏢 Seleziona azienda", aziende)
    with col2:
        anno_sel = st.selectbox("📅 Seleziona anno", anni)

    kpi_da_mostrare = {
        "EBITDA Margin": "%", "ROE": "%", "ROI": "%", "Current Ratio": "", "Indice Sintetico": "/100"
    }
    kpi_scelti = st.multiselect(
        "🎯 KPI da visualizzare",
        options=list(kpi_da_mostrare.keys()),
        default=list(kpi_da_mostrare.keys())
    )

    riga = df_kpi[(df_kpi["Azienda"] == azienda_sel) & (df_kpi["Anno"] == anno_sel)]
    if not riga.empty:
        st.markdown("### 📈 Risultati KPI")
        col1, col2 = st.columns(2)
        for i, kpi in enumerate(kpi_scelti):
            if kpi not in riga.columns:
                st.warning(f"⚠️ '{kpi}' non disponibile per {azienda_sel} – {anno_sel}")
                continue

            valore = riga[kpi].values[0]
            unita = kpi_da_mostrare.get(kpi, "")
            colore = "🟢" if valore > 10 else "🟡" if valore > 5 else "🔴"
            col = col1 if i % 2 == 0 else col2

            col.markdown(f"""<div style='background-color:#f9f9f9;
                        padding:1rem;border-left:5px solid #ccc;
                        border-radius:8px;margin-bottom:0.5rem'>
                        <strong style='font-size:1.1rem'>{colore} {kpi}</strong><br>
                        <span style='font-size:1.3rem'>{valore:.2f} {unita}</span>
                        </div>""", unsafe_allow_html=True)


# === Grafici KPI singoli ===
with st.container():
    st.subheader("📈 Grafici per Azienda")
    aziende = sorted(df_kpi["Azienda"].unique())

    for i, azienda in enumerate(aziende):
        st.markdown(f"#### 🔎 {azienda}")
        fig = genera_grafico_kpi(df_kpi[df_kpi["Azienda"] == azienda])

        if hasattr(fig, "to_dict"):
            st.plotly_chart(fig, use_container_width=True, key=f"fig_{i}")
        else:
            st.warning(f"⚠️ Errore: genera_grafico_kpi() non ha restituito un oggetto Plotly per {azienda}. Tipo ricevuto: {type(fig)}")

    st.divider()

# === Confronto tra aziende ===
with st.container():
    st.subheader("⚖️ Confronto KPI tra Aziende")
    fig = grafico_confronto_indice(df_kpi)
    if fig is not None:
        st.plotly_chart(fig, use_container_width=True, key='fig_2')
    else:
        st.info("⚠️ Nessun confronto disponibile")
        st.plotly_chart(fig, use_container_width=True, key='fig_3')
    st.divider()

# === Radar & Gauge ===
with st.container():
    st.subheader("🧭 Radar e Gauge per ciascun bilancio")

    for i, ((azi, yr), df) in enumerate(bilanci.items()):
        st.markdown(f"### 📌 {azi} – {yr}")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 🎯 Radar KPI")
            radar = genera_radar_kpi(df)  # ✅ CORRETTO: 1 solo argomento
            if radar is not None:
                st.plotly_chart(radar, use_container_width=True, key=f"radar_{i}")
            else:
                st.info("Nessun radar disponibile.")

        with col2:
            st.markdown("#### ⏱️ Gauge Finanziari")
            try:
                gauge = grafico_gauge_indice(df, benchmark)
                if gauge is not None:
                    st.plotly_chart(gauge, use_container_width=True, key=f"gauge_{i}")
                else:
                    st.info("Nessun gauge disponibile.")
            except:
                st.info("Gauge non disponibile per questo bilancio.")

    st.divider()



# === Export PDF ===
with st.expander("📤 Esporta Report PDF"):
    if st.button("📄 Genera PDF"):
        buffer = BytesIO()
        genera_super_pdf(buffer, df_kpi, df_voci, df_yoy)
        st.download_button("📥 Scarica PDF", buffer.getvalue(), file_name="report_kpi.pdf")
