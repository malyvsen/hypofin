from dataclasses import dataclass
import numpy as np
import pandas as pd
from typing import List

from .config import num_trajectories_for_quantile


@dataclass(frozen=True)
class Portfolio:
    def sample_returns(self, num_steps: int) -> np.ndarray:
        raise NotImplementedError()

    def sample_savings(self, additions: np.ndarray) -> np.ndarray:
        """A sequence of amounts saved up, given that additions[step_id] is added at that step"""
        cumulative_growth = np.cumprod(1 + self.sample_returns(len(additions)))
        return np.cumsum(additions / cumulative_growth) * cumulative_growth

    def savings_quantile(
        self,
        additions: np.ndarray,
        quantile: float,
    ) -> np.ndarray:
        return np.quantile(
            [
                self.sample_savings(additions=additions)
                for simulation in range(num_trajectories_for_quantile)
            ],
            q=quantile,
            axis=0,
        )


@dataclass(frozen=True)
class BalancedPortfolio(Portfolio):
    """A portfolio which is rebalanced monthly"""

    @dataclass(frozen=True)
    class Component:
        weight: float
        portfolio: Portfolio

    components: List[Component]

    def __post_init__(self):
        assert np.isclose(sum(component.weight for component in self.components), 1)

    def sample_returns(self, num_steps: int) -> np.ndarray:
        return sum(
            component.portfolio.sample_returns(num_steps=num_steps) * component.weight
            for component in self.components
        )


@dataclass(frozen=True)
class RisklessPortfolio(Portfolio):
    return_per_step: float

    def sample_returns(self, num_steps: int) -> np.ndarray:
        return np.full(shape=num_steps, fill_value=self.return_per_step)


@dataclass(frozen=True)
class RiskyPortfolio(Portfolio):
    example_returns: np.ndarray

    @classmethod
    def from_historical_prices(
        cls, historical_prices: pd.Series, expected_return: float
    ):
        historical_returns = np.array(
            historical_prices.pct_change(fill_method=None).dropna()
        )
        return cls(
            example_returns=historical_returns
            - historical_returns.mean()
            + expected_return
        )

    def sample_returns(self, num_steps: int) -> np.ndarray:
        return np.random.choice(self.example_returns, size=num_steps)
