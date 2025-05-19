import pandas as pd
import streamlit as st
import re
from io import BytesIO
from cruscotto_pmi.alias import ALIAS_FOGLI
from cruscotto_pmi.alias import ALIAS_COLONNE_VOCE, ALIAS_COLONNE_IMPORTO


def mappa_tipo_foglio(nome):
    nome = nome.lower().strip()

    for tipo, alias_list in ALIAS_FOGLI.items():
        for alias in alias_list:
            if alias in nome:
                return tipo

    # fallback compatibile
    if "stato patrimoniale" in nome:
        if "attivo" in nome:
            return "Attivo"
        if "passivo" in nome:
            return "Passivo"

    return None


def load_excel(file, debug=False):
    nome_file = file.name.replace(".xlsx", "")
    azienda, anno = estrai_info_da_nome(nome_file)

    try:
        xls = pd.ExcelFile(file)
        if debug:
            st.info(f"📘 Analisi file: `{file.name}` – Fogli trovati: {', '.join(xls.sheet_names)}")

        df_finale = pd.DataFrame()
        fogli_utilizzati = 0
        log_ignorati = []  # ⬅️ Nuovo log compatto

        for nome_foglio_originale in xls.sheet_names:
            tipo_foglio = mappa_tipo_foglio(nome_foglio_originale)
            df_temp = pd.read_excel(xls, sheet_name=nome_foglio_originale)

            if tipo_foglio:
                try:
                    df_temp = pulisci_df(df_temp, debug=debug)
                    if df_temp.empty:
                        log_ignorati.append((nome_foglio_originale, "Foglio vuoto dopo la pulizia"))
                        continue

                    df_temp["Tipo"] = tipo_foglio
                    df_temp["Azienda"] = azienda
                    df_temp["Anno"] = anno
                    df_finale = pd.concat([df_finale, df_temp], ignore_index=True)
                    fogli_utilizzati += 1

                    if debug:
                        st.success(f"✅ Foglio `{nome_foglio_originale}` caricato ({len(df_temp)} righe) come `{tipo_foglio}`")

                except Exception as e:
                    log_ignorati.append((nome_foglio_originale, f"Errore durante la pulizia: {e}"))

            else:
                fallback_df = gestione_foglio_non_riconosciuto(df_temp, nome_foglio_originale,azienda=azienda,anno=anno)
                if fallback_df is not None:
                    fallback_df["Azienda"] = azienda
                    fallback_df["Anno"] = anno
                    df_finale = pd.concat([df_finale, fallback_df], ignore_index=True)
                    fogli_utilizzati += 1
                else:
                    log_ignorati.append((nome_foglio_originale, "Scelta manuale: ignorato"))

        # === Log finale compatto
        if log_ignorati:
            with st.expander(f"ℹ️ Fogli ignorati ({len(log_ignorati)}): clicca per dettagli"):
                for nome, motivo in log_ignorati:
                    st.markdown(f"• 📄 **{nome}** – {motivo}")
                
        # Debug: preview dati aggregati
        if debug:
            st.info("Preview dati caricati (prime 10 righe):")
            st.dataframe(df_finale.head(10))
            st.write("Colonne:", list(df_finale.columns))
            st.write("Aziende:", df_finale['Azienda'].unique())
            st.write("Anni:", df_finale['Anno'].unique())
            st.write("Tipi:", df_finale['Tipo'].unique())

        return df_finale, azienda, anno

    except Exception as e:
        st.error(f"❌ Errore critico nella lettura del file `{file.name}`: {str(e)}")
        return pd.DataFrame()

        


def pulisci_df(df, debug=True):
    # Uniforma nomi colonna
    df.columns = [col.lower().strip() for col in df.columns]

    # Mapping colonne con fuzzy logic
    voce_col = None
    importo_col = None

    # Cerca alias anche parziali
    for alias in ALIAS_COLONNE_VOCE:
        voce_col = next((c for c in df.columns if alias in c), None)
        if voce_col: break

    for alias in ALIAS_COLONNE_IMPORTO:
        importo_col = next((c for c in df.columns if alias in c), None)
        if importo_col: break

    # Logging e fallback
    if not voce_col and debug:
        st.warning("⚠️ Colonna 'Voce' non trovata nel foglio. Tutte le righe marcate come 'Voce non specificata'.")
    if not importo_col and debug:
        st.warning("⚠️ Colonna 'Importo' non trovata nel foglio. Tutti i valori saranno impostati a 0.")

    # Ricostruzione DataFrame
    df["Voce"] = df[voce_col].astype(str).str.strip() if voce_col else "Voce non specificata"
    df["Importo (€)"] = (
        pd.to_numeric(df[importo_col], errors="coerce").fillna(0) if importo_col else 0.0
    )

    # Rimozione righe vuote
    df = df.dropna(how="all")
    df = df[df["Voce"].astype(str).str.strip() != ""]

    return df[["Voce", "Importo (€)"]]



def estrai_info_da_nome(nome_file):
    nome_base = nome_file.replace(".xlsx", "").replace(".xls", "").strip()

    # Cattura nome_anno ovunque ci sia un 4 cifre finali
    match = re.search(r"(.+?)[_\-\s]?(\d{4})\b", nome_base)
    if match:
        azienda = match.group(1).strip()
        anno = match.group(2)
        return azienda, anno

    # Fallback: prova a trovare un numero di 4 cifre ovunque
    parts = re.split(r"[_\-\s]", nome_base)
    anno = next((p for p in parts if p.isdigit() and len(p) == 4), None)
    azienda = nome_base.replace(anno, "").replace("_", " ").strip() if anno else nome_base
    return azienda.strip(), anno if anno else "Anno?"



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

def gestione_foglio_non_riconosciuto(df: pd.DataFrame, nome_foglio: str, azienda=None, anno=None):
    st.warning(f"⚠️ Il foglio '{nome_foglio}' non è stato riconosciuto automaticamente.")

    # Rendi la chiave univoca usando anche azienda e anno!
    unique_id = f"{azienda}_{anno}_{nome_foglio}".replace(" ", "_")

    tipo = st.selectbox(
        f"Classifica il foglio '{nome_foglio}' come:",
        ["Ignora", "CE", "Attivo", "Passivo"],
        key=f"tipo_{unique_id}"
    )
    if tipo == "Ignora":
        return None

    col_voce = st.selectbox(
        f"Colonna descrizione per '{nome_foglio}'",
        df.columns,
        key=f"voce_{unique_id}"
    )
    col_importo = st.selectbox(
        f"Colonna importo per '{nome_foglio}'",
        df.columns,
        key=f"importo_{unique_id}"
    )

    df_renamed = df.rename(columns={col_voce: "Voce", col_importo: "Importo (€)"})
    df_filtrato = df_renamed[["Voce", "Importo (€)"]].dropna()
    df_filtrato["Tipo"] = tipo

    st.dataframe(df_filtrato.head(10))
    return df_filtrato

