import pandas as pd
from cruscotto_pmi.data_loader import estrai_info_da_nome


def filtra_bilanci(bilanci_dict, azienda, anni):
    return [
        df for (az, anno), df in bilanci_dict.items()
        if az == azienda and anno in anni and isinstance(df, pd.DataFrame)
    ]

def estrai_aziende_anni(bilanci_dict):
    aziende = sorted({k[0] for k in bilanci_dict})
    anni = sorted({k[1] for k in bilanci_dict})
    return aziende, anni

def genera_df_yoy(df_kpi, df_voci, azienda, anno1, anno2):
    # Filtro i dati KPI e voci solo per l'azienda selezionata
    kpi1 = df_kpi[(df_kpi["Azienda"] == azienda) & (df_kpi["Anno"].astype(str) == str(anno1))]
    kpi2 = df_kpi[(df_kpi["Azienda"] == azienda) & (df_kpi["Anno"].astype(str) == str(anno2))]

    voci1 = df_voci[(df_voci["Azienda"] == azienda) & (df_voci["Anno"].astype(str) == str(anno1))]
    voci2 = df_voci[(df_voci["Azienda"] == azienda) & (df_voci["Anno"].astype(str) == str(anno2))]

    # Ristruttura KPI
    if not kpi1.empty and not kpi2.empty:
        kpi_cols = kpi1.select_dtypes(include=["number"]).columns
        s1 = kpi1[kpi_cols].squeeze()
        s2 = kpi2[kpi_cols].squeeze()

        delta_kpi = ((s2 - s1) / s1.replace(0, pd.NA)) * 100
        df_kpi_yoy = pd.DataFrame({
            "Voce": delta_kpi.index,
            "Variazione (%)": delta_kpi.values
        })
    else:
        df_kpi_yoy = pd.DataFrame(columns=["Voce", "Variazione (%)"])

    # Ristruttura Voci
    if not voci1.empty and not voci2.empty:
        v1 = voci1.pivot_table(index="Voce", values="Importo (€)", aggfunc="sum")
        v2 = voci2.pivot_table(index="Voce", values="Importo (€)", aggfunc="sum")
        joined = v1.join(v2, lsuffix="_1", rsuffix="_2", how="inner")
        joined["Variazione (%)"] = ((joined["Importo (€)_2"] - joined["Importo (€)_1"]) /
                                     joined["Importo (€)_1"].replace(0, pd.NA)) * 100
        joined = joined.reset_index()[["Voce", "Variazione (%)"]]
    else:
        joined = pd.DataFrame(columns=["Voce", "Variazione (%)"])

    # Combina KPI e Voci
    df_yoy = pd.concat([df_kpi_yoy, joined], axis=0, ignore_index=True)
    df_yoy = df_yoy.dropna(subset=["Variazione (%)"])
    df_yoy = df_yoy.sort_values("Variazione (%)", ascending=False).reset_index(drop=True)

    return df_yoy

def normalizza_kpi(df):
    """
    Converte un DataFrame KPI da formato lungo (con colonne 'KPI' e 'Valore')
    a formato largo (colonne KPI), solo se rilevante.
    """
    if not isinstance(df, pd.DataFrame):
        return df

    cols = df.columns.tolist()
    if all(x in cols for x in ["Azienda", "Anno", "KPI", "Valore"]):
        try:
            df_wide = df.pivot_table(
                index=["Azienda", "Anno"],
                columns="KPI",
                values="Valore",
                aggfunc="first"  # gestisce eventuali duplicati
            ).reset_index()
            return df_wide
        except Exception as e:
            print(f"[normalizza_kpi] Pivot fallito: {e}")
            return df
    return df

