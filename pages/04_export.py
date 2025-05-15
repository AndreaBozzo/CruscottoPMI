import streamlit as st
import pandas as pd
from io import BytesIO
from zipfile import ZipFile
from datetime import datetime

from cruscotto_pmi.utils import genera_super_pdf

st.title("📤 Esportazione avanzata dei risultati")

# Recupero dei dati
df_kpi = st.session_state.get("df_kpi", pd.DataFrame())
df_voci = st.session_state.get("df_voci", pd.DataFrame())
df_yoy = st.session_state.get("df_yoy", pd.DataFrame())

if df_kpi.empty and df_voci.empty and df_yoy.empty:
    st.warning("⚠️ Nessun dato disponibile per l'esportazione.")
    st.stop()

with st.form("export_form"):
    st.subheader("📑 Cosa vuoi includere nel report unificato?")
    export_kpi = st.checkbox("Includi KPI", value=not df_kpi.empty)
    export_voci = st.checkbox("Includi Voci di Bilancio", value=not df_voci.empty)
    export_yoy = st.checkbox("Includi Analisi YoY", value=not df_yoy.empty)
    note = st.text_area("Note personali da includere nel PDF", height=100)
    submit = st.form_submit_button("📥 Genera Report Unificato")

if submit:
    excel_buf = BytesIO()
    with pd.ExcelWriter(excel_buf, engine="xlsxwriter") as writer:
        if export_kpi and not df_kpi.empty:
            df_kpi.to_excel(writer, sheet_name="KPI", index=False)
        if export_voci and not df_voci.empty:
            df_voci.to_excel(writer, sheet_name="Bilancio", index=False)
        if export_yoy and not df_yoy.empty:
            df_yoy.to_excel(writer, sheet_name="YoY", index=False)
    excel_buf.seek(0)

    pdf_buf = genera_super_pdf(
        df_kpi if export_kpi else pd.DataFrame(),
        df_voci if export_voci else pd.DataFrame(),
        df_yoy if export_yoy else pd.DataFrame(),
        note
    )

    zip_buf = BytesIO()
    with ZipFile(zip_buf, "w") as zipf:
        zipf.writestr("report_finanziario_completo.pdf", pdf_buf.getvalue())
        zipf.writestr("dati_completi.xlsx", excel_buf.getvalue())
    zip_buf.seek(0)

    st.success("✅ Report completo generato!")
    st.download_button("📁 Scarica ZIP con PDF + Excel", zip_buf.getvalue(), file_name="export_cruscottoPMI_completo.zip")
