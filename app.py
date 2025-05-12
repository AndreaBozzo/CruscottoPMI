import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from utils import load_excel, calcola_kpi, load_benchmark

st.set_page_config(page_title="Cruscotto Finanziario PMI", layout="wide")
st.title("📊 Cruscotto Finanziario per PMI")

# ─── INPUT ─────────────────────────────────────────────
demo_mode = st.checkbox("🔍 Usa dati di esempio", value=False)
benchmark_file = st.file_uploader("Carica file CSV benchmark (facoltativo)", type=["csv"])
uploaded_files = (
    st.file_uploader(
        "Carica uno o più file Excel del bilancio (uno per anno)",
        type=["xlsx"], accept_multiple_files=True
    )
    if not demo_mode else None
)

# ─── BENCHMARK DI DEFAULT E EDITOR ─────────────────────
default_benchmark = {"EBITDA Margin": 15.0, "ROE": 10.0, "ROI": 8.0, "Current Ratio": 1.3}
benchmark = load_benchmark(benchmark_file, default_benchmark)

st.sidebar.markdown("## ⚙️ Modifica Benchmark")
for kpi in benchmark:
    benchmark[kpi] = st.sidebar.number_input(kpi, value=float(benchmark[kpi]), step=0.1)

# ─── ELABORAZIONE ─────────────────────────────────────
kpi_cols = ["EBITDA Margin", "ROE", "ROI", "Current Ratio"]
tabella_kpi, tabella_voci, bilanci = [], [], {}

if demo_mode:
    st.info("Modalità demo: dati di esempio caricati.")
    demo_ce = pd.DataFrame({
        "Voce": ["Ricavi", "Utile netto", "EBIT", "Spese operative", "Ammortamenti", "Oneri finanziari"],
        "Importo (€)": [1_200_000, 85_000, 90_000, 200_000, 15_000, 10_000],
    })
    demo_att = pd.DataFrame({"Attività": ["Disponibilità liquide"], "Importo (€)": [110_000]})
    demo_pas = pd.DataFrame({
        "Passività e Patrimonio Netto": ["Debiti a breve", "Patrimonio netto"],
        "Importo (€)": [85_000, 420_000]
    })
    bilanci = {
        ("Alpha Srl", 2022): {"ce": demo_ce, "attivo": demo_att, "passivo": demo_pas},
    }

elif uploaded_files:
    for f in uploaded_files:
    try:
        ce, att, pas = load_excel(f)
        name_parts = f.name.replace(".xlsx", "").split("_")
        azi, yr = (name_parts + ["Sconosciuta"])[:2]
        try:
            anno = int(float(yr))
        except (ValueError, TypeError):
            st.warning(f"⚠️ Anno non valido nel file '{azi}_{yr}': {yr}")
            continue
        bilanci[(azi, anno)] = {"ce": ce, "attivo": att, "passivo": pas}
    except Exception as e:
        st.error(f"Errore nel file {f.name}: {e}")

            
# Funzione per il calcolo dei KPI
@st.cache_data(show_spinner=False)
def calcola_kpi(ce, att, pas, benchmark):
    try:
        ricavi = ce.loc[ce["Voce"] == "Ricavi", "Importo (€)"].values[0]
        utile_netto = ce.loc[ce["Voce"] == "Utile netto", "Importo (€)"].values[0]
        ebit = ce.loc[ce["Voce"] == "EBIT", "Importo (€)"].values[0]
        spese_oper = ce.loc[ce["Voce"] == "Spese operative", "Importo (€)"].values[0]
        ammortamenti = ce.loc[ce["Voce"] == "Ammortamenti", "Importo (€)"].values[0] if "Ammortamenti" in ce["Voce"].values else 0
        oneri_fin = ce.loc[ce["Voce"] == "Oneri finanziari", "Importo (€)"].values[0] if "Oneri finanziari" in ce["Voce"].values else 0
        mol = ricavi - spese_oper
        liquidita = att.loc[att["Attività"] == "Disponibilità liquide", "Importo (€)"].values[0]
        debiti_brevi = pas.loc[pas["Passività e Patrimonio Netto"] == "Debiti a breve", "Importo (€)"].values[0]
        patrimonio = pas.loc[pas["Passività e Patrimonio Netto"] == "Patrimonio netto", "Importo (€)"].values[0]
        totale_att = att["Importo (€)"].sum()

        ebitda = ebit + spese_oper
        eda_m = round(ebitda / ricavi * 100, 2)
        roe = round(utile_netto / patrimonio * 100, 2)
        roi = round(ebit / totale_att * 100, 2)
        curr_r = round(liquidita / debiti_brevi, 2)
        indice = round(((eda_m / benchmark["EBITDA Margin"] +
                         roe / benchmark["ROE"] +
                         roi / benchmark["ROI"] +
                         curr_r / benchmark["Current Ratio"]) / 4) * 10, 1)

        valutazione = "Ottima solidità ✅"
        if any([eda_m < 10, roe < 5, roi < 5, curr_r < 1]):
            valutazione = "⚠️ Alcuni indici critici"
        if all([eda_m < 10, roe < 5, roi < 5, curr_r < 1]):
            valutazione = "❌ Situazione critica"

        kpi_row = {
            "EBITDA Margin": eda_m, "ROE": roe, "ROI": roi, "Current Ratio": curr_r,
            "Indice Sintetico": indice, "Valutazione": valutazione,
            "Ricavi": ricavi, "EBIT": ebit, "Spese Operative": spese_oper,
            "Ammortamenti": ammortamenti, "Oneri Finanziari": oneri_fin,
            "MOL": mol, "Totale Attivo": totale_att, "Patrimonio Netto": patrimonio,
            "Liquidità": liquidita, "Debiti a Breve": debiti_brevi
        }

        return kpi_row
    except Exception as e:
        return {"Errore": str(e)}

