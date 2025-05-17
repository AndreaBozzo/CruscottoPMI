import pytest
import pandas as pd
from cruscotto_pmi.kpi_calculator import calcola_kpi

def test_calcola_kpi_base():
    ce = pd.DataFrame({
        "Voce": ["Ricavi", "EBIT", "Spese operative", "Ammortamenti", "Oneri finanziari", "Utile netto"],
        "Importo (€)": [1000000, 200000, 700000, 50000, 10000, 100000]
    })
    att = pd.DataFrame({
        "Voce": ["Disponibilità liquide", "Totale attivo"],
        "Importo (€)": [300000, 1000000]
    })
    pas = pd.DataFrame({
        "Voce": ["Debiti a breve", "Patrimonio netto", "Totale passivo"],
        "Importo (€)": [150000, 400000, 1000000]
    })
    benchmark = {
        "EBITDA Margin": 15,
        "ROE": 10,
        "ROI": 8,
        "Current Ratio": 1.3
    }

    result = calcola_kpi(ce, att, pas, benchmark)

    assert isinstance(result, dict)
    assert "EBITDA Margin" in result
    assert "Indice Sintetico" in result
    assert result["EBITDA Margin"] > 0