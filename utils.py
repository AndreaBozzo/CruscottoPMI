import pandas as pd
import streamlit as st

@st.cache_data(show_spinner=False)
def load_excel(file):
    ce = pd.read_excel(file, sheet_name="Conto Economico")
    att = pd.read_excel(file, sheet_name="Attivo")
    pas = pd.read_excel(file, sheet_name="Passivo")
    return ce, att, pas

@st.cache_data(show_spinner=False)
def load_benchmark(file, default_benchmark):
    if file is None:
        return default_benchmark.copy()
    df_bm = pd.read_csv(file)
    return {row["KPI"]: row["Valore"] for _, row in df_bm.iterrows()}

def calcola_kpi(ce, att, pas, benchmark):
    try:
        ricavi       = ce.loc[ce["Voce"] == "Ricavi", "Importo (€)"].values[0]
        utile_netto  = ce.loc[ce["Voce"] == "Utile netto", "Importo (€)"].values[0]
        ebit         = ce.loc[ce["Voce"] == "EBIT", "Importo (€)"].values[0]
        spese_oper   = ce.loc[ce["Voce"] == "Spese operative", "Importo (€)"].values[0]
        ammortamenti = ce.loc[ce["Voce"] == "Ammortamenti", "Importo (€)"].values[0] if "Ammortamenti" in ce["Voce"].values else 0
        oneri_fin    = ce.loc[ce["Voce"] == "Oneri finanziari", "Importo (€)"].values[0] if "Oneri finanziari" in ce["Voce"].values else 0
        mol          = ricavi - spese_oper
        liquidita    = att.loc[att["Attività"] == "Disponibilità liquide", "Importo (€)"].values[0]
        debiti_brevi = pas.loc[pas["Passività e Patrimonio Netto"] == "Debiti a breve", "Importo (€)"].values[0]
        patrimonio   = pas.loc[pas["Passività e Patrimonio Netto"] == "Patrimonio netto", "Importo (€)"].values[0]
        totale_att   = att["Importo (€)"].sum()

        ebitda = ebit + spese_oper
        eda_m  = round(ebitda / ricavi * 100, 2)
        roe    = round(utile_netto / patrimonio * 100, 2)
        roi    = round(ebit / totale_att * 100, 2)
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
