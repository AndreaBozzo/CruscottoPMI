# utils.py
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

default_benchmark = {"EBITDA Margin": 15.0, "ROE": 10.0, "ROI": 8.0, "Current Ratio": 1.3}

@st.cache_data(show_spinner=False)
def load_benchmark(file, default_benchmark):
    if file is None:
        return default_benchmark.copy()
    df_bm = pd.read_csv(file)
    return {row["KPI"]: row["Valore"] for _, row in df_bm.iterrows()}

def load_excel(file):
    ce = pd.read_excel(file, sheet_name="Conto Economico")
    att = pd.read_excel(file, sheet_name="Attivo")
    pas = pd.read_excel(file, sheet_name="Passivo")
    return ce, att, pas

def calcola_kpi(ce, att, pas, benchmark):
    try:
        ricavi = ce.loc[ce["Voce"]=="Ricavi","Importo (€)"].values[0]
        utile_netto = ce.loc[ce["Voce"]=="Utile netto","Importo (€)"].values[0]
        ebit = ce.loc[ce["Voce"]=="EBIT","Importo (€)"].values[0]
        spese_oper = ce.loc[ce["Voce"]=="Spese operative","Importo (€)"].values[0]
        ammortamenti = ce.loc[ce["Voce"]=="Ammortamenti","Importo (€)"].values[0] if "Ammortamenti" in ce["Voce"].values else 0
        oneri_fin = ce.loc[ce["Voce"]=="Oneri finanziari","Importo (€)"].values[0] if "Oneri finanziari" in ce["Voce"].values else 0
        mol = ricavi - spese_oper
        liquidita = att.loc[att["Attività"]=="Disponibilità liquide","Importo (€)"].values[0]
        debiti_brevi = pas.loc[pas["Passività e Patrimonio Netto"]=="Debiti a breve","Importo (€)"].values[0]
        patrimonio = pas.loc[pas["Passività e Patrimonio Netto"]=="Patrimonio netto","Importo (€)"].values[0]
        totale_att = att["Importo (€)"].sum()
        ebitda = ebit + spese_oper
        eda_m = round(ebitda/ricavi*100,2)
        roe = round(utile_netto/patrimonio*100,2)
        roi = round(ebit/totale_att*100,2)
        curr_r = round(liquidita/debiti_brevi,2)
        indice = round(((eda_m/benchmark["EBITDA Margin"] + roe/benchmark["ROE"] + roi/benchmark["ROI"] + curr_r/benchmark["Current Ratio"]) / 4) * 10, 1)
        valut = "Ottima solidità ✅"
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

def evidenzia_kpi(row):
    return pd.Series({
        "EBITDA Margin":"background-color:#f8d7da" if row["EBITDA Margin"]<10 else "background-color:#d4edda",
        "ROE":"background-color:#f8d7da" if row["ROE"]<5 else "background-color:#d4edda",
        "ROI":"background-color:#f8d7da" if row["ROI"]<5 else "background-color:#d4edda",
        "Current Ratio":"background-color:#f8d7da" if row["Current Ratio"]<1 else "background-color:#d4edda"
    })

def prepare_kpi_dataframe(tabella_kpi):
    df = pd.DataFrame(tabella_kpi)
    if "Anno" in df.columns:
        df["Anno"] = df["Anno"].astype(int).astype(str)
    return df

def prepare_voci_dataframe(tabella_voci):
    df = pd.DataFrame(tabella_voci)
    if "Anno" in df.columns:
        df["Anno"] = df["Anno"].astype(int).astype(str)
    return df

def calculate_yoy(df_kpi):
    kpi_cols = ["EBITDA Margin", "ROE", "ROI", "Current Ratio", "Indice Sintetico", "Ricavi"]
    return (
        df_kpi.groupby("Azienda")
        .apply(lambda g: g.sort_values("Anno").set_index("Anno")[kpi_cols].pct_change().dropna())
        .reset_index()
        .rename(columns={c: f"Δ% {c}" for c in kpi_cols})
    )

def create_excel_report(df_kpi, df_voci, df_yoy):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df_kpi.to_excel(writer, sheet_name="KPI", index=False)
        df_voci.to_excel(writer, sheet_name="Bilancio", index=False)
        df_yoy.to_excel(writer, sheet_name="Δ YoY", index=False)
    return buffer.getvalue()

def genera_pdf(df):
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2*cm, height - 2*cm, "Report Finanziario PMI")
    c.setFont("Helvetica", 10)
    y = height - 3*cm
    for _, row in df.iterrows():
        for key in ["Azienda", "Anno", "EBITDA Margin", "ROE", "ROI", "Current Ratio", "Indice Sintetico", "Valutazione"]:
            c.drawString(2*cm, y, f"{key}: {row[key]}")
            y -= 0.5*cm
        y -= 0.3*cm
        if y < 4*cm:
            c.showPage()
            y = height - 3*cm
    c.save()
    buf.seek(0)
    return buf
