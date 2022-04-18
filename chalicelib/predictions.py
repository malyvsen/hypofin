from cachetools import cached, TTLCache
import numpy as np

import chalicelib.data as data
from .return_source import (
    InflationPremiumSource,
    RisklessReturnSource,
    RiskyReturnSource,
    ReplayReturnSource,
)
from .return_utils import annual_to_monthly


@cached(cache=TTLCache(maxsize=1, ttl=24 * 60 * 60))
def stocks():
    return InflationPremiumSource.immediate(
        RiskyReturnSource.from_historical_prices(
            historical_prices=data.stock_prices(),
            expected_return=annual_to_monthly(1 / data.global_cape_ratio()),
        )
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
    return ReplayReturnSource(
        predicted_returns=prediction,
        prediction_confidence=np.linspace(1, 0, num=len(prediction)),
        historical_returns=monthly,
    )


@cached(cache=TTLCache(maxsize=16, ttl=24 * 60 * 60))
def bonds(country: str) -> InflationPremiumSource:
    if country == "netherlands":
        return InflationPremiumSource.immediate(
            premium_source=RisklessReturnSource(return_per_step=0),  # TODO
        )
    if country == "poland":
        values = data.polish_bond_yield()
        return InflationPremiumSource(
            fixed_returns=np.array([annual_to_monthly(values["first_year"])] * 12),
            premium_source=RisklessReturnSource(
                return_per_step=annual_to_monthly(values["inflation_premium"])
            ),
        )


@cached(cache=TTLCache(maxsize=16, ttl=24 * 60 * 60))
def monthly_default_probability(country: str):
    five_year = data.default_probability(country)
    return 1 - (1 - five_year) ** (1 / 12 / 5)
