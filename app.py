# Cruscotto Finanziario per PMI – Build completa con YoY, benchmark, filtri, export

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

# ─── Input iniziali ──────────────────────────────────
demo_mode = st.checkbox("🔍 Usa dati di esempio", value=False)
benchmark_file = st.file_uploader("Carica file CSV benchmark (facoltativo)", type=["csv"])
uploaded_files = (
    st.file_uploader(
        "Carica uno o più file Excel del bilancio (uno per anno)",
        type=["xlsx"], accept_multiple_files=True
    )
    if not demo_mode else None
)

# Benchmark di default
benchmark = {"EBITDA Margin": 15.0, "ROE": 10.0, "ROI": 8.0, "Current Ratio": 1.3}
if benchmark_file is not None:
    df_bm = pd.read_csv(benchmark_file)
    benchmark = {row["KPI"]: row["Valore"] for _, row in df_bm.iterrows()}

kpi_cols = ["EBITDA Margin", "ROE", "ROI", "Current Ratio"]
tabella_kpi, tabella_voci, bilanci = [], [], {}

# ─── Caricamento dati reali ──────────────────────────
if not demo_mode and uploaded_files:
    for file in uploaded_files:
        try:
            df_ce      = pd.read_excel(file, sheet_name="Conto Economico")
            df_attivo  = pd.read_excel(file, sheet_name="Attivo")
            df_passivo = pd.read_excel(file, sheet_name="Passivo")
            nome       = file.name.replace(".xlsx", "").split("_")
            azienda, anno = (nome + ["Sconosciuta"])[0:2]
            bilanci[(azienda, anno)] = {"ce": df_ce, "attivo": df_attivo, "passivo": df_passivo}
        except Exception as e:
            st.error(f"Errore nel file {file.name}: {e}")

# ─── Modalità demo ───────────────────────────────────
if demo_mode:
    st.info("Modalità demo attiva: dati di esempio caricati.")
    bilanci = {
        ("Alpha Srl", 2022): {
            "ce": pd.DataFrame({"Voce":["Ricavi","Utile netto","EBIT","Spese operative"],"Importo (€)":[1_200_000,85_000,90_000,200_000]}),
            "attivo": pd.DataFrame({"Attività":["Disponibilità liquide"],"Importo (€)":[110_000]}),
            "passivo": pd.DataFrame({"Passività e Patrimonio Netto":["Debiti a breve","Patrimonio netto"],"Importo (€)":[85_000,420_000]})
        },
        ("Beta Spa", 2022): {
            "ce": pd.DataFrame({"Voce":["Ricavi","Utile netto","EBIT","Spese operative"],"Importo (€)":[1_750_000,120_000,130_000,260_000]}),
            "attivo": pd.DataFrame({"Attività":["Disponibilità liquide"],"Importo (€)":[150_000]}),
            "passivo": pd.DataFrame({"Passività e Patrimonio Netto":["Debiti a breve","Patrimonio netto"],"Importo (€)":[120_000,500_000]})
        }
    }

