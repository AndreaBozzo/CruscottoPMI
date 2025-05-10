# Cruscotto Finanziario per PMI - Build Completa
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

benchmark_default = {"EBITDA Margin": 15.0, "ROE": 10.0, "ROI": 8.0, "Current Ratio": 1.3}
if benchmark_file:
    df_benchmark = pd.read_csv(benchmark_file)
    benchmark = {row['KPI']: row['Valore'] for _, row in df_benchmark.iterrows()}
else:
    benchmark = benchmark_default

if uploaded_files:
    bilanci, tabella_kpi, tabella_voci = {}, [], []
    for file in uploaded_files:
        try:
            df_ce = pd.read_excel(file, sheet_name="Conto Economico")
            df_attivo = pd.read_excel(file, sheet_name="Attivo")
            df_passivo = pd.read_excel(file, sheet_name="Passivo")
            nome_split = file.name.replace(".xlsx", "").split("_")
            azienda, anno = (nome_split + ["Sconosciuta"])[0:2]
            bilanci[(azienda, anno)] = {"ce": df_ce, "attivo": df_attivo, "passivo": df_passivo}
        except Exception as e:
            st.error(f"Errore nel file {file.name}: {e}")

    for (azienda, anno), dati in sorted(bilanci.items()):
        df_ce, df_attivo, df_passivo = dati["ce"], dati["attivo"], dati["passivo"]
        try:
            ricavi = df_ce.loc[df_ce["Voce"] == "Ricavi", "Importo (€)"].values[0]
            utile_netto = df_ce.loc[df_ce["Voce"] == "Utile netto", "Importo (€)"].values[0]
            ebit = df_ce.loc[df_ce["Voce"] == "EBIT", "Importo (€)"].values[0]
            spese_oper = df_ce.loc[df_ce["Voce"] == "Spese operative", "Importo (€)"].values[0]
            ammortamenti = df_ce.loc[df_ce["Voce"] == "Ammortamenti", "Importo (€)"].values[0] if "Ammortamenti" in df_ce["Voce"].values else 0
            oneri_fin = df_ce.loc[df_ce["Voce"] == "Oneri finanziari", "Importo (€)"].values[0] if "Oneri finanziari" in df_ce["Voce"].values else 0
            mol = ricavi - spese_oper
            liquidita = df_attivo.loc[df_attivo["Attività"] == "Disponibilità liquide", "Importo (€)"].values[0]
            debiti_brevi = df_passivo.loc[df_passivo["Passività e Patrimonio Netto"] == "Debiti a breve", "Importo (€)"].values[0]
            patrimonio_netto = df_passivo.loc[df_passivo["Passività e Patrimonio Netto"] == "Patrimonio netto", "Importo (€)"].values[0]
            totale_attivo = df_attivo["Importo (€)"].sum()

            ebitda = ebit + spese_oper
            ebitda_margin = round(ebitda / ricavi * 100, 2)
            roe = round(utile_netto / patrimonio_netto * 100, 2)
            roi = round(ebit / totale_attivo * 100, 2)
            current_ratio = round(liquidita / debiti_brevi, 2)
            valutazione = "Ottima solidità ✅"
            if any([ebitda_margin < 10, roe < 5, roi < 5, current_ratio < 1]): valutazione = "⚠️ Alcuni indici critici"
            if all([ebitda_margin < 10, roe < 5, roi < 5, current_ratio < 1]): valutazione = "❌ Situazione critica"

            indice_sintetico = round((
                (ebitda_margin / benchmark["EBITDA Margin"] +
                roe / benchmark["ROE"] +
                roi / benchmark["ROI"] +
                current_ratio / benchmark["Current Ratio"]) / 4) * 10, 1)

            tabella_kpi.append({
                "Azienda": azienda, "Anno": anno,
                "EBITDA Margin": ebitda_margin, "Benchmark EBITDA": benchmark["EBITDA Margin"],
                "ROE": roe, "Benchmark ROE": benchmark["ROE"],
                "ROI": roi, "Benchmark ROI": benchmark["ROI"],
                "Current Ratio": current_ratio, "Benchmark Current": benchmark["Current Ratio"],
                "Indice Sintetico": indice_sintetico, "Valutazione": valutazione
            })

            tabella_voci.append({"Azienda": azienda, "Anno": anno, "Ricavi": ricavi, "Utile Netto": utile_netto, "EBIT": ebit,
                "Spese Operative": spese_oper, "Ammortamenti": ammortamenti, "Oneri Finanziari": oneri_fin, "MOL": mol,
                "Totale Attivo": totale_attivo, "Patrimonio Netto": patrimonio_netto, "Liquidità": liquidita, "Debiti a Breve": debiti_brevi})

        except Exception as e:
            st.warning(f"Errore nell'elaborazione di {azienda} {anno}: {e}")

    df_kpi_finale = pd.DataFrame(tabella_kpi)
    df_voci_finale = pd.DataFrame(tabella_voci)

    st.sidebar.markdown("## 🔍 Filtri Dashboard")
    anni = sorted(df_kpi_finale['Anno'].unique())
    aziende = sorted(df_kpi_finale['Azienda'].unique())
    kpi_sel = st.sidebar.multiselect("Seleziona KPI", ["EBITDA Margin", "ROE", "ROI", "Current Ratio"], default=["EBITDA Margin", "ROE"])
    anni_sel = st.sidebar.multiselect("Seleziona Anno", anni, default=anni)
    voci_bilancio = [col for col in df_voci_finale.columns if col not in ["Anno", "Azienda"]]
    voci_sel = st.sidebar.multiselect("Voci di Bilancio", voci_bilancio, default=["Ricavi", "EBIT"])

    def evidenzia_valori(row):
        return pd.Series({
            "EBITDA Margin": "background-color: #f8d7da" if row["EBITDA Margin"] < 10 else "background-color: #d4edda",
            "ROE": "background-color: #f8d7da" if row["ROE"] < 5 else "background-color: #d4edda",
            "ROI": "background-color: #f8d7da" if row["ROI"] < 5 else "background-color: #d4edda",
            "Current Ratio": "background-color: #f8d7da" if row["Current Ratio"] < 1 else "background-color: #d4edda"
        })

    st.markdown("## 🧾 Riepilogo KPI con Benchmark")
    styled_df = df_kpi_finale.style.format("{:.2f}", na_rep="-").apply(evidenzia_valori, axis=1)
    st.dataframe(styled_df, use_container_width=True)

    if anni_sel and kpi_sel:
        st.markdown("## 📈 Andamento KPI Selezionati")
        df_kpi_filtered = df_kpi_finale[df_kpi_finale["Anno"].isin(anni_sel)]
        for kpi in kpi_sel:
            fig_kpi = px.line(df_kpi_filtered, x="Anno", y=kpi, color="Azienda", markers=True, title=f"Andamento {kpi}")
            st.plotly_chart(fig_kpi, use_container_width=True)

    if anni_sel and voci_sel:
        st.markdown("## 🧩 Voci di Bilancio Selezionate")
        df_voci_filtered = df_voci_finale[df_voci_finale["Anno"].isin(anni_sel)]
        for voce in voci_sel:
            fig_voce = px.bar(df_voci_filtered, x="Anno", y=voce, color="Azienda", barmode="group", title=f"{voce} per Anno e Azienda")
            st.plotly_chart(fig_voce, use_container_width=True)

    st.markdown("## 🏆 Classifica Aziende per Indice Sintetico")
    classifica_df = df_kpi_finale.groupby("Azienda")["Indice Sintetico"].mean().sort_values(ascending=False).reset_index()
    fig_score = px.bar(classifica_df, x="Azienda", y="Indice Sintetico", text="Indice Sintetico", title="Indice medio sintetico per Azienda")
    st.plotly_chart(fig_score, use_container_width=True)
    top_azienda = classifica_df.iloc[0]["Azienda"]
    st.caption("L’indice sintetico rappresenta la media normalizzata dei principali KPI rispetto ai benchmark: un valore > 10 indica performance superiori alla media attesa.")
    st.success(f"🏅 L’azienda con la miglior solidità media è: {top_azienda}")

    st.markdown("## 📤 Esporta report")
    buffer_xlsx = BytesIO()
    with pd.ExcelWriter(buffer_xlsx, engine='xlsxwriter') as writer:
        df_kpi_finale.to_excel(writer, sheet_name="KPI", index=False)
        df_voci_finale.to_excel(writer, sheet_name="Bilancio", index=False)
    st.download_button("📥 Scarica Excel", buffer_xlsx.getvalue(), "report_finanziario.xlsx")

    def genera_pdf(df, logo_path="A_logo_for_Andrea_Bozzo_is_depicted_in_the_image,_.png"):
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        if os.path.exists(logo_path):
            c.drawImage(logo_path, 2 * cm, height - 3.5 * cm, width=3 * cm)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(6 * cm, height - 2.5 * cm, "Report Finanziario PMI")
        y = height - 4.5 * cm
        c.setFont("Helvetica", 11)
        for _, row in df.sort_values("Anno").iterrows():
            for voce in ["Anno", "Azienda", "EBITDA Margin", "ROE", "ROI", "Current Ratio", "Indice Sintetico", "Valutazione"]:
                c.drawString(2 * cm, y, f"{voce}: {row[voce]}")
                y -= 0.6 * cm
            y -= 0.4 * cm
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

    pdf_buffer = genera_pdf(df_kpi_finale)
    st.download_button("📄 Scarica PDF", pdf_buffer, "report_finanziario.pdf")
