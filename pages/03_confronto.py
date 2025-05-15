
import streamlit as st
import pandas as pd
import plotly.express as px

st.title("📘 Confronto voci di bilancio")

df_voci = st.session_state.get("df_voci", pd.DataFrame())
if df_voci.empty:
    st.warning("⚠️ Carica prima i bilanci.")
    st.stop()

anni = df_voci["Anno"].unique()
anni_sel = st.multiselect("Filtra per anno", anni, default=list(anni))
voci = [c for c in df_voci.columns if c not in ["Azienda", "Anno"]]
voci_sel = st.multiselect("Seleziona voci", voci, default=["Ricavi", "EBIT"])

dfb = df_voci[df_voci["Anno"].isin(anni_sel)]

for voce in voci_sel:
    fig = px.bar(dfb, x="Azienda", y=voce, color="Anno", barmode="group", title=voce)
    st.plotly_chart(fig, use_container_width=True)
<<<<<<< HEAD
=======



from cruscotto_pmi.utils import genera_pdf, genera_grafico_kpi, genera_grafico_voci
from io import BytesIO
from zipfile import ZipFile

df_export = st.session_state.get("df_voci", pd.DataFrame())
if df_export is not None and not df_export.empty:
    st.subheader("📤 Esporta Confronto")

    note = st.text_area("Note per il report confronto", key="note_confronto")

    if st.button("📥 Esporta confronto", key="btn_confronto"):
        grafico_kpi_buf = genera_grafico_kpi(st.session_state.get("df_kpi", pd.DataFrame()))
        grafico_voci_buf = genera_grafico_voci(df_export)

        pdf_buf = genera_pdf(df_export, note, grafico_kpi_buf, grafico_voci_buf)

        excel_buf = BytesIO()
        df_export.to_excel(excel_buf, index=False)
        excel_buf.seek(0)

        zip_buf = BytesIO()
        with ZipFile(zip_buf, 'w') as zipf:
            zipf.writestr("report_confronto.pdf", pdf_buf.getvalue())
            zipf.writestr("confronto_voci.xlsx", excel_buf.getvalue())
        zip_buf.seek(0)

        st.success("✅ Report confronto generato!")
        st.download_button("📁 Scarica ZIP Confronto", zip_buf.getvalue(), file_name="report_confronto.zip")
>>>>>>> 0c3ef1b (🚀 Versione stabile - Export completo e layout PDF migliorato)