# ─── Elaborazione KPI e voci di bilancio ─────────────
for (azienda, anno), d in sorted(bilanci.items()):
    try:
        df_ce, df_att, df_pas = d["ce"], d["attivo"], d["passivo"]
        ricavi       = df_ce.loc[df_ce["Voce"]=="Ricavi","Importo (€)"].values[0]
        utile_netto  = df_ce.loc[df_ce["Voce"]=="Utile netto","Importo (€)"].values[0]
        ebit         = df_ce.loc[df_ce["Voce"]=="EBIT","Importo (€)"].values[0]
        spese_oper   = df_ce.loc[df_ce["Voce"]=="Spese operative","Importo (€)"].values[0]
        ammortamenti = df_ce.loc[df_ce["Voce"]=="Ammortamenti","Importo (€)"].values[0] if "Ammortamenti" in df_ce["Voce"].values else 0
        oneri_fin    = df_ce.loc[df_ce["Voce"]=="Oneri finanziari","Importo (€)"].values[0] if "Oneri finanziari" in df_ce["Voce"].values else 0
        mol          = ricavi - spese_oper
        liquidita    = df_att.loc[df_att["Attività"]=="Disponibilità liquide","Importo (€)"].values[0]
        debiti_brevi = df_pas.loc[df_pas["Passività e Patrimonio Netto"]=="Debiti a breve","Importo (€)"].values[0]
        patrimonio   = df_pas.loc[df_pas["Passività e Patrimonio Netto"]=="Patrimonio netto","Importo (€)"].values[0]
        totale_att   = df_att["Importo (€)"].sum()

        ebitda  = ebit + spese_oper
        eda_m   = round(ebitda / ricavi * 100, 2)
        roe     = round(utile_netto / patrimonio * 100, 2)
        roi     = round(ebit / totale_att * 100, 2)
        curr_r  = round(liquidita / debiti_brevi, 2)

        valuta = "Ottima solidità ✅"
        if any([eda_m<10, roe<5, roi<5, curr_r<1]): valuta = "⚠️ Alcuni indici critici"
        if all([eda_m<10, roe<5, roi<5, curr_r<1]): valuta = "❌ Situazione critica"

        indice = round(((eda_m/benchmark["EBITDA Margin"] + roe/benchmark["ROE"] + roi/benchmark["ROI"] + curr_r/benchmark["Current Ratio"])/4)*10,1)

        tabella_kpi.append({
            "Azienda": azienda, "Anno": int(anno),
            "EBITDA Margin": eda_m, "Benchmark EBITDA": benchmark["EBITDA Margin"], "Δ EBITDA": eda_m - benchmark["EBITDA Margin"],
            "ROE": roe, "Benchmark ROE": benchmark["ROE"], "Δ ROE": roe - benchmark["ROE"],
            "ROI": roi, "Benchmark ROI": benchmark["ROI"], "Δ ROI": roi - benchmark["ROI"],
            "Current Ratio": curr_r, "Benchmark Current": benchmark["Current Ratio"], "Δ Current": curr_r - benchmark["Current Ratio"],
            "Indice Sintetico": indice, "Valutazione": valuta, "Ricavi": ricavi
        })

        tabella_voci.append({
            "Azienda": azienda, "Anno": anno, "Ricavi": ricavi, "EBIT": ebit,
            "Spese Operative": spese_oper, "Ammortamenti": ammortamenti, "Oneri Finanziari": oneri_fin,
            "MOL": mol, "Totale Attivo": totale_att, "Patrimonio Netto": patrimonio,
            "Liquidità": liquidita, "Debiti a Breve": debiti_brevi
        })
    except Exception as e:
        st.warning(f"Errore nell'elaborazione di {azienda} {anno}: {e}")

