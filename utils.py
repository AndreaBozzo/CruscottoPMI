# utils.py - Include funzioni per KPI e YoY

import pandas as pd

def calcola_kpi_completo(ce, att, pas, benchmark):
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
        eda_m  = round(ebitda / ricavi * 100, 2)
        roe    = round(utile_netto / patrimonio * 100, 2)
        roi    = round(ebit / totale_att * 100, 2)
        curr_r = round(liquidita / debiti_brevi, 2)

        indice = round(((eda_m / benchmark["EBITDA Margin"] + roe / benchmark["ROE"] + roi / benchmark["ROI"] + curr_r / benchmark["Current Ratio"]) / 4) * 10, 1)
        valut  = "Ottima solidità ✅"
        if any([eda_m < 10, roe < 5, roi < 5, curr_r < 1]): valut = "⚠️ Alcuni indici critici"
        if all([eda_m < 10, roe < 5, roi < 5, curr_r < 1]): valut = "❌ Situazione critica"

        kpi_row = {
            "EBITDA Margin": eda_m, "ROE": roe, "ROI": roi, "Current Ratio": curr_r,
            "Indice Sintetico": indice, "Valutazione": valut,
            "Ricavi": ricavi, "EBIT": ebit, "Spese Operative": spese_oper,
            "Ammortamenti": ammortamenti, "Oneri Finanziari": oneri_fin,
            "MOL": mol, "Totale Attivo": totale_att, "Patrimonio Netto": patrimonio,
            "Liquidità": liquidita, "Debiti a Breve": debiti_brevi
        }
        return kpi_row
    except Exception as ex:
        return {"Errore": str(ex)}

def calcola_variazioni_yoy(df_kpi, kpi_cols):
    if df_kpi.empty:
        return pd.DataFrame()
    return (
        df_kpi.groupby("Azienda")
        .apply(lambda g: g.sort_values("Anno").set_index("Anno")[kpi_cols + ["Ricavi"]].pct_change().dropna())
        .reset_index()
        .rename(columns={c: f"Δ% {c}" for c in kpi_cols + ["Ricavi"]})
    )
