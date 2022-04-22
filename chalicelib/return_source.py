from dataclasses import dataclass
import numpy as np
import pandas as pd
from typing import Dict, List

from .trajectory import ExplainedTrajectory


@dataclass(frozen=True)
class ReturnSource:
    def sample_returns(
        self, num_months: int, inflation: np.ndarray = None
    ) -> np.ndarray:
        raise NotImplementedError()

    def sample_trajectory(
        self, start_amount: float, additions: np.ndarray, inflation: np.ndarray = None
    ):
        return ExplainedTrajectory.infer_savings(
            start_amount=start_amount,
            additions=additions,
            returns=self.sample_returns(num_months=len(additions), inflation=inflation),
        )


@dataclass(frozen=True)
class AnnotatedReturnSource(ReturnSource):
    metadata: Dict[str, str]
    return_source: ReturnSource

    def sample_returns(self, num_months: int, inflation: np.ndarray = None):
        return self.return_source.sample_returns(
            num_months=num_months, inflation=inflation
        )


@dataclass(frozen=True)
class SumReturnSource(ReturnSource):
    return_sources: List[ReturnSource]

    def sample_returns(self, num_months: int, inflation: np.ndarray = None):
        return sum(
            source.sample_returns(num_months=num_months, inflation=inflation)
            for source in self.return_sources
        )


@dataclass(frozen=True)
class DelayedReturnSource(ReturnSource):
    upcoming_returns: np.ndarray
    return_source: ReturnSource

    def sample_returns(self, num_months: int, inflation: np.ndarray = None):
        upcoming_returns = self.upcoming_returns[:num_months]
        sampled_returns = self.return_source.sample_returns(
            num_months=num_months - len(upcoming_returns),
            inflation=inflation[: -len(upcoming_returns)]  #  intentionally delayed
            if inflation is not None
            else None,
        )
        return np.concatenate([upcoming_returns, sampled_returns])


@dataclass(frozen=True)
class InflationPremiumSource(ReturnSource):
    premium_source: ReturnSource

    def sample_returns(self, num_months: int, inflation: np.ndarray) -> np.ndarray:
        premium = self.premium_source.sample_returns(
            num_months=num_months, inflation=inflation
        )
        return (1 + premium) * (1 + inflation) - 1


@dataclass(frozen=True)
class RisklessReturnSource(ReturnSource):
    monthly_return: float

    def sample_returns(
        self, num_months: int, inflation: np.ndarray = None
    ) -> np.ndarray:
        return np.full(shape=num_months, fill_value=self.monthly_return)


@dataclass(frozen=True)
class RiskyReturnSource(ReturnSource):
    example_returns: np.ndarray
    autocorrelation_months: int

    @classmethod
    def from_historical_prices(
        cls,
        historical_prices: pd.Series,
        expected_return: float,
        autocorrelation_months: int,
    ):
        historical_returns = np.array(
            historical_prices.pct_change(fill_method=None).dropna()
        )
        return cls(
            example_returns=historical_returns
            - historical_returns.mean()
            + expected_return,
            autocorrelation_months=autocorrelation_months,
        )

    def sample_returns(
        self, num_months: int, inflation: np.ndarray = None
    ) -> np.ndarray:
        start_indices = np.random.randint(
            0,
            len(self.example_returns),
            size=(num_months + self.autocorrelation_months - 1)
            // self.autocorrelation_months,
        )
        repeated_indices = start_indices.repeat(self.autocorrelation_months)[
            :num_months
        ]
        indices = (repeated_indices + np.arange(num_months)) % len(self.example_returns)
        return self.example_returns[indices]
