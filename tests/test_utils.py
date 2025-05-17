import pytest
import pandas as pd
from cruscotto_pmi.utils import filtra_bilanci, estrai_aziende_anni

def test_filtra_bilanci():
    df = pd.DataFrame({"Voce": ["A"], "Importo (€)": [100]})
    bilanci = {("ACME", 2022): df, ("BETA", 2023): df}
    res = filtra_bilanci(bilanci, "ACME", [2022])
    assert len(res) == 1
    assert isinstance(res[0], pd.DataFrame)

def test_estrai_aziende_anni():
    bilanci = {("ACME", 2022): None, ("BETA", 2023): None}
    aziende, anni = estrai_aziende_anni(bilanci)
    assert aziende == ["ACME", "BETA"]
    assert anni == [2022, 2023]