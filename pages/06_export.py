
import streamlit as st
import pandas as pd
from io import BytesIO
import zipfile
from cruscotto_pmi.pdf_generator import genera_super_pdf

st.set_page_config(page_title="Export Report", layout="wide")
st.title("📤 Esportazione Report Aziendale")

# === Recupero bilanci e benchmark
bilanci = st.session_state.get("bilanci", {})
benchmark = st.session_state.get("benchmark", {})

if not bilanci:
    st.warning("⚠️ Nessun bilancio disponibile per l'esportazione.")
    st.stop()

# === Selezione azienda e anno
opzioni = list(bilanci.keys())
azienda_anno = st.selectbox("📌 Seleziona Azienda e Anno", opzioni, format_func=lambda x: f"{x[0]} – {x[1]}")

azienda, anno = azienda_anno
df = bilanci.get((azienda, anno), pd.DataFrame())

if df.empty:
    st.warning("⚠️ Dati non trovati per l'azienda selezionata.")
    st.stop()

st.markdown("Puoi esportare un report PDF con i principali indicatori economico-finanziari e opzionalmente i dati in formato Excel.")

# === Area note
nota = st.text_area("📝 Aggiungi una nota personalizzata al report (facoltativa)", placeholder="Es: considerazioni, commenti, scenari...")

# === Selezione contenuti
with st.expander("⚙️ Contenuti del report"):
    include_kpi = st.checkbox("✅ Includi KPI", value=True)
    include_voci = st.checkbox("📊 Includi Voci di Bilancio", value=True)
    include_yoy = st.checkbox("📈 Includi Analisi YoY", value="df_yoy" in st.session_state)

# === Bottone per esportare
st.divider()
st.subheader("📄 Esporta Report")

if st.button("📥 Genera Report PDF + Excel"):
    df_yoy = st.session_state.get("df_yoy", pd.DataFrame())
    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
        if include_kpi:
            df_kpi = df[df["Tipo"] == "KPI"]
            if not df_kpi.empty:
                df_kpi.to_excel(writer, sheet_name="KPI", index=False)
        if include_voci:
            df[df["Tipo"] != "KPI"].to_excel(writer, sheet_name="Bilancio", index=False)
        if include_yoy and not df_yoy.empty:
            df_yoy.to_excel(writer, sheet_name="YoY", index=False)
    excel_buffer.seek(0)

    pdf_buffer = BytesIO()
    genera_super_pdf(pdf_buffer, df, benchmark, df_yoy if include_yoy else pd.DataFrame(), nota=nota)
    pdf_buffer.seek(0)

    # Pacchetto ZIP
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zipf:
        zipf.writestr(f"{azienda}_{anno}_report.pdf", pdf_buffer.read())
        zipf.writestr(f"{azienda}_{anno}_dati.xlsx", excel_buffer.read())
    zip_buffer.seek(0)

    st.success("✅ Report generato correttamente!")
    st.download_button(
        "📦 Scarica ZIP con PDF + Excel",
        zip_buffer,
        file_name=f"{azienda}_{anno}_report_completo.zip",
        mime="application/zip"
    )
