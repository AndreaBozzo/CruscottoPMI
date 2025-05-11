import pandas as pd
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
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
        ...

