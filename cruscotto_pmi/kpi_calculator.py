import pandas as pd
import streamlit as st

def calcola_kpi(ce, att, pas, benchmark, azienda=None, anno=None):
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
            "Indice liquidità": round(liquidita / deb_brevi, 2) if deb_brevi else 0,
            "Indice indebitamento": round((tot_attivo - patrimonio) / patrimonio, 2) if patrimonio else 0,
            "Equity ratio": round(patrimonio / tot_attivo, 2) if tot_attivo else 0,
            "Return on Equity": round(utile / patrimonio * 100, 2) if patrimonio else 0
        }

        valori_utili = [v for v in kpi.values() if isinstance(v, (int, float))]
        kpi["Indice Sintetico"] = round(sum(valori_utili) / len(valori_utili), 2) if len(valori_utili) >= 3 else None

        kpi["Azienda"] = azienda or "Sconosciuta"
        kpi["Anno"] = anno or "N/A"
        return kpi

    except Exception as e:
        st.warning(f"Errore durante il calcolo KPI: {e}")
        return {
            "Azienda": azienda or "Sconosciuta",
            "Anno": anno or "N/A",
            "Indice Sintetico": None,
            "Errore": str(e)
        }


def calcola_kpi_sessione(bilanci: dict, benchmark: dict = None) -> pd.DataFrame:
    lista_kpi = []

    for (azienda, anno), dati in bilanci.items():
        ce = dati.get("CE")
        att = dati.get("Attivo")
        pas = dati.get("Passivo")

        if ce is None or att is None or pas is None:
            st.warning(f"❗ Dati incompleti per {azienda} – {anno}")
            continue

        # Chiamata esplicita con metadati
        kpi_raw = calcola_kpi(ce, att, pas, benchmark or {}, azienda=azienda, anno=anno)

        for k, v in kpi_raw.items():
            if k not in ["Azienda", "Anno"]:
                lista_kpi.append({
                    "Azienda": kpi_raw["Azienda"],
                    "Anno": kpi_raw["Anno"],
                    "KPI": k,
                    "Valore": v
                })

    return pd.DataFrame(lista_kpi)
