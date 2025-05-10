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
benchmark_file = st.file_uploader("Carica file CSV benchmark (facoltativo)", type=["csv"])

benchmark_default = {
    "EBITDA Margin": 15.0,
    "ROE": 10.0,
    "ROI": 8.0,
    "Current Ratio": 1.3
}

if benchmark_file:
    df_benchmark = pd.read_csv(benchmark_file)
    benchmark = {row['KPI']: row['Valore'] for _, row in df_benchmark.iterrows()}
else:
    benchmark = benchmark_default

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

    tabella_kpi = []

    for anno, dati in sorted(bilanci.items()):
        df_ce = dati["ce"]
        df_attivo = dati["attivo"]
        df_passivo = dati["passivo"]

        try:
            ricavi = df_ce.loc[df_ce["Voce"] == "Ricavi", "Importo (€)"].values[0]
            utile_netto = df_ce.loc[df_ce["Voce"] == "Utile netto", "Importo (€)"].values[0]
            liquidita = df_attivo.loc[df_attivo["Attività"] == "Disponibilità liquide", "Importo (€)"].values[0]
            debiti_brevi = df_passivo.loc[df_passivo["Passività e Patrimonio Netto"] == "Debiti a breve", "Importo (€)"].values[0]
            current_ratio = round(liquidita / debiti_brevi, 2)

            ebit = df_ce.loc[df_ce["Voce"] == "EBIT", "Importo (€)"].values[0]
            ebitda = ebit + df_ce.loc[df_ce["Voce"] == "Spese operative", "Importo (€)"].values[0]

            patrimonio_netto = df_passivo.loc[df_passivo["Passività e Patrimonio Netto"] == "Patrimonio netto", "Importo (€)"].values[0]
            totale_attivo = df_attivo["Importo (€)"].sum()

            ebitda_margin = round(ebitda / ricavi * 100, 2)
            roe = round(utile_netto / patrimonio_netto * 100, 2)
            roi = round(ebit / totale_attivo * 100, 2)

            valutazione = "Ottima solidità ✅"
            if any([ebitda_margin < 10, roe < 5, roi < 5, current_ratio < 1]):
                valutazione = "⚠️ Attenzione: alcuni indici critici"
            if all([ebitda_margin < 10, roe < 5, roi < 5, current_ratio < 1]):
                valutazione = "❌ Situazione critica"

            tabella_kpi.append({
                "Anno": anno,
                "EBITDA Margin": ebitda_margin,
                "Benchmark EBITDA": benchmark["EBITDA Margin"],
                "Δ EBITDA": ebitda_margin - benchmark["EBITDA Margin"],
                "ROE": roe,
                "Benchmark ROE": benchmark["ROE"],
                "Δ ROE": roe - benchmark["ROE"],
                "ROI": roi,
                "Benchmark ROI": benchmark["ROI"],
                "Δ ROI": roi - benchmark["ROI"],
                "Current Ratio": current_ratio,
                "Benchmark Current": benchmark["Current Ratio"],
                "Δ Current": current_ratio - benchmark["Current Ratio"],
                "Valutazione": valutazione
            })

        except Exception as e:
            st.warning(f"Errore nell'elaborazione del bilancio {anno}: {e}")

    if tabella_kpi:
        df_kpi_finale = pd.DataFrame(tabella_kpi)

        st.markdown("## 📤 Esportazione Report Multi-anno")

        buffer_xlsx = BytesIO()
        with pd.ExcelWriter(buffer_xlsx, engine="xlsxwriter") as writer:
            df_kpi_finale.to_excel(writer, sheet_name="KPI_vs_Benchmark", index=False)
        st.download_button(
            label="📥 Scarica report Excel multi-anno",
            data=buffer_xlsx.getvalue(),
            file_name="report_multianno.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        def genera_pdf_multianno(df, logo_path):
            buffer = BytesIO()
            c = canvas.Canvas(buffer, pagesize=A4)
            width, height = A4
            if os.path.exists(logo_path):
                c.drawImage(logo_path, 2 * cm, height - 3.5 * cm, width=3 * cm, preserveAspectRatio=True)
            c.setFont("Helvetica-Bold", 16)
            c.drawString(6 * cm, height - 2.5 * cm, "Report Finanziario Multi-Anno")
            y = height - 4.5 * cm
            c.setFont("Helvetica", 11)

            for _, row in df.sort_values("Anno").iterrows():
                c.drawString(2 * cm, y, f"Anno: {row['Anno']}")
                y -= 0.6 * cm
                c.drawString(2 * cm, y, f"EBITDA Margin: {row['EBITDA Margin']}%")
                y -= 0.6 * cm
                c.drawString(2 * cm, y, f"ROE: {row['ROE']}%")
                y -= 0.6 * cm
                c.drawString(2 * cm, y, f"ROI: {row['ROI']}%")
                y -= 0.6 * cm
                c.drawString(2 * cm, y, f"Current Ratio: {row['Current Ratio']}")
                y -= 0.6 * cm
                c.drawString(2 * cm, y, f"Valutazione: {row['Valutazione']}")
                y -= 1.0 * cm
                if y < 5 * cm:
                    c.setFont("Helvetica-Oblique", 8)
                    c.drawString(2 * cm, 2 * cm, "© 2025 Andrea Bozzo – Cruscotto Finanziario per PMI")
                    c.showPage()
                    y = height - 4.5 * cm
                    c.setFont("Helvetica", 11)

            c.setFont("Helvetica-Oblique", 8)
            c.drawString(2 * cm, 2 * cm, "© 2025 Andrea Bozzo – Cruscotto Finanziario per PMI")
            c.save()
            buffer.seek(0)
            return buffer

        logo_path = "A_logo_for_Andrea_Bozzo_is_depicted_in_the_image,_.png"
        buffer_pdf = genera_pdf_multianno(df_kpi_finale, logo_path)
        st.download_button(
            label="📄 Scarica report PDF multi-anno",
            data=buffer_pdf,
            file_name="report_multianno.pdf",
            mime="application/pdf"
        )
else:
    st.info("Carica almeno un file Excel per iniziare.")
