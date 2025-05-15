<<<<<<< HEAD

import streamlit as st
import pandas as pd

st.title("📈 Analisi YoY")

df_kpi = st.session_state.get("df_kpi", pd.DataFrame())
if df_kpi.empty:
    st.warning("⚠️ Carica prima i KPI nella pagina precedente.")
    st.stop()

aziende = sorted(df_kpi["Azienda"].unique())
aziende_sel = st.multiselect("Seleziona aziende", aziende, default=aziende)

kpi_base = ["EBITDA Margin", "ROE", "ROI", "Current Ratio", "Indice Sintetico", "Ricavi"]
kpi_scelti = st.multiselect("Scegli KPI da confrontare", options=kpi_base, default=kpi_base)

for azi in aziende_sel:
    dati = df_kpi[df_kpi["Azienda"] == azi].sort_values("Anno")
    if len(dati) < 2:
        continue
    yoy = dati.set_index("Anno")[kpi_scelti].pct_change().dropna().reset_index()
    yoy.columns = ["Anno"] + [f"Δ% {k}" for k in kpi_scelti]
    st.subheader(f"📊 Variazione % – {azi}")
    st.dataframe(yoy, use_container_width=True)
=======
import streamlit as st
import pandas as pd
from cruscotto_pmi.utils import genera_pdf, genera_grafico_voci
from io import BytesIO
from zipfile import ZipFile

st.title("📉 Analisi Variazioni YoY")

df_yoy = st.session_state.get("df_yoy", pd.DataFrame())
if df_yoy.empty:
    st.warning("⚠️ Nessuna analisi YoY disponibile.")
    st.stop()

st.dataframe(df_yoy, use_container_width=True)

st.subheader("📤 Esporta Analisi YoY")

note = st.text_area("Note da includere nel PDF (facoltative)", key="note_yoy")

if st.button("📥 Esporta YoY", key="btn_yoy"):
    # Grafico con variazioni percentuali
    df_plot = df_yoy.rename(columns={"Variazione %": "Importo (€)"})  # per compatibilità
    grafico_buf = genera_grafico_voci(df_plot)

    # Genera PDF
    pdf_buf = genera_pdf(df_yoy, note, grafico_kpi_buf=None, grafico_voci_buf=grafico_buf)

    # Genera Excel
    excel_buf = BytesIO()
    df_yoy.to_excel(excel_buf, index=False)
    excel_buf.seek(0)

    # Crea ZIP
    zip_buf = BytesIO()
    with ZipFile(zip_buf, 'w') as zipf:
        zipf.writestr("report_yoy.pdf", pdf_buf.getvalue())
        zipf.writestr("analisi_yoy.xlsx", excel_buf.getvalue())
    zip_buf.seek(0)

    st.success("✅ Report YoY generato!")
    st.download_button("📁 Scarica ZIP YoY", zip_buf.getvalue(), file_name="report_yoy.zip")
>>>>>>> 0c3ef1b (🚀 Versione stabile - Export completo e layout PDF migliorato)
