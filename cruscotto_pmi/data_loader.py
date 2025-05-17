import pandas as pd
import streamlit as st

@st.cache_data(show_spinner=False)
def load_excel(file):
    nome_file = file.name.replace(".xlsx", "")
    try:
        azienda, anno = nome_file.split("_")
    except:
        azienda, anno = "Sconosciuta", "Anno?"

    try:
        xls = pd.ExcelFile(file)
        fogli_validi = [s for s in xls.sheet_names if s.lower() in ["attivo", "passivo", "conto economico"]]

        df_finale = pd.DataFrame()
        for foglio in fogli_validi:
            df_temp = pd.read_excel(xls, sheet_name=foglio)
            df_temp["Tipo"] = foglio  # es: "Attivo"
            df_temp["Azienda"] = azienda
            df_temp["Anno"] = anno
            df_finale = pd.concat([df_finale, df_temp], ignore_index=True)

        return df_finale

    except Exception as e:
        print(f"Errore nel caricamento del file {file.name}: {e}")
        return None

import pandas as pd

def load_benchmark(file, default):
    if file is not None:
        try:
            df = pd.read_csv(file)
            if "KPI" in df.columns and "Valore" in df.columns:
                return {row["KPI"]: row["Valore"] for _, row in df.iterrows()}
        except Exception as e:
            print(f"Errore nel caricamento benchmark: {e}")
            return default
    return default
