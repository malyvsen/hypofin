import chalicelib.data as data
from .portfolio import RisklessPortfolio, RiskyPortfolio


def annual_to_monthly(annual_return: float) -> float:
    return (1 + annual_return) ** (1 / 12) - 1


bond_portfolio = RisklessPortfolio(
    return_per_step=annual_to_monthly(
        (1 + data.bond_yield()) / (1 + data.euro_inflation()) - 1
    )
)
stock_portfolio = RiskyPortfolio.from_historical_prices(
    historical_prices=data.stock_prices(), expected_return=1 / data.global_cape_ratio()
)
