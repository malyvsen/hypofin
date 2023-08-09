from dataclasses import dataclass
from functools import cached_property

import numpy as np

from .data import (
    BondYield,
    global_cape_ratio,
    historical_inflation_pln,
    historical_prices_pln,
)
from .return_conversion import annual_to_monthly, prices_to_returns


@dataclass(frozen=True)
class Scenario:
    """A possible future scenario, month by month."""

    inflation: np.ndarray
    stock_returns: np.ndarray

    @cached_property
    def bond_returns(self):
        bond_yield = BondYield.polish_four_year()
        if self.num_months <= 12:
            return np.array(
                [annual_to_monthly(bond_yield.first_year)] * self.num_months
            )
        total_inflation = self.inflation.cumprod()
        inflation_year_over_year = total_inflation[12:] / total_inflation[:-12]
        return np.array(
            [annual_to_monthly(bond_yield.first_year)] * 12
            + annual_to_monthly(
                inflation_year_over_year + bond_yield.inflation_premium
            ).tolist()
        )

    @cached_property
    def num_months(self):
        return len(self.inflation)

    @classmethod
    def hypothesize(cls, num_months: int):
        """Sample a random future scenario."""
        historical_inflation_monthly = annual_to_monthly(historical_inflation_pln())
        sampled_inflation = np.random.choice(
            historical_inflation_monthly, size=num_months, replace=True
        )

        # use S&P 500 because more data is better than exact data
        historical_stock_returns = prices_to_returns(historical_prices_pln("^GSPC"))

        # based on Shiller, Robert J. 2000. Irrational Exuberance
        # and an assumption that stock returns are independent of inflation
        expected_stock_returns = annual_to_monthly(1 / global_cape_ratio())

        # using empirical distribution and assuming iid - keep it simple, stupid
        sampled_stock_returns = np.random.choice(
            historical_stock_returns
            - historical_stock_returns.mean()
            + expected_stock_returns,
            size=num_months,
            replace=True,
        )

        return cls(
            inflation=sampled_inflation,
            stock_returns=sampled_stock_returns,
        )

    def prices(self, initial_price: float):
        """How much something starting at initial_price will cost over time."""
        return np.array(
            [initial_price] + list(initial_price * np.cumprod(self.inflation + 1))
        )
