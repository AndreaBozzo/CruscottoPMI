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
    def get_val(df, voce_col, voce_name):
        subset = df[df[voce_col] == voce_name]
        return subset["Importo (€)"].values[0] if not subset.empty else 0

    try:
        ricavi       = get_val(ce, "Voce", "Ricavi")
        utile_netto  = get_val(ce, "Voce", "Utile netto")
        ebit         = get_val(ce, "Voce", "EBIT")
        spese_oper   = get_val(ce, "Voce", "Spese operative")
        ammortamenti = get_val(ce, "Voce", "Ammortamenti")
        oneri_fin    = get_val(ce, "Voce", "Oneri finanziari")
        mol          = ricavi - spese_oper

        liquidita    = get_val(att, "Attività", "Disponibilità liquide")
        debiti_brevi = get_val(pas, "Passività e Patrimonio Netto", "Debiti a breve")
        patrimonio   = get_val(pas, "Passività e Patrimonio Netto", "Patrimonio netto")
        totale_att   = att["Importo (€)"].sum()

        if any(v == 0 for v in [ricavi, patrimonio, totale_att, debiti_brevi]):
            return {"Errore": "Uno o più valori chiave sono zero o mancanti."}

        ebitda = ebit + spese_oper
        eda_m  = round(ebitda / ricavi * 100, 2)
        roe    = round(utile_netto / patrimonio * 100, 2)
        roi    = round(ebit / totale_att * 100, 2)
        curr_r = round(liquidita / debiti_brevi, 2)

        indice = round(((eda_m / benchmark.get("EBITDA Margin", 1)) +
                        (roe / benchmark.get("ROE", 1)) +
                        (roi / benchmark.get("ROI", 1)) +
                        (curr_r / benchmark.get("Current Ratio", 1))) / 4 * 10, 1)

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