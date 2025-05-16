import streamlit as st
import pandas as pd
from cruscotto_pmi.utils import genera_pdf, genera_grafico_voci, genera_df_yoy
from io import BytesIO
from zipfile import ZipFile
import plotly.express as px


st.set_page_config(page_title="Analisi YoY", layout="wide")
st.title("📈 Analisi YoY – Variazione tra bilanci")

bilanci = st.session_state.get("bilanci", {})
if not bilanci:
    st.warning("⚠️ Nessun bilancio caricato. Carica almeno due file per visualizzare la YoY.")
    st.stop()

# Costruisci lista aziende e anni disponibili
aziende = sorted(set(k[0] for k in bilanci.keys()))
azienda_sel = st.selectbox("📌 Seleziona azienda", aziende)

anni_disp = sorted([k[1] for k in bilanci.keys() if k[0] == azienda_sel])
anni_sel = st.multiselect("📅 Seleziona due anni da confrontare", anni_disp, default=anni_disp[:2])

if len(anni_sel) != 2:
    st.info("Seleziona due anni distinti per generare il confronto.")
    st.stop()

# Ordina gli anni selezionati
y1, y2 = sorted(anni_sel)
df1 = bilanci.get((azienda_sel, y1))
df2 = bilanci.get((azienda_sel, y2))

df_yoy = genera_df_yoy(df1, df2, y1, y2, azienda=azienda_sel)

if df_yoy.empty:
    st.warning("⚠️ Nessuna variazione disponibile per le voci confrontate.")
else:
    st.dataframe(df_yoy, use_container_width=True)

    if "Voce" in df_yoy.columns and "Variazione %" in df_yoy.columns:
        fig = px.bar(
            df_yoy,
            x="Voce",
            y="Variazione %",
            color="Variazione %",
            color_continuous_scale="RdYlGn",
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ Grafico non disponibile: dati insufficienti o colonne mancanti.")


# Esportazione
st.subheader("📤 Esporta Analisi YoY")
note = st.text_area("Note da includere nel PDF (facoltative)", key="note_yoy")

if st.button("📥 Esporta YoY", key="btn_yoy"):
    df_plot = df_yoy.rename(columns={"Variazione %": "Importo (€)"})  # compatibilità per il grafico
    grafico_buf = genera_grafico_voci(df_plot)

    pdf_buf = genera_pdf(df_yoy, note, grafico_kpi_buf=None, grafico_voci_buf=grafico_buf)

    excel_buf = BytesIO()
    df_yoy.to_excel(excel_buf, index=False)
    excel_buf.seek(0)

    zip_buf = BytesIO()
    with ZipFile(zip_buf, 'w') as zipf:
        zipf.writestr("report_yoy.pdf", pdf_buf.getvalue())
        zipf.writestr("analisi_yoy.xlsx", excel_buf.getvalue())
    zip_buf.seek(0)

    st.download_button("📁 Scarica ZIP YoY", zip_buf.getvalue(), file_name="report_yoy.zip", key="download_zip_yoy")
