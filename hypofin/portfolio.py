from dataclasses import dataclass
import numpy as np
import pandas as pd
import scipy.stats
from typing import List


@dataclass(frozen=True)
class Portfolio:
    def sample_returns(self, num_steps: int) -> np.ndarray:
        raise NotImplementedError()

    def sample_savings(
        self, num_steps: int, start_amount: float, added_per_step: float
    ) -> np.ndarray:
        """
        A sequence of amount saved up, projected num_steps ahead
        The first element is already one step after the current situation
        """
        cumulative_growth = np.cumprod(1 + self.sample_returns(num_steps))
        start_amount_growth = start_amount * cumulative_growth
        added = np.full(shape=num_steps, fill_value=added_per_step)
        added_growth = np.cumsum(added / cumulative_growth) * cumulative_growth
        return start_amount_growth + added_growth


@dataclass(frozen=True)
class BalancedPortfolio(Portfolio):
    @dataclass(frozen=True)
    class Component:
        weight: float
        portfolio: Portfolio

    components: List[Component]

    def sample_returns(self, num_steps: int) -> np.ndarray:
        return sum(
            component.weight * component.portfolio.sample_returns(num_steps)
            for component in self.components
        )


@dataclass(frozen=True)
class RisklessPortfolio(Portfolio):
    return_per_step: float

    def sample_returns(self, num_steps: int) -> np.ndarray:
        return np.full(shape=num_steps, fill_value=self.return_per_step)


@dataclass(frozen=True)
class RiskyPortfolio(Portfolio):
    log_return_distribution: scipy.stats.rv_continuous

    @classmethod
    def from_historical_prices(
        cls, historical_prices: pd.Series, expected_return: float
    ):
        historical_log_returns = np.log(historical_prices).diff().dropna()
        loc, scale = scipy.stats.laplace.fit(historical_log_returns)
        return cls(
            log_return_distribution=scipy.stats.laplace(
                np.log(1 + expected_return), scale
            )
        )

    def sample_returns(self, num_steps: int) -> np.ndarray:
        return np.exp(self.log_return_distribution.rvs(num_steps)) - 1
