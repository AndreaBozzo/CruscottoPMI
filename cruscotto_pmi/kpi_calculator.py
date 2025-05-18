import pandas as pd
import streamlit as st

def calcola_kpi(ce, att, pas, benchmark):
    try:
        ricavi = ce[ce["Voce"].str.lower().str.contains("ricavi")]["Importo (€)"].sum()
        costi = ce[ce["Voce"].str.lower().str.contains("costi")]["Importo (€)"].sum()
        ebitda = ricavi - costi
        patrimonio = pas[pas["Voce"].str.lower().str.contains("patrimonio")]["Importo (€)"].sum()
        utile = ebitda * 0.6
        capitale_investito = att["Importo (€)"].sum()
        debiti = pas[pas["Voce"].str.lower().str.contains("debiti")]["Importo (€)"].sum()
        liquidita = att[att["Voce"].str.lower().str.contains("liquidità")]["Importo (€)"].sum()
        deb_brevi = pas[pas["Voce"].str.lower().str.contains("breve")]["Importo (€)"].sum()
        tot_attivo = att["Importo (€)"].sum()

        kpi = {
            "EBITDA Margin": round(ebitda / ricavi * 100, 2) if ricavi else 0,
            "ROE": round(utile / patrimonio * 100, 2) if patrimonio else 0,
            "ROI": round(ebitda / capitale_investito * 100, 2) if capitale_investito else 0,
            "Current Ratio": round(att["Importo (€)"].sum() / pas["Importo (€)"].sum(), 2) if pas["Importo (€)"].sum() else 0,
        }

        # KPI strutturali aggiuntivi per Gauge
        kpi["Indice liquidità"] = round(liquidita / deb_brevi, 2) if deb_brevi else 0
        kpi["Indice indebitamento"] = round((tot_attivo - patrimonio) / patrimonio, 2) if patrimonio else 0
        kpi["Equity ratio"] = round(patrimonio / tot_attivo, 2) if tot_attivo else 0
        kpi["Return on Equity"] = round(utile / patrimonio * 100, 2) if patrimonio else 0

        # Indice sintetico: media dei KPI validi
        valori_utili = [v for v in kpi.values() if isinstance(v, (int, float))]
        if len(valori_utili) >= 3:
            kpi["Indice Sintetico"] = round(sum(valori_utili) / len(valori_utili), 2)
        else:
            kpi["Indice Sintetico"] = None

        # Aggiunta robusta dei metadati Azienda/Anno
        kpi["Azienda"] = ce.attrs.get("azienda", "Sconosciuta")
        kpi["Anno"] = ce.attrs.get("anno", "N/A")
        return kpi

    except Exception as e:
        st.warning(f"Errore durante il calcolo KPI: {e}")
        return {
            "Azienda": ce.attrs.get("azienda", "Sconosciuta"),
            "Anno": ce.attrs.get("anno", "N/A"),
            "Indice Sintetico": None,
            "Errore": str(e)
        }