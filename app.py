# app.py
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Cruscotto Finanziario PMI", layout="wide")
st.title("📊 Cruscotto Finanziario per PMI")

uploaded_file = st.file_uploader("Carica il file Excel del bilancio", type=["xlsx"])

if uploaded_file:
    df_ce = pd.read_excel(uploaded_file, sheet_name="Conto Economico")
    df_attivo = pd.read_excel(uploaded_file, sheet_name="Attivo")
    df_passivo = pd.read_excel(uploaded_file, sheet_name="Passivo")

    st.subheader("Conto Economico")
    st.dataframe(df_ce)

    st.subheader("Stato Patrimoniale - Attivo")
    st.dataframe(df_attivo)

    st.subheader("Stato Patrimoniale - Passivo")
    st.dataframe(df_passivo)

    # Estrazione valori
    ricavi = df_ce.loc[df_ce["Voce"] == "Ricavi", "Importo (€)"].values[0]
    utile_netto = df_ce.loc[df_ce["Voce"] == "Utile netto", "Importo (€)"].values[0]
    liquidità = df_attivo.loc[df_attivo["Attività"] == "Disponibilità liquide", "Importo (€)"].values[0]
    debiti_brevi = df_passivo.loc[df_passivo["Passività e Patrimonio Netto"] == "Debiti a breve", "Importo (€)"].values[0]
    current_ratio = round(liquidità / debiti_brevi, 2)

    # KPI
     # Altri indicatori di bilancio
    ebit = df_ce.loc[df_ce["Voce"] == "EBIT", "Importo (€)"].values[0]
    ebitda = ebit + df_ce.loc[df_ce["Voce"] == "Spese operative", "Importo (€)"].values[0]  # approssimazione

    patrimonio_netto = df_passivo.loc[df_passivo["Passività e Patrimonio Netto"] == "Patrimonio netto", "Importo (€)"].values[0]
    totale_attivo = df_attivo["Importo (€)"].sum()

    ebitda_margin = round(ebitda / ricavi * 100, 2)
    roe = round(utile_netto / patrimonio_netto * 100, 2)
    roi = round(ebit / totale_attivo * 100, 2)

    st.markdown("## 📌 Indicatori di Redditività")
    col1, col2, col3 = st.columns(3)
    col1.metric("EBITDA Margin", f"{ebitda_margin} %")
    col2.metric("ROE", f"{roe} %")
    col3.metric("ROI", f"{roi} %")

    # 📊 GRAFICO A BARRE: Ricavi vs Utile Netto
    st.markdown("## 📈 Ricavi e Utile Netto")
    bar_fig = px.bar(
        x=["Ricavi", "Utile Netto"],
        y=[ricavi, utile_netto],
        labels={"x": "Voce", "y": "Importo (€)"},
        color=["Ricavi", "Utile Netto"],
        text=[ricavi, utile_netto]
    )
    st.plotly_chart(bar_fig, use_container_width=True)

    # 🧩 GRAFICI A TORTA
    st.markdown("## 🧩 Composizione Attivo e Passivo")
    col1, col2 = st.columns(2)

    # Attivo
    fig_attivo = px.pie(df_attivo, names="Attività", values="Importo (€)", title="Attivo")
    col1.plotly_chart(fig_attivo, use_container_width=True)

    # Passivo
    fig_passivo = px.pie(df_passivo, names="Passività e Patrimonio Netto", values="Importo (€)", title="Passivo")
    col2.plotly_chart(fig_passivo, use_container_width=True)

else:
    st.info("Carica un file Excel per iniziare.")
  # 🔄 Esportazione dati
    st.markdown("## 📤 Esporta il Report")

    export_ce = df_ce.copy()
    export_attivo = df_attivo.copy()
    export_passivo = df_passivo.copy()

    from io import BytesIO
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        export_ce.to_excel(writer, sheet_name="Conto Economico", index=False)
        export_attivo.to_excel(writer, sheet_name="Attivo", index=False)
        export_passivo.to_excel(writer, sheet_name="Passivo", index=False)

        # KPI aggiuntivi
        kpi_df = pd.DataFrame({
            "KPI": ["Current Ratio", "EBITDA Margin (%)", "ROE (%)", "ROI (%)"],
            "Valore": [current_ratio, ebitda_margin, roe, roi]
        })
        kpi_df.to_excel(writer, sheet_name="Indicatori", index=False)

    st.download_button(
        label="📥 Scarica report Excel",
        data=output.getvalue(),
        file_name="report_finanziario.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
  import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

# Funzione per creare il PDF
def genera_pdf(kpi_dict, bar_chart_path, pie1_path, pie2_path):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 16)
    c.drawString(2 * cm, height - 2 * cm, "Report Finanziario PMI")

    c.setFont("Helvetica", 12)
    y = height - 3.5 * cm
    for k, v in kpi_dict.items():
        c.drawString(2 * cm, y, f"{k}: {v}")
        y -= 0.6 * cm

    # Inserimento immagini
    if os.path.exists(bar_chart_path):
        c.drawImage(bar_chart_path, 2 * cm, y - 8 * cm, width=16*cm, height=6*cm)
        y -= 9 * cm
    if os.path.exists(pie1_path):
        c.drawImage(pie1_path, 2 * cm, y - 7 * cm, width=8*cm, height=6*cm)
    if os.path.exists(pie2_path):
        c.drawImage(pie2_path, 10 * cm, y - 7 * cm, width=8*cm, height=6*cm)

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# Salva i grafici come immagini
bar_fig.write_image("bar_chart.png")
fig_attivo.write_image("pie_attivo.png")
fig_passivo.write_image("pie_passivo.png")

# Dizionario KPI
kpi_data = {
    "Ricavi": f"€ {ricavi:,.0f}",
    "Utile Netto": f"€ {utile_netto:,.0f}",
    "Current Ratio": current_ratio,
    "EBITDA Margin": f"{ebitda_margin}%",
    "ROE": f"{roe}%",
    "ROI": f"{roi}%"
}

# Genera PDF
pdf_buffer = genera_pdf(kpi_data, "bar_chart.png", "pie_attivo.png", "pie_passivo.png")

# Bottone di download
st.download_button(
    label="📄 Scarica report PDF",
    data=pdf_buffer,
    file_name="report_finanziario.pdf",
    mime="application/pdf"
)
