import streamlit as st
import pandas as pd
from cruscotto_pmi.charts import genera_trend_kpi, genera_grafico_confronto_kpi

st.set_page_config(layout="wide", page_title="Trend & Confronto KPI")
st.title("📈 Trend & Confronto KPI")
st.markdown("Scegli un KPI, le aziende e gli anni per vedere evoluzione e confronto con il benchmark.")

# === Dati da sessione ===
df_kpi = st.session_state.get("df_kpi", pd.DataFrame())
benchmark_globale = st.session_state.get("benchmark", {})

# === Validazione base ===
if df_kpi.empty:
    st.warning("⚠️ Nessun dato KPI disponibile. Carica bilanci o avvia demo.")
    st.stop()

# === Selettore KPI ===
KPI_CHOICES = sorted(df_kpi["KPI"].unique())
default_idx = KPI_CHOICES.index("Indice Sintetico") if "Indice Sintetico" in KPI_CHOICES else 0
kpi_sel = st.selectbox("🔍 KPI", KPI_CHOICES, index=default_idx)

# === Selettore aziende (multiselect) ===
aziende = sorted(df_kpi["Azienda"].unique())
aziende_sel = st.multiselect(
    "🏢 Aziende",
    aziende,
    default=aziende[:1],
    help="Seleziona una o più aziende da confrontare"
)
if not aziende_sel:
    st.warning("⚠️ Seleziona almeno un'azienda.")
    st.stop()

# === Selettore anni (multiselect) ===
anni = sorted(df_kpi["Anno"].astype(str).unique())
anni_sel = st.multiselect(
    "📅 Anni",
    anni,
    default=anni,
    help="Seleziona gli anni per il trend e il confronto"
)
if not anni_sel:
    st.warning("⚠️ Seleziona almeno un anno.")
    st.stop()

# === Benchmark dinamico ===
st.markdown("### 🎯 Benchmark per il KPI selezionato")
bm_default = float(benchmark_globale.get(kpi_sel, 0))
show_benchmark = st.checkbox("Mostra linea benchmark", value=True)

if show_benchmark:
    bm_override = st.number_input(
        f"Valore di riferimento per {kpi_sel}",
        value=bm_default,
        step=0.1,
        help="Modifica temporanea del benchmark per questo KPI"
    )
    benchmark_corrente = {kpi_sel: bm_override}
else:
    benchmark_corrente = {}

# === Grafico Trend Multi-Anno ===
st.divider()
st.subheader(f"📈 Trend di {kpi_sel}")
df_trend = df_kpi[
    (df_kpi["KPI"] == kpi_sel) &
    (df_kpi["Azienda"].isin(aziende_sel)) &
    (df_kpi["Anno"].astype(str).isin(anni_sel))
]
if not df_trend.empty:
    fig_trend = genera_trend_kpi(df_trend, kpi_sel, benchmark_corrente)
    st.plotly_chart(fig_trend, use_container_width=True, key=f"trend_{kpi_sel}")
else:
    st.info("Trend non disponibile per le selezioni correnti.")

# === Grafico Confronto Cross-Company ===
st.divider()
anno_conf = st.selectbox("Anno per confronto", anni_sel, index=len(anni_sel)-1)
st.subheader(f"⚖️ Confronto {kpi_sel} – Anno {anno_conf}")
df_conf = df_kpi[
    (df_kpi["KPI"] == kpi_sel) &
    (df_kpi["Anno"].astype(str) == anno_conf) &
    (df_kpi["Azienda"].isin(aziende_sel))
]
if not df_conf.empty:
    fig_conf = genera_grafico_confronto_kpi(df_conf, kpi_sel, anno_conf, benchmark_corrente)
    st.plotly_chart(fig_conf, use_container_width=True, key=f"conf_{kpi_sel}")
else:
    st.info("Confronto non disponibile per le selezioni correnti.")
