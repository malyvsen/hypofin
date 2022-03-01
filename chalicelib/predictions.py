from cachetools import cached, TTLCache
import chalicelib.data as data
from .portfolio import RisklessPortfolio, RiskyPortfolio


# TODO: inflation shouldn't be included here - it should be applied post-tax
@cached(cache=TTLCache(maxsize=1, ttl=24 * 60 * 60))
def bond_portfolio():
    return RisklessPortfolio(
        return_per_step=(1 + annual_to_monthly(data.bond_yield()))
        / (1 + monthly_inflation())
        - 1
    )


@cached(cache=TTLCache(maxsize=1, ttl=24 * 60 * 60))
def stock_portfolio():
    return RiskyPortfolio.from_historical_prices(
        historical_prices=data.stock_prices(),
        expected_return=1 / data.global_cape_ratio(),
    )


@cached(cache=TTLCache(maxsize=1, ttl=24 * 60 * 60))
def bank_portfolio():
    return RisklessPortfolio(return_per_step=1 / (1 + monthly_inflation()) - 1)


@cached(cache=TTLCache(maxsize=1, ttl=24 * 60 * 60))
def monthly_inflation():
    return annual_to_monthly(data.euro_inflation())


def annual_to_monthly(annual_return: float) -> float:
    return (1 + annual_return) ** (1 / 12) - 1
