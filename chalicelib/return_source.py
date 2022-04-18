from cmath import inf
from dataclasses import dataclass
import numpy as np
import pandas as pd
from typing import List

from .trajectory import ExplainedTrajectory


@dataclass(frozen=True)
class ReturnSource:
    def sample_returns(self, *args, **kwargs) -> np.ndarray:
        raise NotImplementedError()

    def sample_trajectory(
        self, start_amount: float, additions: np.ndarray, *args, **kwargs
    ):
        return ExplainedTrajectory.infer_savings(
            start_amount=start_amount,
            additions=additions,
            returns=self.sample_returns(num_steps=len(additions)),
        )


@dataclass(frozen=True)
class InflationPremiumSource(ReturnSource):
    fixed_returns: np.ndarray
    premium_source: ReturnSource

    @classmethod
    def immediate(cls, premium_source: ReturnSource):
        return cls(fixed_returns=np.array([]), premium_source=premium_source)

    def sample_returns(self, inflation: np.ndarray) -> np.ndarray:
        fixed_part = self.fixed_returns[: len(inflation)]
        delayed_inflation = inflation[len(fixed_part) :]
        premium_part = (
            self.premium_source.sample_returns(len(delayed_inflation))
            + delayed_inflation
        )
        return np.concatenate([fixed_part, premium_part])

    def sample_trajectory(
        self, start_amount: float, additions: np.ndarray, inflation: np.ndarray
    ) -> np.ndarray:
        ExplainedTrajectory.infer_savings(
            start_amount=start_amount,
            additions=additions,
            returns=self.sample_returns(inflation=inflation),
        )


@dataclass(frozen=True)
class RisklessReturnSource(ReturnSource):
    return_per_step: float

    def sample_returns(self, num_steps: int) -> np.ndarray:
        return np.full(shape=num_steps, fill_value=self.return_per_step)


@dataclass(frozen=True)
class RiskyReturnSource(ReturnSource):
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
class ReplayReturnSource(ReturnSource):
    """Plays out the predicted future and then repeats history cyclically from a randomly chosen point."""

    predicted_returns: np.ndarray
    prediction_confidence: np.ndarray
    historical_returns: np.ndarray

    def sample_returns(self, num_steps: int) -> np.ndarray:
        predicted_result = self.predicted_returns[:num_steps]
        historical_start = np.random.randint(low=0, high=len(self.historical_returns))
        historical_end = historical_start + num_steps
        historical_indices = np.arange(historical_start, historical_end) % len(
            self.historical_returns
        )
        historical_result = self.historical_returns[historical_indices]
        confidence = self.prediction_confidence[: len(predicted_result)]
        result_start = (predicted_result * confidence) + (
            historical_result[: len(predicted_result)] * (1 - confidence)
        )
        return np.concatenate([result_start, historical_result[len(result_start) :]])
