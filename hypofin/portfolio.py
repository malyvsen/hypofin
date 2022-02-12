from dataclasses import dataclass
import math
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

    def stratum(
        self,
        num_steps: int,
        start_amount: float,
        added_per_step: float,
        stratum: float,
        precision=1024,
    ) -> np.ndarray:
        assert 0 <= stratum <= 1
        if stratum == 1:
            return self.certain_stratum(
                num_steps=num_steps,
                start_amount=start_amount,
                added_per_step=added_per_step,
            )
        return np.quantile(
            [
                self.sample_savings(
                    num_steps=num_steps,
                    start_amount=start_amount,
                    added_per_step=added_per_step,
                )
                for simulation in range(precision)
            ],
            q=1 - stratum,
            axis=0,
        )

    def certain_stratum(
        self, num_steps: int, start_amount: float, added_per_step: float
    ) -> np.ndarray:
        raise NotImplementedError()

    def steps_until_certain(
        self, start_amount: float, added_per_step: float, savings_goal: float
    ) -> float:
        """The number of steps until we are 100% sure that the goal reached"""
        raise NotImplementedError()


@dataclass(frozen=True)
class BalancedPortfolio(Portfolio):
    @dataclass(frozen=True)
    class Component:
        weight: float
        portfolio: Portfolio

    components: List[Component]

    @property
    def riskless_components(self):
        return [
            component
            for component in self.components
            if isinstance(component, RisklessPortfolio)
        ]

    @property
    def riskless_weight(self):
        return sum(component.weight for component in self.riskless_components)

    def sample_returns(self, num_steps: int) -> np.ndarray:
        return sum(
            component.weight * component.portfolio.sample_returns(num_steps)
            for component in self.components
        )

    def certain_stratum(
        self, num_steps: int, start_amount: float, added_per_step: float
    ) -> np.ndarray:
        return sum(
            component.certain_stratum(
                num_steps=num_steps,
                start_amount=start_amount * component.weight,
                added_per_step=added_per_step * component.weight,
            )
            for component in self.riskless_components
        )

    def steps_until_certain(
        self, start_amount: float, added_per_step: float, savings_goal: float
    ):
        riskless_return = sum(
            component.return_per_step * component.weight / self.riskless_weight
            for component in self.riskless_components
        )
        return RisklessPortfolio(return_per_step=riskless_return).steps_until_certain(
            start_amount=start_amount * self.riskless_weight,
            added_per_step=added_per_step * self.riskless_weight,
            savings_goal=savings_goal,
        )


@dataclass(frozen=True)
class RisklessPortfolio(Portfolio):
    return_per_step: float

    def sample_returns(self, num_steps: int) -> np.ndarray:
        return np.full(shape=num_steps, fill_value=self.return_per_step)

    def certain_stratum(
        self, num_steps: int, start_amount: float, added_per_step: float
    ) -> np.ndarray:
        return self.sample_savings(
            num_steps=num_steps,
            start_amount=start_amount,
            added_per_step=added_per_step,
        )

    def steps_until_certain(
        self, start_amount: float, added_per_step: float, savings_goal: float
    ):
        growth_per_step = 1 + self.return_per_step
        added_contribution = added_per_step / math.log(growth_per_step)
        return math.log(
            (savings_goal + added_contribution) / (start_amount + added_contribution),
            base=growth_per_step,
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

    def sample_returns(self, num_steps: int) -> np.ndarray:
        return np.exp(self.log_return_distribution.rvs(num_steps)) - 1

    def certain_stratum(
        self, num_steps: int, start_amount: float, added_per_step: float
    ) -> np.ndarray:
        raise RuntimeError("Risky portfolio has no certainty")

    def steps_until_certain(
        self, start_amount: float, added_per_step: float, savings_goal: float
    ):
        raise RuntimeError("Risky portfolio has no certainty")
