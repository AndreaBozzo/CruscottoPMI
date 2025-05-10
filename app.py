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

uploaded_files = st.file_uploader("Carica uno o più file Excel del bilancio (uno per anno)", type=["xlsx"], accept_multiple_files=True)

if uploaded_files:
    bilanci = {}

    for file in uploaded_files:
        try:
            df_ce = pd.read_excel(file, sheet_name="Conto Economico")
            df_attivo = pd.read_excel(file, sheet_name="Attivo")
            df_passivo = pd.read_excel(file, sheet_name="Passivo")
            anno = file.name.split("_")[0] if "_" in file.name else file.name
            bilanci[anno] = {
                "ce": df_ce,
                "attivo": df_attivo,
                "passivo": df_passivo
            }
        except Exception as e:
            st.error(f"Errore nel file {file.name}: {e}")

    for anno, dati in sorted(bilanci.items()):
        st.header(f"📅 Bilancio {anno}")
        df_ce = dati["ce"]
        df_attivo = dati["attivo"]
        df_passivo = dati["passivo"]

        st.subheader("Conto Economico")
        st.dataframe(df_ce)

        st.subheader("Stato Patrimoniale - Attivo")
        st.dataframe(df_attivo)

        st.subheader("Stato Patrimoniale - Passivo")
        st.dataframe(df_passivo)

        # Estrazione valori chiave
        try:
            ricavi = df_ce.loc[df_ce["Voce"] == "Ricavi", "Importo (€)"].values[0]
            utile_netto = df_ce.loc[df_ce["Voce"] == "Utile netto", "Importo (€)"].values[0]
            liquidita = df_attivo.loc[df_attivo["Attività"] == "Disponibilità liquide", "Importo (€)"].values[0]
            debiti_brevi = df_passivo.loc[df_passivo["Passività e Patrimonio Netto"] == "Debiti a breve", "Importo (€)"].values[0]
            current_ratio = round(liquidita / debiti_brevi, 2)

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

            # 📊 Grafico a barre
            st.markdown("## 📈 Ricavi e Utile Netto")
            bar_fig = px.bar(
                x=["Ricavi", "Utile Netto"],
                y=[ricavi, utile_netto],
                labels={"x": "Voce", "y": "Importo (€)"},
                color=["Ricavi", "Utile Netto"],
                text=[ricavi, utile_netto]
            )
            st.plotly_chart(bar_fig, use_container_width=True)

            # 🧩 Grafici a torta
            st.markdown("## 🧩 Composizione Attivo e Passivo")
            col1, col2 = st.columns(2)

            fig_attivo = px.pie(df_attivo, names="Attività", values="Importo (€)", title="Attivo")
            col1.plotly_chart(fig_attivo, use_container_width=True)

            fig_passivo = px.pie(df_passivo, names="Passività e Patrimonio Netto", values="Importo (€)", title="Passivo")
            col2.plotly_chart(fig_passivo, use_container_width=True)

            # 🔄 Esportazione Excel
            st.markdown("## \U0001F4E4 Esporta il Report")
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_ce.to_excel(writer, sheet_name="Conto Economico", index=False)
                df_attivo.to_excel(writer, sheet_name="Attivo", index=False)
                df_passivo.to_excel(writer, sheet_name="Passivo", index=False)

                kpi_df = pd.DataFrame({
                    "KPI": ["Current Ratio", "EBITDA Margin (%)", "ROE (%)", "ROI (%)"],
                    "Valore": [current_ratio, ebitda_margin, roe, roi]
                })
                kpi_df.to_excel(writer, sheet_name="Indicatori", index=False)

            st.download_button(
                label=f"📥 Scarica report Excel {anno}",
                data=output.getvalue(),
                file_name=f"report_{anno}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            # 📄 PDF
            def genera_pdf(kpi_dict, bar_chart_path, pie1_path, pie2_path):
                buffer = BytesIO()
                c = canvas.Canvas(buffer, pagesize=A4)
                width, height = A4

                c.setFont("Helvetica-Bold", 16)
                c.drawString(2 * cm, height - 2 * cm, f"Report Finanziario {anno}")

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

            bar_path = f"bar_chart_{anno}.png"
            pie_attivo_path = f"pie_attivo_{anno}.png"
            pie_passivo_path = f"pie_passivo_{anno}.png"

            bar_fig.write_image(bar_path)
            fig_attivo.write_image(pie_attivo_path)
            fig_passivo.write_image(pie_passivo_path)

            kpi_data = {
                "Ricavi": f"€ {ricavi:,.0f}",
                "Utile Netto": f"€ {utile_netto:,.0f}",
                "Current Ratio": current_ratio,
                "EBITDA Margin": f"{ebitda_margin}%",
                "ROE": f"{roe}%",
                "ROI": f"{roi}%"
            }

            pdf_buffer = genera_pdf(kpi_data, bar_path, pie_attivo_path, pie_passivo_path)

            st.download_button(
                label=f"📄 Scarica report PDF {anno}",
                data=pdf_buffer,
                file_name=f"report_{anno}.pdf",
                mime="application/pdf"
            )

        except Exception as e:
            st.warning(f"Errore nell'elaborazione del bilancio {anno}: {e}")
else:
    st.info("Carica almeno un file Excel per iniziare.")
