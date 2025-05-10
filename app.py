# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm


st.set_page_config(page_title="Cruscotto Finanziario PMI", layout="wide")
st.title("📊 Cruscotto Finanziario per PMI")

uploaded_file = st.file_uploader("Carica il file Excel con più anni", type=["xlsx"])

if uploaded_file:
    # Leggi i tre fogli con colonna "Anno"
    df_ce = pd.read_excel(uploaded_file, sheet_name="Conto Economico")
    df_attivo = pd.read_excel(uploaded_file, sheet_name="Attivo")
    df_passivo = pd.read_excel(uploaded_file, sheet_name="Passivo")

    # Estrai anni disponibili
    anni_disponibili = sorted(df_ce["Anno"].unique(), reverse=True)
    anno_scelto = st.selectbox("Seleziona l'anno da analizzare", anni_disponibili)

    # Filtra per anno scelto
    df_ce_anno = df_ce[df_ce["Anno"] == anno_scelto]
    df_attivo_anno = df_attivo[df_attivo["Anno"] == anno_scelto]
    df_passivo_anno = df_passivo[df_passivo["Anno"] == anno_scelto]

    # Mostra i dati filtrati
    st.subheader(f"Conto Economico ({anno_scelto})")
    st.dataframe(df_ce_anno)

    st.subheader(f"Stato Patrimoniale - Attivo ({anno_scelto})")
    st.dataframe(df_attivo_anno)

    st.subheader(f"Stato Patrimoniale - Passivo ({anno_scelto})")
    st.dataframe(df_passivo_anno)

# --- Estrazione Valori e KPI ---
ricavi = df_ce_anno.loc[df_ce_anno["Voce"] == "Ricavi", "Importo (€)"].values[0]
utile_netto = df_ce_anno.loc[df_ce_anno["Voce"] == "Utile netto", "Importo (€)"].values[0]
ebit = df_ce_anno.loc[df_ce_anno["Voce"] == "EBIT", "Importo (€)"].values[0]
spese_oper = df_ce_anno.loc[df_ce_anno["Voce"] == "Spese operative", "Importo (€)"].values[0]

liquidità = df_attivo_anno.loc[df_attivo_anno["Attività"] == "Disponibilità liquide", "Importo (€)"].values[0]
debiti_brevi = df_passivo_anno.loc[df_passivo_anno["Passività e Patrimonio Netto"] == "Debiti a breve", "Importo (€)"].values[0]
patrimonio_netto = df_passivo_anno.loc[df_passivo_anno["Passività e Patrimonio Netto"] == "Patrimonio netto", "Importo (€)"].values[0]
totale_attivo = df_attivo_anno["Importo (€)"].sum()

# KPI
current_ratio = round(liquidità / debiti_brevi, 2)
ebitda = ebit + spese_oper
ebitda_margin = round(ebitda / ricavi * 100, 2)
roe = round(utile_netto / patrimonio_netto * 100, 2)
roi = round(ebit / totale_attivo * 100, 2)

st.markdown(f"## 📌 Indicatori di Redditività ({anno_scelto})")
col1, col2, col3 = st.columns(3)
col1.metric("EBITDA Margin", f"{ebitda_margin} %")
col2.metric("ROE", f"{roe} %")
col3.metric("ROI", f"{roi} %")

# --- 📊 GRAFICO A BARRE ---
st.markdown(f"## 📈 Ricavi e Utile Netto ({anno_scelto})")
import plotly.express as px
bar_fig = px.bar(
    x=["Ricavi", "Utile Netto"],
    y=[ricavi, utile_netto],
    labels={"x": "Voce", "y": "Importo (€)"},
    color=["Ricavi", "Utile Netto"],
    text=[ricavi, utile_netto]
)
st.plotly_chart(bar_fig, use_container_width=True)

# --- 🧩 GRAFICI A TORTA ---
st.markdown(f"## 🧩 Composizione Attivo e Passivo ({anno_scelto})")
col1, col2 = st.columns(2)

fig_attivo = px.pie(df_attivo_anno, names="Attività", values="Importo (€)", title="Attivo")
col1.plotly_chart(fig_attivo, use_container_width=True)

fig_passivo = px.pie(df_passivo_anno, names="Passività e Patrimonio Netto", values="Importo (€)", title="Passivo")
col2.plotly_chart(fig_passivo, use_container_width=True)


        # Esportazione Excel
        st.markdown("## \U0001F4E4 Esporta il Report")
        export_ce = df_ce.copy()
        export_attivo = df_attivo.copy()
        export_passivo = df_passivo.copy()

        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            export_ce.to_excel(writer, sheet_name="Conto Economico", index=False)
            export_attivo.to_excel(writer, sheet_name="Attivo", index=False)
            export_passivo.to_excel(writer, sheet_name="Passivo", index=False)
            kpi_df = pd.DataFrame({
                "KPI": ["Current Ratio", "EBITDA Margin (%)", "ROE (%)", "ROI (%)"],
                "Valore": [current_ratio, ebitda_margin, roe, roi]
            })
            kpi_df.to_excel(writer, sheet_name="Indicatori", index=False)

        st.download_button(
            label="\U0001F4E5 Scarica report Excel",
            data=output.getvalue(),
            file_name="report_finanziario.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # Salvataggio grafici per PDF
        bar_fig.write_image("bar_chart.png")
        fig_attivo.write_image("pie_attivo.png")
        fig_passivo.write_image("pie_passivo.png")

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
            if os.path.exists(bar_chart_path):
                c.drawImage(bar_chart_path, 2 * cm, y - 8 * cm, width=16 * cm, height=6 * cm)
                y -= 9 * cm
            if os.path.exists(pie1_path):
                c.drawImage(pie1_path, 2 * cm, y - 7 * cm, width=8 * cm, height=6 * cm)
            if os.path.exists(pie2_path):
                c.drawImage(pie2_path, 10 * cm, y - 7 * cm, width=8 * cm, height=6 * cm)
            c.showPage()
            c.save()
            buffer.seek(0)
            return buffer

        kpi_data = {
            "Ricavi": f"€ {ricavi:,.0f}",
            "Utile Netto": f"€ {utile_netto:,.0f}",
            "Current Ratio": current_ratio,
            "EBITDA Margin": f"{ebitda_margin}%",
            "ROE": f"{roe}%",
            "ROI": f"{roi}%"
        }

        pdf_buffer = genera_pdf(kpi_data, "bar_chart.png", "pie_attivo.png", "pie_passivo.png")
        st.download_button(
            label="\U0001F4C4 Scarica report PDF",
            data=pdf_buffer,
            file_name="report_finanziario.pdf",
            mime="application/pdf"
        )
else:
    st.info("Carica un file Excel per iniziare.")

