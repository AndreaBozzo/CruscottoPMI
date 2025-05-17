import pandas as pd

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
