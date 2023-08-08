from hypofin.data import BondYield, global_cape_ratio, historical_inflation, quotes


def test_polish_bond_yield():
    result = BondYield.polish_four_year()
    assert 0 < result.first_year < 0.1
    assert 0 < result.inflation_premium < 0.02


def test_global_cape_ratio():
    assert 10 < global_cape_ratio() < 30


def test_historical_inflation():
    result = historical_inflation()
    assert result.index.min() == 1995
    assert result.index.max() >= 2022
    assert len(result) == result.index.max() - result.index.min() + 1
    assert result.max() < 0.5
    assert result.min() > -0.05
