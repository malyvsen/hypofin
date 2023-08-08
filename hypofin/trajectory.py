from dataclasses import dataclass
from functools import cached_property

import numpy as np

from .portfolio import Portfolio
from .return_conversion import annual_to_monthly
from .scenario import Scenario

CAPITAL_GAINS_TAX = 0.19


@dataclass(frozen=True)
class Trajectory:
    """What happens to a portfolio in a given scenario."""

    portfolio: Portfolio
    scenario: Scenario

    @cached_property
    def post_tax_savings(self):
        """The money one would obtain by selling all their assets at any given time."""
        excess_savings = self.pre_tax_savings - self.total_investment
        negative_excess = np.minimum(excess_savings, 0)
        positive_excess = np.maximum(excess_savings, 0)
        return (
            self.total_investment
            + negative_excess
            + positive_excess * (1 + annual_to_monthly(-CAPITAL_GAINS_TAX))
        )

    @cached_property
    def pre_tax_savings(self):
        initial_and_additions = np.concatenate(
            [
                [self.portfolio.initial_investment],
                [self.portfolio.monthly_addition] * (self.scenario.num_months - 1),
            ]
        )
        cumulative_growth = np.concatenate([[1], np.cumprod(1 + self.pre_tax_returns)])
        return np.cumsum(initial_and_additions / cumulative_growth) * cumulative_growth

    @cached_property
    def pre_tax_returns(self):
        return (
            self.portfolio.bond_fraction * self.scenario.bond_returns
            + self.portfolio.stock_fraction * self.scenario.stock_returns
        )

    @cached_property
    def total_investment(self):
        return (
            self.portfolio.initial_investment
            + np.arange(self.scenario.num_months) * self.portfolio.monthly_addition
        )
