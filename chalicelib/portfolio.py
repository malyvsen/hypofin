from dataclasses import dataclass
import numpy as np
import pandas as pd
from typing import List

from .trajectory import ExplainedTrajectory


@dataclass(frozen=True)
class Portfolio:
    def sample_returns(self, num_steps: int) -> np.ndarray:
        raise NotImplementedError()

    def sample_trajectory(self, start_amount: float, additions: np.ndarray):
        return ExplainedTrajectory.infer_savings(
            start_amount=start_amount,
            additions=additions,
            returns=self.sample_returns(num_steps=len(additions)),
        )


@dataclass(frozen=True)
class WeightedPortfolio(Portfolio):
    """A weighted portfolio, rebalanced monthly"""

    @dataclass(frozen=True)
    class Component:
        weight: float
        portfolio: Portfolio

    components: List[Component]

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


@dataclass(frozen=True)
class InflationPortfolio(Portfolio):
    future_predictions: np.ndarray
    historical_inflation: np.ndarray

    def sample_returns(self, num_steps: int) -> np.ndarray:
        predicted_result = self.future_predictions[:num_steps]
        historical_start = np.random.randint(low=0, high=len(self.historical_inflation))
        historical_end = historical_start + num_steps - len(predicted_result)
        historical_indices = np.arange(historical_start, historical_end) % len(
            self.historical_inflation
        )
        historical_result = self.historical_inflation[historical_indices]
        return np.concatenate([predicted_result, historical_result])