def elabora_bilanci(file_caricati: dict, debug: bool = False) -> dict:
    """
    Rielabora i file Excel normalizzati in DataFrame lunghi,
    restituendo un dizionario ben strutturato per azienda e anno.

    Output:
    {
        ("Alpha", "2022"): {
            "CE": df_ce,
            "Attivo": df_att,
            "Passivo": df_pas,
            "completo": df_lungo
        },
        ...
    }

    Parametri:
    - file_caricati: dict di DataFrame provenienti da load_excel()
    - debug: se True, attiva messaggi di log via Streamlit
    """
    bilanci = {}
    required_cols = {"Voce", "Importo (€)"}

    for nome_file, df in file_caricati.items():
        azienda, anno = estrai_info_da_nome(nome_file)

        if not isinstance(df, pd.DataFrame) or df.empty:
            if debug:
                st.warning(f"⚠️ Il file `{nome_file}` è vuoto o non valido.")
            continue

        # Verifica colonna 'Tipo'
        if "Tipo" not in df.columns:
            if debug:
                st.error(f"❌ Il file `{nome_file}` manca della colonna 'Tipo'. Impossibile segmentare.")
            continue

        # Verifica colonne minime richieste
        if not required_cols.issubset(set(df.columns)):
            missing = required_cols - set(df.columns)
            if debug:
                st.warning(f"⚠️ Colonne mancanti nel file `{nome_file}`: {', '.join(missing)}")

        sezioni = {}
        sezioni_presenti = df["Tipo"].unique()

        for tipo in ["CE", "Attivo", "Passivo"]:
            df_tipo = df[df["Tipo"] == tipo].copy()
            if not df_tipo.empty:
                sezioni[tipo] = df_tipo.reset_index(drop=True)
            else:
                sezioni[tipo] = pd.DataFrame(columns=df.columns)
                if debug:
                    st.warning(f"⚠️ Sezione {tipo} mancante per {azienda} – {anno}")

        sezioni["completo"] = df.reset_index(drop=True)
        for key in ["CE", "Attivo", "Passivo", "completo"]:
            sezioni[key]["Anno"] = anno
            sezioni[key]["Azienda"] = azienda
        bilanci[(azienda, anno)] = sezioni

        if debug:
            st.success(f"📦 Bilancio caricato: {azienda} – {anno} ({', '.join(sezioni_presenti)})")

    if debug:
        if bilanci:
            aziende_ok = [f"{a}–{y}" for (a, y) in bilanci.keys()]
            st.info(f"✅ Elaborazione completata per: {', '.join(aziende_ok)}")
        else:
            st.error("❌ Nessun bilancio valido è stato elaborato.")

    return bilanci

def genera_badge_kpi(valore, soglia, unita="%", kpi_nome=""):
    """
    Genera badge visivo con colore in base al confronto col benchmark.
    Restituisce una stringa HTML da usare con st.markdown(..., unsafe_allow_html=True)
    """
    try:
        valore = float(valore)
        soglia = float(soglia)
        rapporto = valore / soglia if soglia else 0
    except:
        return ""

    if rapporto >= 1:
        colore = "#2ecc71"  # verde
        stato = "Ottimo"
    elif rapporto >= 0.75:
        colore = "#f1c40f"  # giallo
        stato = "Sufficiente"
    else:
        colore = "#e74c3c"  # rosso
        stato = "Critico"

    valore_formattato = f"{valore:.2f}{unita}"
    html = f"""
    <div style='
        display: inline-block;
        padding: 6px 12px;
        border-radius: 8px;
        background-color: {colore};
        color: white;
        font-weight: bold;
        font-size: 0.85rem;
        margin-bottom: 4px;
    '>
        {kpi_nome}: {valore_formattato} ({stato})
    </div>
    """
    return html

def commento_kpi(kpi, valore, soglia):
    """
    Genera un commento testuale per un KPI confrontando il valore con la soglia.
    """
    try:
        valore = float(valore)
        soglia = float(soglia)
        rapporto = valore / soglia if soglia else 0
    except:
        return ""

    if rapporto >= 1.05:
        giudizio = "superiore al benchmark. Ottima performance."
    elif rapporto >= 0.95:
        giudizio = "in linea con il benchmark. Performance adeguata."
    else:
        giudizio = "inferiore alla soglia. Attenzione su questo indicatore."

    return f"{kpi}: {giudizio}"
