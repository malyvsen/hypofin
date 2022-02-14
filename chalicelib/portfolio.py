from dataclasses import dataclass
import numpy as np
import pandas as pd
import scipy.stats
from typing import List


@dataclass(frozen=True)
class Portfolio:
    def sample_returns(self, num_steps: int) -> np.NDArray:
        raise NotImplementedError()

    def sample_savings(
        self, num_steps: int, start_amount: float, added_per_step: float
    ) -> np.NDArray:
        """
        A sequence of amount saved up, projected num_steps ahead
        The first element is already one step after the current situation
        """
        cumulative_growth = np.cumprod(1 + self.sample_returns(num_steps))
        start_amount_growth = start_amount * cumulative_growth
        added = np.full(shape=num_steps, fill_value=added_per_step)
        added_growth = np.cumsum(added / cumulative_growth) * cumulative_growth
        return start_amount_growth + added_growth

    def quantile(
        self,
        num_steps: int,
        start_amount: float,
        added_per_step: float,
        quantile: float,
        precision=1024,
    ) -> np.NDArray:
        raise NotImplementedError()


@dataclass(frozen=True)
class BalancedPortfolio(Portfolio):
    @dataclass(frozen=True)
    class Component:
        weight: float
        portfolio: Portfolio

    components: List[Component]

    def sample_returns(self, num_steps: int) -> np.NDArray:
        return sum(
            component.weight * component.portfolio.sample_returns(num_steps)
            for component in self.components
        )

    def quantile(
        self,
        num_steps: int,
        start_amount: float,
        added_per_step: float,
        quantile: float,
        precision=1024,
    ) -> np.NDArray:
        return sum(
            component.weight
            * component.quantile(
                num_steps=num_steps,
                start_amount=start_amount,
                added_per_step=added_per_step,
                quantile=quantile,
                precision=precision,
            )
            for component in self.components
        )


@dataclass(frozen=True)
class RisklessPortfolio(Portfolio):
    return_per_step: float

    def sample_returns(self, num_steps: int) -> np.NDArray:
        return np.full(shape=num_steps, fill_value=self.return_per_step)

    def quantile(
        self,
        num_steps: int,
        start_amount: float,
        added_per_step: float,
        quantile: float,
        precision=1024,
    ) -> np.NDArray:
        return self.sample_savings(
            num_steps=num_steps,
            start_amount=start_amount,
            added_per_step=added_per_step,
        )


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

    def sample_returns(self, num_steps: int) -> np.NDArray:
        return np.exp(self.log_return_distribution.rvs(num_steps)) - 1

    def quantile(
        self,
        num_steps: int,
        start_amount: float,
        added_per_step: float,
        quantile: float,
        precision=1024,
    ) -> np.NDArray:
        if quantile == 0:
            return np.full(shape=num_steps, fill_value=added_per_step)
        return np.quantile(
            [
                self.sample_savings(
                    num_steps=num_steps,
                    start_amount=start_amount,
                    added_per_step=added_per_step,
                )
                for simulation in range(precision)
            ],
            q=quantile,
            axis=0,
        )
