import pandas as pd
import streamlit as st
import re

@st.cache_data(show_spinner=False)
def load_excel(file):
    nome_file = file.name.replace(".xlsx", "")
    azienda, anno = estrai_info_da_nome(nome_file)

    try:
        xls = pd.ExcelFile(file)
        st.write(f"DEBUG: Fogli trovati nel file '{file.name}': {xls.sheet_names}")

        df_finale = pd.DataFrame()

        for nome_foglio_originale in xls.sheet_names:
            tipo_foglio = mappa_tipo_foglio(nome_foglio_originale)
            st.write(f"DEBUG: Analizzo foglio '{nome_foglio_originale}', tipo mappato: {tipo_foglio}")
            if tipo_foglio is None:
                st.write(f"DEBUG: Foglio '{nome_foglio_originale}' ignorato perché non rilevante")
                continue  # ignora fogli non rilevanti

            df_temp = pd.read_excel(xls, sheet_name=nome_foglio_originale)
            st.write(f"DEBUG: Righe lette nel foglio '{nome_foglio_originale}': {len(df_temp)}")

            df_temp = pulisci_df(df_temp)
            st.write(f"DEBUG: Righe dopo pulizia foglio '{nome_foglio_originale}': {len(df_temp)}")

            df_temp["Tipo"] = tipo_foglio
            df_temp["Azienda"] = azienda
            df_temp["Anno"] = anno
            df_finale = pd.concat([df_finale, df_temp], ignore_index=True)

        st.write(f"DEBUG: DataFrame finale righe totali: {len(df_finale)}")

        if df_finale.empty:
            st.warning(f"Nessun foglio rilevante trovato in {file.name}.")

        return df_finale

    except Exception as e:
        st.error(f"Errore durante la lettura del file {file.name}: {str(e)}")
        return pd.DataFrame()

def mappa_tipo_foglio(nome):
    nome = nome.lower()
    if "economico" in nome:
        return "CE"
    if "attivo" in nome:
        return "Attivo"
    if "passivo" in nome:
        return "Passivo"
    if "stato patrimoniale" in nome and "attivo" in nome:
        return "Attivo"
    if "stato patrimoniale" in nome and "passivo" in nome:
        return "Passivo"
    return None

def pulisci_df(df):
    rename_map = {
        "descrizione": "Voce",
        "nome voce": "Voce",
        "voce": "Voce",
        "voce descrizione": "Voce",
        "valore": "Importo (€)",
        "importo": "Importo (€)",
        "importo €": "Importo (€)",
        "valore euro": "Importo (€)"
    }

    df.columns = [col.strip().lower() for col in df.columns]  # uniforma e pulisce nomi
    df = df.rename(columns={k.lower(): v for k, v in rename_map.items() if k.lower() in df.columns})

    if "voce" not in df.columns:
        df["Voce"] = "Voce non specificata"
        st.warning("⚠️ Colonna 'Voce' non trovata. Valore di default applicato.")
    else:
        df["Voce"] = df["voce"].astype(str).str.strip()

    if "importo (€)" not in df.columns:
        df["Importo (€)"] = 0.0
        st.warning("⚠️ Colonna 'Importo (€)' non trovata. Valori impostati a 0.")
    else:
        df["Importo (€)"] = pd.to_numeric(df["importo (€)"], errors="coerce").fillna(0)

    df = df.dropna(how="all")
    df = df[df["Voce"].str.strip() != ""]

    return df[["Voce", "Importo (€)"]] if "Voce" in df.columns and "Importo (€)" in df.columns else pd.DataFrame()

def estrai_info_da_nome(nome_file):
    # Estrae azienda e anno dal nome del file, es: "BetaSpa_2022.xlsx"
    match = re.match(r"(.+?)_?(\d{4})?$", nome_file)
    if match:
        azienda = match.group(1).strip()
        anno = match.group(2) if match.group(2) else "Anno?"
        return azienda, anno
    return nome_file, "Anno?"


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
