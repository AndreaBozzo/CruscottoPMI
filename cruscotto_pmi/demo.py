import pandas as pd
import streamlit as st
from cruscotto_pmi.kpi_calculator import calcola_kpi

# KPI da mostrare in demo
KPI_ATTESI = [
    "EBITDA Margin", "ROE", "ROI", "Current Ratio",
    "Indice liquidità", "Indice indebitamento",
    "Equity ratio", "Return on Equity", "Indice Sintetico"
]

# Parametri di base per ogni azienda
AZIENDE_BASE = {
    "DemoCorp": {"rev": 1_000_000, "cost": 700_000, "amm": 50_000, "att": 300_000, "liq": 200_000, "deb": 100_000, "eq": 400_000},
    "AlphaSRL": {"rev": 800_000,   "cost": 550_000, "amm": 40_000, "att": 250_000, "liq": 150_000, "deb":  80_000, "eq": 300_000},
    "BetaSpa":  {"rev": 1_200_000, "cost": 840_000, "amm": 60_000, "att": 360_000, "liq": 240_000, "deb": 120_000, "eq": 480_000},
    "GammaLLP": {"rev": 900_000,   "cost": 630_000, "amm": 45_000, "att": 270_000, "liq": 180_000, "deb":  90_000, "eq": 360_000},
}

# Moltiplicatori specifici per (azienda, anno)
MULTIPLIERS = {
    ("DemoCorp", "2020"): 0.7,
    ("DemoCorp", "2021"): 1.0,
    ("DemoCorp", "2022"): 1.3,
    ("AlphaSRL", "2020"): 1.1,
    ("AlphaSRL", "2021"): 0.9,
    ("AlphaSRL", "2022"): 1.2,
    ("BetaSpa",  "2020"): 0.85,
    ("BetaSpa",  "2021"): 1.15,
    ("BetaSpa",  "2022"): 1.05,
    ("GammaLLP","2020"): 1.2,
    ("GammaLLP","2021"): 0.95,
    ("GammaLLP","2022"): 1.0,
}

# Benchmark di riferimento
BENCHMARK_DEFAULT = {
    "Indice Sintetico":     60,
    "EBITDA Margin":        20,
    "ROE":                  15,
    "ROI":                  12,
    "Current Ratio":        1.5,
    "Indice liquidità":     2.0,
    "Indice indebitamento": 1.2,
    "Equity ratio":         0.4,
    "Return on Equity":     10
}

def carica_demo_avanzata():
    bilanci_dict = {}
    lista_kpi    = []
    benchmark    = BENCHMARK_DEFAULT.copy()

    for azi, params in AZIENDE_BASE.items():
        for anno in ["2020", "2021", "2022"]:
            mol = MULTIPLIERS.get((azi, anno), 1.0)
            # costruisco il bilancio di base scalato
            df_base = pd.DataFrame([
                {"Voce": "Ricavi",               "Importo (€)": params["rev"] * mol, "Tipo": "Conto Economico"},
                {"Voce": "Costi",                "Importo (€)": params["cost"] * mol, "Tipo": "Conto Economico"},
                {"Voce": "Ammortamenti",         "Importo (€)": params["amm"]  * mol, "Tipo": "Conto Economico"},
                {"Voce": "Immobilizzazioni",     "Importo (€)": params["att"]  * mol, "Tipo": "Attivo"},
                {"Voce": "Liquidità",            "Importo (€)": params["liq"]  * mol, "Tipo": "Attivo"},
                {"Voce": "Debiti Breve Termine", "Importo (€)": params["deb"]  * mol, "Tipo": "Passivo"},
                {"Voce": "Patrimonio Netto",     "Importo (€)": params["eq"]   * mol, "Tipo": "Passivo"},
            ])

            df_ce  = df_base[df_base["Tipo"] == "Conto Economico"].copy()
            df_att = df_base[df_base["Tipo"] == "Attivo"].copy()
            df_pas = df_base[df_base["Tipo"] == "Passivo"].copy()
            df_ce.attrs["azienda"] = azi
            df_ce.attrs["anno"]   = anno

            kpi = calcola_kpi(df_ce, df_att, df_pas, benchmark)

            for key in KPI_ATTESI:
                val = kpi.get(key, 0.0)
                lista_kpi.append({
                    "Azienda": azi,
                    "Anno":     anno,
                    "KPI":      key,
                    "Valore":   float(val) if isinstance(val, (int, float)) else 0.0
                })

            bilanci_dict[(azi, anno)] = {
                "CE":       df_ce,
                "Attivo":   df_att,
                "Passivo":  df_pas,
                "completo": df_base.assign(Azienda=azi, Anno=anno)
            }

    st.session_state["bilanci"]  = bilanci_dict
    st.session_state["benchmark"] = benchmark
    st.session_state["df_kpi"]    = pd.DataFrame(lista_kpi)
