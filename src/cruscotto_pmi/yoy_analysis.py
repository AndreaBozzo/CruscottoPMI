import pandas as pd
import streamlit as st

@st.cache_data(show_spinner=False)
def genera_df_yoy(df1, df2, anno1, anno2, azienda="Sconosciuta"):
    try:
        ce1, ce2 = df1[df1["Tipo"] == "Conto Economico"], df2[df2["Tipo"] == "Conto Economico"]
        df_yoy = ce1.merge(ce2, on="Voce", suffixes=(f" {anno1}", f" {anno2}"))
        df_yoy["Anno Precedente"] = df_yoy[f"Importo (€) {anno1}"]
        df_yoy["Anno Attuale"] = df_yoy[f"Importo (€) {anno2}"]
        df_yoy["Variazione %"] = ((df_yoy["Anno Attuale"] - df_yoy["Anno Precedente"]) / df_yoy["Anno Precedente"]) * 100
        df_yoy["Azienda"] = azienda
        return df_yoy[["Azienda", "Voce", "Anno Precedente", "Anno Attuale", "Variazione %"]]
    except:
        return pd.DataFrame()