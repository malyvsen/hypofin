from cachetools import cached, TTLCache
import numpy as np

import chalicelib.data as data
from .portfolio import RisklessPortfolio, RiskyPortfolio, ReplayPortfolio
from .return_utils import annual_to_monthly


@cached(cache=TTLCache(maxsize=1, ttl=24 * 60 * 60))
def bond_portfolio():
    return RisklessPortfolio(
        return_per_step=annual_to_monthly(data.bond_yield("germany"))
    )


@cached(cache=TTLCache(maxsize=1, ttl=24 * 60 * 60))
def stock_premium_portfolio():
    """A portfolio tracking the returns of stocks minus inflation"""
    return RiskyPortfolio.from_historical_prices(
        historical_prices=data.stock_prices(),
        expected_return=annual_to_monthly(1 / data.global_cape_ratio()),
    )


@cached(cache=TTLCache(maxsize=16, ttl=24 * 60 * 60))
def inflation(country: str):
    yearly = np.array(
        data.historical_inflation(country).loc[2000:]
    )  # we only care about things which happened when the euro was in place
    monthly = np.repeat(annual_to_monthly(yearly), repeats=12)
    prediction = {
        "netherlands": data.euro_inflation_predictions,
        "poland": data.pln_inflation_predictions,
    }[country]()
    return ReplayPortfolio(
        predicted_returns=prediction,
        prediction_confidence=np.linspace(1, 0, num=len(prediction)),
        historical_returns=monthly,
    )


@cached(cache=TTLCache(maxsize=16, ttl=24 * 60 * 60))
def monthly_default_probability(country: str):
    five_year = data.default_probability(country)
    return 1 - (1 - five_year) ** (1 / 12 / 5)
