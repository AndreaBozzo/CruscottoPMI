<<<<<<< HEAD

import streamlit as st
import pandas as pd
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm

st.title("📤 Esportazione risultati")

df_kpi = st.session_state.get("df_kpi", pd.DataFrame())
df_voci = st.session_state.get("df_voci", pd.DataFrame())

if df_kpi.empty:
    st.warning("⚠️ Nessun dato disponibile.")
    st.stop()

buffer = BytesIO()
with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
    df_kpi.to_excel(writer, sheet_name="KPI", index=False)
    df_voci.to_excel(writer, sheet_name="Bilancio", index=False)

st.download_button("📥 Scarica Excel", buffer.getvalue(), file_name="cruscotto_finanziario.xlsx")

def genera_pdf(df):
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2 * cm, height - 2 * cm, "Report Finanziario PMI")
    c.setFont("Helvetica", 10)
    y = height - 3 * cm
    for _, row in df.iterrows():
        for key in ["Azienda", "Anno", "EBITDA Margin", "ROE", "ROI", "Current Ratio", "Indice Sintetico", "Valutazione"]:
            c.drawString(2 * cm, y, f"{key}: {row.get(key, '-')}")
            y -= 0.5 * cm
        y -= 0.3 * cm
        if y < 4 * cm:
            c.showPage()
            y = height - 3 * cm
    c.save()
    buf.seek(0)
    return buf

pdf_buf = genera_pdf(df_kpi)
st.download_button("📄 Scarica PDF", pdf_buf, file_name="report_finanziario.pdf")
=======
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
>>>>>>> 0c3ef1b (🚀 Versione stabile - Export completo e layout PDF migliorato)
