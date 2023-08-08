from datetime import datetime

from hypofin.data import (
    BondYield,
    global_cape_ratio,
    historical_inflation_pln,
    historical_prices_pln,
)
from hypofin.data.historical_values import historical_usd_pln


def test_polish_bond_yield():
    result = BondYield.polish_four_year()
    assert 0 < result.first_year < 0.1
    assert 0 < result.inflation_premium < 0.02


def test_global_cape_ratio():
    assert 10 < global_cape_ratio() < 30


def test_historical_inflation_pln():
    result = historical_inflation_pln()
    assert result.index.min() == 1995
    assert result.index.max() >= datetime.now().year - 2
    assert len(result) == result.index.max() - result.index.min() + 1
    assert result.max() < 0.5
    assert result.min() > -0.05


def test_historical_prices_pln():
    result = historical_prices_pln("MSFT")
    assert result.index[0].year == 1995
    assert (datetime.now() - result.index[-1]).days < 45
    num_years = result.index[-1].year - result.index[0].year
    num_months = result.index[-1].month - result.index[0].month
    num_expected_values = num_years * 12 + num_months + 1
    assert len(result) == num_expected_values


def test_historical_usd_pln():
    result = historical_usd_pln()
    assert result.index[0].year == 1995
    assert (datetime.now() - result.index[-1]).days < 45
    assert result["2023-08-01"] == 4.00395
    assert result.max() < 5
    assert result.min() > 1
