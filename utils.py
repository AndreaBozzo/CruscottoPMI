# utils.py

import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from io import BytesIO
import os

def load_excel(xlsx):
    ce = pd.read_excel(xlsx, sheet_name="Conto Economico")
    attivo = pd.read_excel(xlsx, sheet_name="Attivo")
    passivo = pd.read_excel(xlsx, sheet_name="Passivo")
    return ce, attivo, passivo

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

        indice = round(((eda_m/benchmark["EBITDA Margin"] +
                         roe/benchmark["ROE"] +
                         roi/benchmark["ROI"] +
                         curr_r/benchmark["Current Ratio"]) / 4) * 10, 1)

        valut  = "Ottima solidità ✅"
        if any([eda_m < 10, roe < 5, roi < 5, curr_r < 1]):
            valut = "⚠️ Alcuni indici critici"
        if all([eda_m < 10, roe < 5, roi < 5, curr_r < 1]):
            valut = "❌ Situazione critica"

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
