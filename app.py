# Cruscotto Finanziario per PMI – Build completa con YoY, benchmark, cache, filtri, export

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

# ─── INPUT ───

demo_mode = st.checkbox("🔍 Usa dati di esempio", value=False)
benchmark_file = st.file_uploader("Carica file CSV benchmark (facoltativo)", type=["csv"])
uploaded_files = (
    st.file_uploader(
        "Carica uno o più file Excel del bilancio (uno per anno)",
        type=["xlsx"], accept_multiple_files=True
    )
    if not demo_mode else None
)

# ─── FUNZIONI CACHATE ───

@st.cache_data(show_spinner=False)
def load_benchmark(file):
    if file is None:
        return {"EBITDA Margin": 15.0, "ROE": 10.0, "ROI": 8.0, "Current Ratio": 1.3}
    df_bm = pd.read_csv(file)
    return {row["KPI"]: row["Valore"] for _, row in df_bm.iterrows()}

@st.cache_data(show_spinner=False)
def load_excel(xlsx):
    ce      = pd.read_excel(xlsx, sheet_name="Conto Economico")
    attivo  = pd.read_excel(xlsx, sheet_name="Attivo")
    passivo = pd.read_excel(xlsx, sheet_name="Passivo")
    return ce, attivo, passivo

@st.cache_data(show_spinner=False)
def calcola_kpi(ce, att, pas, benchmark):
    try:
        ricavi       = ce.loc[ce["Voce"]=="Ricavi","Importo (€)"].values[0]
        utile_netto  = ce.loc[ce["Voce"]=="Utile netto","Importo (€)"].values[0]
        ebit         = ce.loc[ce["Voce"]=="EBIT","Importo (€)"].values[0]
        spese_oper   = ce.loc[ce["Voce"]=="Spese operative","Importo (€)"].values[0]
        ammortamenti = ce.loc[ce["Voce"]=="Ammortamenti","Importo (€)"].values[0] if "Ammortamenti" in ce["Voce"].values else 0
        oneri_fin    = ce.loc[ce["Voce"]=="Oneri finanziari","Importo (€)"].values[0] if "Oneri finanziari" in ce["Voce"].values else 0
        mol          = ricavi - spese_oper
        liquidita    = att.loc[att["Attività"]=="Disponibilità liquide","Importo (€)"].values[0]
        debiti_brevi = pas.loc[pas["Passività e Patrimonio Netto"]=="Debiti a breve","Importo (€)"].values[0]
        patrimonio   = pas.loc[pas["Passività e Patrimonio Netto"]=="Patrimonio netto","Importo (€)"].values[0]
        totale_att   = att["Importo (€)"].sum()

        ebitda = ebit + spese_oper
        eda_m  = round(ebitda/ricavi*100,2)
        roe    = round(utile_netto/patrimonio*100,2)
        roi    = round(ebit/totale_att*100,2)
        curr_r = round(liquidita/debiti_brevi,2)
        indice = round(((eda_m/benchmark["EBITDA Margin"] + roe/benchmark["ROE"] + roi/benchmark["ROI"] + curr_r/benchmark["Current Ratio"]) / 4) * 10, 1)
        valut  = "Ottima solidità ✅"
        if any([eda_m<10, roe<5, roi<5, curr_r<1]): valut="⚠️ Alcuni indici critici"
        if all([eda_m<10, roe<5, roi<5, curr_r<1]): valut="❌ Situazione critica"
        return {
            "EBITDA Margin": eda_m, "ROE": roe, "ROI": roi, "Current Ratio": curr_r,
            "Indice Sintetico": indice, "Valutazione": valut,
            "Ricavi": ricavi, "EBIT": ebit, "Spese Operative": spese_oper,
            "Ammortamenti": ammortamenti, "Oneri Finanziari": oneri_fin,
            "MOL": mol, "Totale Attivo": totale_att, "Patrimonio Netto": patrimonio,
            "Liquidità": liquidita, "Debiti a Breve": debiti_brevi
        }
    except Exception as ex:
        return {"Errore": str(ex)}

