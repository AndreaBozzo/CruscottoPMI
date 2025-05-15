import streamlit as st
import pandas as pd
from cruscotto_pmi.utils import genera_pdf, genera_grafico_voci
from io import BytesIO
from zipfile import ZipFile

df_yoy = st.session_state.get("df_yoy", pd.DataFrame())
st.write("DEBUG YOY caricato:", df_yoy)
if df_yoy.empty:
    st.warning("⚠️ Nessuna analisi YoY disponibile.")
    st.stop()

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
