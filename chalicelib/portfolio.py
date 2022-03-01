from dataclasses import dataclass
from functools import lru_cache
import numpy as np
import pandas as pd
import scipy.stats
from typing import List


@dataclass(frozen=True)
class Portfolio:
    def sample_returns(self, num_steps: int) -> np.ndarray:
        raise NotImplementedError()

    def sample_savings(self, additions: np.ndarray) -> np.ndarray:
        """A sequence of amounts saved up, given the additions[step_id] is added at that step"""
        cumulative_growth = np.cumprod(1 + self.sample_returns(len(additions)))
        return np.cumsum(additions / cumulative_growth) * cumulative_growth

    def savings_quantile_cached(
        self,
        additions: np.ndarray,
        quantile: float,
        precision=1024,
    ) -> np.ndarray:
        return self._savings_quantile_cached(
            additions=tuple(additions), quantile=quantile, precision=precision
        )

    @lru_cache(maxsize=64)
    def _savings_quantile_cached(
        self, additions: tuple, quantile: float, precision: int
    ):
        return self.savings_quantile(
            additions=np.array(additions), quantile=quantile, precision=precision
        )

    def savings_quantile(
        self,
        additions: np.ndarray,
        quantile: float,
        precision: int,
    ) -> np.ndarray:
        raise NotImplementedError()


@dataclass(frozen=True)
class MixedPortfolio(Portfolio):
    @dataclass(frozen=True)
    class Component:
        weight: float
        portfolio: Portfolio

    riskless_component: Component
    risky_component: Component

    def __post_init__(self):
        assert np.isclose(sum(component.weight for component in self.components), 1)
        assert isinstance(self.riskless_component.portfolio, RisklessPortfolio)
        assert isinstance(self.risky_component.portfolio, RiskyPortfolio)

    @property
    def components(self) -> List[Component]:
        return [self.riskless_component, self.risky_component]

    def sample_savings(self, additions: np.ndarray) -> np.ndarray:
        return sum(
            component.portfolio.sample_savings(additions=additions * component.weight)
            for component in self.components
        )

    def savings_quantile(
        self,
        additions: np.ndarray,
        quantile: float,
        precision: int,
    ) -> np.ndarray:
        return sum(
            component.portfolio.savings_quantile(
                additions=additions * component.weight,
                quantile=quantile,
                precision=precision,
            )
            for component in self.components
        )


@dataclass(frozen=True)
class RisklessPortfolio(Portfolio):
    return_per_step: float

    def sample_returns(self, num_steps: int) -> np.ndarray:
        return np.full(shape=num_steps, fill_value=self.return_per_step)

    def savings_quantile(
        self,
        additions: np.ndarray,
        quantile: float,
        precision: int,
    ) -> np.ndarray:
        return self.sample_savings(additions=additions)


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

    def savings_quantile(
        self,
        additions: np.ndarray,
        quantile: float,
        precision: int,
    ) -> np.ndarray:
        if quantile == 0:
            return additions
        return np.quantile(
            [
                self.sample_savings(additions=additions)
                for simulation in range(precision)
            ],
            q=quantile,
            axis=0,
        )
