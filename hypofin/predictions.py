import numpy as np
from cachetools import TTLCache, cached

import hypofin.data as data

from .return_source import (
    AnnotatedReturnSource,
    DelayedReturnSource,
    InflationPremiumSource,
    RisklessReturnSource,
    RiskyReturnSource,
    SumReturnSource,
)
from .return_utils import annual_to_monthly


@cached(cache=TTLCache(maxsize=1, ttl=24 * 60 * 60))
def stocks():
    """Stock return estimation method based on: Shiller, Robert J. 2000. Irrational Exuberance"""
    expense_ratio = 0.0022
    return AnnotatedReturnSource(
        metadata=dict(
            name="Vanguard FTSE All-World UCITS ETF",
            isin="IE00BK5BQT80",
        ),
        return_source=SumReturnSource(
            return_sources=[
                InflationPremiumSource(
                    premium_source=RiskyReturnSource.from_historical_prices(
                        historical_prices=data.quotes(
                            "^GSPC"  # having more data is more important than using the exact instrument/currency
                        ),
                        expected_return=annual_to_monthly(1 / data.global_cape_ratio()),
                        autocorrelation_months=24,
                    ),
                ),
                RisklessReturnSource(monthly_return=annual_to_monthly(-expense_ratio)),
            ]
        ),
    )


@cached(cache=TTLCache(maxsize=16, ttl=24 * 60 * 60))
def polish_bonds(months_to_maturity: int):
    metadata = dict(
        name=data.polish_bond_names[months_to_maturity],
        buy_url=data.polish_bond_urls[months_to_maturity],
    )
    if months_to_maturity < 48:
        return AnnotatedReturnSource(
            metadata=metadata,
            return_source=RisklessReturnSource(
                monthly_return=annual_to_monthly(
                    data.polish_bond_yield(months_to_maturity)
                )
            ),
        )
    values = data.polish_bond_yield(months_to_maturity)
    return AnnotatedReturnSource(
        metadata=metadata,
        return_source=DelayedReturnSource(
            upcoming_returns=np.array([annual_to_monthly(values["first_year"])] * 12),
            return_source=InflationPremiumSource(
                premium_source=RisklessReturnSource(
                    monthly_return=annual_to_monthly(values["inflation_premium"])
                ),
            ),
        ),
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
    return DelayedReturnSource(
        upcoming_returns=prediction,
        return_source=RiskyReturnSource(
            example_returns=monthly,
            autocorrelation_months=36,
        ),
    )


@cached(cache=TTLCache(maxsize=16, ttl=24 * 60 * 60))
def monthly_default_probability(country: str):
    five_year = data.default_probability(country)
    return 1 - (1 - five_year) ** (1 / 12 / 5)