# Calcola i KPI per ciascun bilancio
for (azi, yr), dfs in bilanci.items():
    row = calcola_kpi(dfs["ce"], dfs["attivo"], dfs["passivo"], benchmark)
    if "Errore" in row:
        st.warning(f"Errore su {azi} {yr}: {row['Errore']}")
        continue
    row.update({"Azienda": azi, "Anno": int(float(yr))})
    tabella_kpi.append(row)
    tabella_voci.append({"Azienda": azi, "Anno": int(float(yr)), **{k: row[k] for k in row if k not in kpi_cols + ["Indice Sintetico", "Valutazione", "Azienda", "Anno"]}})

df_kpi = pd.DataFrame(tabella_kpi)
df_voci = pd.DataFrame(tabella_voci)

# Forza Anno a int per evitare visualizzazione decimale
if not df_kpi.empty and "Anno" in df_kpi.columns:
    df_kpi["Anno"] = df_kpi["Anno"].astype(int).astype(str)

if not df_voci.empty and "Anno" in df_voci.columns:
    df_voci["Anno"] = df_voci["Anno"].astype(int).astype(str)

# ─── DASHBOARD & EXPORT ───────────────────────────────
if not df_kpi.empty:
    df_kpi.sort_values(["Azienda", "Anno"], inplace=True)
    num_cols = df_kpi.select_dtypes(include="number").columns
    fmt_dict = {c: "{:.2f}" for c in num_cols}

    def evid(row):
        return pd.Series({
            "EBITDA Margin": "background-color: #f8d7da" if row["EBITDA Margin"] < 10 else "background-color: #d4edda",
            "ROE": "background-color: #f8d7da" if row["ROE"] < 5 else "background-color: #d4edda",
            "ROI": "background-color: #f8d7da" if row["ROI"] < 5 else "background-color: #d4edda",
            "Current Ratio": "background-color: #f8d7da" if row["Current Ratio"] < 1 else "background-color: #d4edda"
        })

    st.dataframe(df_kpi.style.format(fmt_dict).apply(evid, axis=1), use_container_width=True)

    yoy = (
        df_kpi.groupby("Azienda")
        .apply(lambda g: g.sort_values("Anno").set_index("Anno")[kpi_cols + ["Ricavi"]].pct_change().dropna())
        .reset_index()
        .rename(columns={c: f"Δ% {c}" for c in kpi_cols + ["Ricavi"]})
    )

    st.dataframe(yoy, use_container_width=True)

    # ─── CONFRONTO VOCI DI BILANCIO ───────────────────────
    st.markdown("## 📘 Confronto voci di bilancio")
    asel = st.multiselect("Filtra per anno", df_voci["Anno"].unique(), default=df_voci["Anno"].unique())
    vs = st.multiselect("Seleziona voci da confrontare", [c for c in df_voci.columns if c not in ["Azienda", "Anno"]], default=["Ricavi", "EBIT"])
    if asel and vs:
        dfb = df_voci[df_voci['Anno'].isin(asel)]
        for v in vs:
            fig = px.bar(dfb, x="Azienda", y=v, color="Anno", barmode="group", title=f"{v} per azienda e anno")
            st.plotly_chart(fig, use_container_width=True)

    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df_kpi.to_excel(writer, sheet_name="KPI", index=False)
        df_voci.to_excel(writer, sheet_name="Bilancio", index=False)
        yoy.to_excel(writer, sheet_name="Δ YoY", index=False)
    st.download_button("📥 Scarica Excel", buffer.getvalue(), file_name="cruscotto_finanziario.xlsx")

    # ─── EXPORT PDF ──────────────────────────────────────
    def genera_pdf(df):
        buf = BytesIO()
        c = canvas.Canvas(buf, pagesize=A4)
        width, height = A4
        c.setFont("Helvetica-Bold", 16)
        c.drawString(2 * cm, height - 2 * cm, "Report Finanziario PMI")
        c.setFont("Helvetica", 10)
        y = height - 3 * cm
        for _, row in df.iterrows():
            for key in ["Azienda", "Anno"] + kpi_cols + ["Indice Sintetico", "Valutazione"]:
                c.drawString(2 * cm, y, f"{key}: {row[key]}")
                y -= 0.5 * cm
            y -= 0.3 * cm
            if y < 4 * cm:
                c.showPage()
                y = height - 3 * cm
        c.save()
        buf.seek(0)
        return buf

    pdf_buf = genera_pdf(df_kpi)
    st.download_button("📄 Scarica PDF", pdf_buf, file_name="report_finanziario.pdf")