# ─── ELABORAZIONE DATI ───
benchmark = load_benchmark(benchmark_file)
kpi_cols = ["EBITDA Margin", "ROE", "ROI", "Current Ratio"]
tabella_kpi, tabella_voci, bilanci = [], [], {}

if not demo_mode and uploaded_files:
    for f in uploaded_files:
        try:
            ce, att, pas = load_excel(f)
            name_parts = f.name.replace(".xlsx", "").split("_")
            azi, yr = (name_parts + ["Sconosciuta"])[0:2]
            bilanci[(azi, yr)] = {"ce": ce, "attivo": att, "passivo": pas}
        except Exception as e:
            st.error(f"Errore nel file {f.name}: {e}")

if demo_mode:
    st.info("Modalità demo: dati di esempio caricati.")
    demo_ce = pd.DataFrame({
        "Voce": ["Ricavi", "Utile netto", "EBIT", "Spese operative"],
        "Importo (€)": [1_200_000, 85_000, 90_000, 200_000],
    })
    demo_att = pd.DataFrame({
        "Attività": ["Disponibilità liquide"],
        "Importo (€)": [110_000],
    })
    demo_pas = pd.DataFrame({
        "Passività e Patrimonio Netto": ["Debiti a breve", "Patrimonio netto"],
        "Importo (€)": [85_000, 420_000],
    })
    bilanci = {
        ("Alpha Srl", 2022): {"ce": demo_ce, "attivo": demo_att, "passivo": demo_pas},
    }

for (azi, yr), dfs in bilanci.items():
    row = calcola_kpi(dfs["ce"], dfs["attivo"], dfs["passivo"], benchmark)
    if "Errore" in row:
        st.warning(f"Errore su {azi} {yr}: {row['Errore']}")
        continue
    row.update({"Azienda": azi, "Anno": int(yr)})
    tabella_kpi.append(row)
    tabella_voci.append({k: row[k] for k in row if k not in kpi_cols + ["Indice Sintetico","Valutazione","Azienda","Anno"]})

# ─── DASHBOARD ───

if tabella_kpi:
    df_kpi = pd.DataFrame(tabella_kpi)
    df_kpi.sort_values(["Azienda", "Anno"], inplace=True)
    num_cols = df_kpi.select_dtypes(include="number").columns
    fmt_dict = {c: "{:.2f}" for c in num_cols}

    def evid(row):
        return pd.Series({
            "EBITDA Margin":"background-color:#f8d7da" if row["EBITDA Margin"]<10 else "background-color:#d4edda",
            "ROE":"background-color:#f8d7da" if row["ROE"]<5 else "background-color:#d4edda",
            "ROI":"background-color:#f8d7da" if row["ROI"]<5 else "background-color:#d4edda",
            "Current Ratio":"background-color:#f8d7da" if row["Current Ratio"]<1 else "background-color:#d4edda"
        })

    st.markdown("## 📜 KPI con Evidenziazione Condizionale")
    st.dataframe(df_kpi.style.format(fmt_dict).apply(evid, axis=1), use_container_width=True)

    st.markdown("## 📉 Variazione Percentuale YoY")
    
    yoy = (
    df_kpi
    .sort_values(["Azienda", "Anno"])
    .groupby("Azienda", group_keys=False)[["Anno"] + kpi_cols + ["Ricavi"]]
    .apply(lambda g: g.set_index("Anno").pct_change().dropna().reset_index())
    .reset_index(drop=True)
    .rename(columns={c: f"Δ% {c}" for c in kpi_cols + ["Ricavi"]})
    )

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
    if "Anno" in df_voci.columns:
    dfb = df_voci[df_voci['Anno'].isin(asel)]
    else:
    st.warning("La colonna 'Anno' non è presente in df_voci.")
    st.write("Colonne disponibili:", df_voci.columns.tolist())

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

