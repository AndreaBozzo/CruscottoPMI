import pytest
import pandas as pd
from io import BytesIO
from cruscotto_pmi import utils


def test_calcola_kpi_base():
    anno = "2022"

    df_attivo = pd.DataFrame({
        "Attività": ["Totale Attivo", "Disponibilità liquide"],
        "Importo (€)": [100000, 20000],
        "Anno": [anno, anno]
    })

    df_passivo = pd.DataFrame({
        "Passività e Patrimonio Netto": ["Patrimonio netto", "Totale Passivo", "Debiti a breve"],
        "Importo (€)": [50000, 120000, 40000],
        "Anno": [anno, anno, anno]
    })

    df_ce = pd.DataFrame({
        "Voce": ["Ricavi", "EBIT", "Utile netto", "Spese operative"],
        "Importo (€)": [200000, 40000, 25000, 160000],
        "Anno": [anno] * 4
    })

    benchmark = pd.DataFrame(columns=["KPI", "Valore"])

    kpi = utils.calcola_kpi(df_ce, df_attivo, df_passivo, benchmark)

    assert "EBITDA Margin" in kpi
    assert round(kpi["EBITDA Margin"], 2) == 100.0
    assert "ROE" in kpi
    assert "Indice Sintetico" in kpi


def test_load_excel():
    ce_df = pd.DataFrame({"Voce": ["Ricavi"], "Importo (€)": [100000], "Anno": [2022]})
    att_df = pd.DataFrame({"Attività": ["Totale Attivo"], "Importo (€)": [150000], "Anno": [2022]})
    pas_df = pd.DataFrame({"Passività e Patrimonio Netto": ["Patrimonio netto"], "Importo (€)": [80000], "Anno": [2022]})

    # Cast a stringa PRIMA della scrittura
    ce_df["Anno"] = ce_df["Anno"].astype(str)
    att_df["Anno"] = att_df["Anno"].astype(str)
    pas_df["Anno"] = pas_df["Anno"].astype(str)

    excel_file = BytesIO()
    with pd.ExcelWriter(excel_file, engine="openpyxl") as writer:
        ce_df.to_excel(writer, sheet_name="Conto Economico", index=False)
        att_df.to_excel(writer, sheet_name="Attivo", index=False)
        pas_df.to_excel(writer, sheet_name="Passivo", index=False)
    excel_file.seek(0)

    ce_loaded, att_loaded, pas_loaded = utils.load_excel(excel_file)

    # Cast a stringa anche DOPO la lettura
    ce_loaded["Anno"] = ce_loaded["Anno"].astype(str)
    att_loaded["Anno"] = att_loaded["Anno"].astype(str)
    pas_loaded["Anno"] = pas_loaded["Anno"].astype(str)

    pd.testing.assert_frame_equal(ce_loaded, ce_df, check_dtype=False, check_like=True)
    pd.testing.assert_frame_equal(att_loaded, att_df, check_dtype=False, check_like=True)
    pd.testing.assert_frame_equal(pas_loaded, pas_df, check_dtype=False, check_like=True)

def test_load_excel_missing_sheet():
    # Crea solo un foglio su tre
    ce_df = pd.DataFrame({"Voce": ["Ricavi"], "Importo (€)": [100000], "Anno": [2022]})

    excel_file = BytesIO()
    with pd.ExcelWriter(excel_file, engine="openpyxl") as writer:
        ce_df.to_excel(writer, sheet_name="Conto Economico", index=False)
    excel_file.seek(0)

    # Verifica che sollevi un errore perché mancano "Attivo" e "Passivo"
    with pytest.raises(Exception) as exc_info:
        utils.load_excel(excel_file)

    assert "Attivo" in str(exc_info.value) or "sheet" in str(exc_info.value)

def test_load_benchmark_from_csv():
    # Simula un CSV benchmark con due righe
    csv_content = b"KPI,Valore\nROE,10\nEBITDA Margin,20\n"

    # Usa BytesIO per simulare il file CSV in memoria
    csv_file = BytesIO(csv_content)

    default_benchmark = pd.DataFrame({
        "KPI": ["ROE", "EBITDA Margin", "ROI", "Current Ratio"],
        "Valore": [5, 10, 7, 1.5]
    })

    result = utils.load_benchmark(csv_file, default_benchmark)

    assert isinstance(result, dict)
    assert result["ROE"] == 10
    assert result["EBITDA Margin"] == 20
