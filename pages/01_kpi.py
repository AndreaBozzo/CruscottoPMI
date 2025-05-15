
import streamlit as st
import pandas as pd
<<<<<<< HEAD
from cruscotto_pmi.utils import calcola_kpi
=======
from cruscotto_pmi.utils import calcola_kpi, genera_grafico_kpi, genera_grafico_voci, genera_pdf
>>>>>>> 0c3ef1b (🚀 Versione stabile - Export completo e layout PDF migliorato)

st.title("📊 Dashboard KPI")

bilanci = st.session_state.get("bilanci", {})
benchmark = st.session_state.get("benchmark", {})

if not bilanci:
    st.warning("⚠️ Carica prima i bilanci dalla Home.")
    st.stop()

tabella_kpi, tabella_voci = [], []

for (azi, yr), dfs in bilanci.items():
    row = calcola_kpi(dfs["ce"], dfs["att"], dfs["pas"], benchmark)
    if "Errore" in row:
        st.warning(f"Errore su {azi} {yr}: {row['Errore']}")
        continue
    row.update({"Azienda": azi, "Anno": int(float(yr))})
    tabella_kpi.append(row)
    tabella_voci.append({
        "Azienda": azi, "Anno": int(float(yr)),
        **{k: row[k] for k in row if k not in benchmark and k not in ["Indice Sintetico", "Valutazione", "Azienda", "Anno"]}
    })

df_kpi = pd.DataFrame(tabella_kpi)
df_voci = pd.DataFrame(tabella_voci)
df_kpi["Anno"] = df_kpi["Anno"].astype(str)
df_voci["Anno"] = df_voci["Anno"].astype(str)

st.session_state["df_kpi"] = df_kpi
st.session_state["df_voci"] = df_voci

aziende = sorted(df_kpi["Azienda"].unique())
anni = sorted(df_kpi["Anno"].unique())

azienda_sel = st.selectbox("Seleziona azienda", aziende)
anno_sel = st.selectbox("Seleziona anno", anni)

kpi_da_mostrare = {
    "EBITDA Margin": "%", "ROE": "%", "ROI": "%", "Current Ratio": "", "Indice Sintetico": "/100"
}

kpi_scelti = st.multiselect(
    "Scegli i KPI da visualizzare",
    options=list(kpi_da_mostrare.keys()),
    default=list(kpi_da_mostrare.keys())
)

riga = df_kpi[(df_kpi["Azienda"] == azienda_sel) & (df_kpi["Anno"] == anno_sel)]
if not riga.empty:
    st.subheader(f"📈 KPI – {azienda_sel} {anno_sel}")
    col1, col2 = st.columns(2)
    for i, kpi in enumerate(kpi_scelti):
        valore = riga[kpi].values[0]
        unita = kpi_da_mostrare[kpi]
        colore = "🟢" if valore > 10 else "🟡" if valore > 5 else "🔴"
        col = col1 if i % 2 == 0 else col2
        col.markdown(f"**{colore} {kpi}:** `{valore:.2f} {unita}`")
<<<<<<< HEAD
=======
df_export = st.session_state.get("df_kpi")  # o df_confronto / df_avanzata
if df_export is not None and not df_export.empty:
    st.subheader("📤 Esporta risultati")

    note = st.text_area("Note personali per il report", key="note_export_modulo_X")
    if st.button("📥 Esporta Report", key="btn_export_modulo_X"):

        grafico_kpi_buf = genera_grafico_kpi(df_export)
        grafico_voci_buf = genera_grafico_voci(st.session_state.get("df_voci", pd.DataFrame()))

        pdf_buf = genera_pdf(df_export, note, grafico_kpi_buf, grafico_voci_buf)

        excel_buf = BytesIO()
        df_export.to_excel(excel_buf, index=False)
        excel_buf.seek(0)

        zip_buf = BytesIO()
        with ZipFile(zip_buf, 'w') as zipf:
            zipf.writestr("report.pdf", pdf_buf.getvalue())
            zipf.writestr("export.xlsx", excel_buf.getvalue())
        zip_buf.seek(0)

        st.download_button("📁 Scarica ZIP", zip_buf.getvalue(), file_name="report.zip", key="zip_export_modulo_X")
>>>>>>> 0c3ef1b (🚀 Versione stabile - Export completo e layout PDF migliorato)
