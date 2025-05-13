
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
