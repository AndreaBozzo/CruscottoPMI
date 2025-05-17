
import pandas as pd
from cruscotto_pmi.kpi_calculator import calcola_kpi

def carica_demo_avanzata():
    import streamlit as st

    data_demo = [
        {"Voce": "Ricavi", "Importo (€)": 1000000, "Tipo": "Conto Economico"},
        {"Voce": "Costi", "Importo (€)": 700000, "Tipo": "Conto Economico"},
        {"Voce": "Liquidità", "Importo (€)": 100000, "Tipo": "Attivo"},
        {"Voce": "Crediti", "Importo (€)": 80000, "Tipo": "Attivo"},
        {"Voce": "Debiti Breve Termine", "Importo (€)": 60000, "Tipo": "Passivo"},
        {"Voce": "Patrimonio Netto", "Importo (€)": 120000, "Tipo": "Passivo"},
    ]

    df_base = pd.DataFrame(data_demo)
    bilanci_dict = {}

    for azienda, anno, moltiplicatore in [("DemoCorp", "2022", 1.0), ("DemoCorp", "2021", 0.85)]:
        df = df_base.copy()
        df["Importo (€)"] = df["Importo (€)"] * moltiplicatore
        df["Azienda"] = azienda
        df["Anno"] = anno

        df_ce = df[df["Tipo"] == "Conto Economico"]
        df_att = df[df["Tipo"] == "Attivo"]
        df_pas = df[df["Tipo"] == "Passivo"]

        benchmark = {
            "Indice liquidità": 1.2,
            "Indice indebitamento": 1.5,
            "Equity ratio": 0.4,
            "Return on Equity": 10.0
        }

        kpi = calcola_kpi(df_ce, df_att, df_pas, benchmark)
        if "Errore" in kpi:
            continue

        # ⬅️ Calcola indice sintetico solo se possibile
        valori_numerici = [v for v in kpi.values() if isinstance(v, (int, float))]
        if valori_numerici:
            kpi["Indice Sintetico"] = round(sum(valori_numerici) / len(valori_numerici), 2)

        kpi.update({"Azienda": azienda, "Anno": anno})

        for voce_kpi in ["Indice liquidità", "Indice indebitamento", "Equity ratio", "Return on Equity", "Indice Sintetico"]:
            if voce_kpi in kpi:
                df = pd.concat([
                    df,
                    pd.DataFrame.from_records([{
                        "Voce": voce_kpi,
                        "Importo (€)": kpi[voce_kpi],
                        "Tipo": "KPI",
                        "Azienda": azienda,
                        "Anno": anno
                    }])
                ], ignore_index=True)

        bilanci_dict[(azienda, anno)] = df

    st.session_state["bilanci"] = bilanci_dict
    st.session_state["benchmark"] = benchmark