# ─── Visualizzazione e dashboard ──────────────────────
if tabella_kpi:
    df_kpi = pd.DataFrame(tabella_kpi).sort_values(["Azienda","Anno"])

    # Formattazione sicura
    num_cols = df_kpi.select_dtypes(include="number").columns
    fmt_dict = {c:"{:.2f}" for c in num_cols}
    def evid(row):
        return pd.Series({
            "EBITDA Margin":"background-color:#f8d7da" if row["EBITDA Margin"]<10 else "background-color:#d4edda",
            "ROE":"background-color:#f8d7da" if row["ROE"]<5 else "background-color:#d4edda",
            "ROI":"background-color:#f8d7da" if row["ROI"]<5 else "background-color:#d4edda",
            "Current Ratio":"background-color:#f8d7da" if row["Current Ratio"]<1 else "background-color:#d4edda"
        })
    st.dataframe(df_kpi.style.format(fmt_dict, na_rep="-").apply(evid, axis=1), use_container_width=True)

    # Δ YoY
    st.markdown("## 📉 Variazione Percentuale YoY")
    yoy = (
        df_kpi.set_index("Anno").groupby("Azienda")[kpi_cols+["Ricavi"]]
        .pct_change().dropna()*100
    ).reset_index().rename(columns={c:f"Δ% {c}" for c in kpi_cols+["Ricavi"]})
    st.dataframe(yoy, use_container_width=True)

    # Classifica
    st.markdown("## 🏆 Classifica Indice Sintetico")
    cls = df_kpi.groupby("Azienda")['Indice Sintetico'].mean().sort_values(ascending=False).reset_index()
    st.plotly_chart(px.bar(cls,x="Azienda",y="Indice Sintetico",text="Indice Sintetico"),use_container_width=True)

    # Sidebar filtri
    st.sidebar.markdown("## 🔍 Filtri")
    anni = sorted(df_kpi['Anno'].unique())
    ksel = st.sidebar.multiselect("KPI", kpi_cols, default=kpi_cols)
    asel = st.sidebar.multiselect("Anno", anni, default=anni)

    if asel and ksel:
        st.markdown("## 📊 KPI selezionati")
        dfp = df_kpi[df_kpi['Anno'].isin(asel)]
        for k in ksel:
            st.plotly_chart(px.line(dfp,x="Anno",y=k,color="Azienda",markers=True,title=k),use_container_width=True)

    # Voci bilancio
    df_voci = pd.DataFrame(tabella_voci)
    vcols = [c for c in df_voci.columns if c not in ("Azienda","Anno")]
    vsel  = st.sidebar.multiselect("Voci bilancio", vcols, default=["Ricavi","EBIT"])
    if asel and vsel:
        st.markdown("## 📊 Voci di Bilancio")
        dfb = df_voci[df_voci['Anno'].isin(asel)]
        for v in vsel:
            st.plotly_chart(px.bar(dfb,x="Anno",y=v,color="Azienda",barmode="group",title=v),use_container_width=True)

    # Export Excel
    buf_x = BytesIO()
    with pd.ExcelWriter(buf_x, engine="xlsxwriter") as w:
        df_kpi.to_excel(w, "KPI", index=False)
        yoy.to_excel(w, "Δ_YoY", index=False)
    st.download_button("📥 Excel", buf_x.getvalue(), "report_finanziario.xlsx")

    # Export PDF
    def g_pdf(df, logo="A_logo_for_Andrea_Bozzo_is_depicted_in_the_image,_.png"):
        buf = BytesIO()
        c = canvas.Canvas(buf, pagesize=A4)
        w, h = A4
        if os.path.exists(logo):
            c.drawImage(logo, 2 * cm, h - 3.5 * cm, 3 * cm, 3 * cm, mask="auto")
        c.setFont("Helvetica-Bold", 16)
        c.drawString(6 * cm, h - 2.5 * cm, "Report Finanziario PMI")
        y = h - 4.5 * cm
        c.setFont("Helvetica", 11)
        for _, r in df.sort_values("Anno").iterrows():
            for v in [
                "Anno",
                "Azienda",
                "EBITDA Margin",
                "ROE",
                "ROI",
                "Current Ratio",
                "Indice Sintetico",
                "Valutazione",
            ]:
                c.drawString(2 * cm, y, f"{v}: {r[v]}")
                y -= 0.6 * cm
            y -= 0.4 * cm
            if y < 5 * cm:
                c.setFont("Helvetica-Oblique", 8)
                c.drawString(2 * cm, 2 * cm, "© 2025 Andrea Bozzo – Cruscotto PMI")
                c.showPage()
                y = h - 4.5 * cm
                c.setFont("Helvetica", 11)
        c.setFont("Helvetica-Oblique", 8)
        c.drawString(2 * cm, 2 * cm, "© 2025 Andrea Bozzo – Cruscotto PMI")
        c.save()
        buf.seek(0)
        return buf

    st.download_button("📄 PDF", g_pdf(df_kpi), "report_finanziario.pdf")

