from dataclasses import dataclass
import numpy as np
import pandas as pd
import scipy.stats


@dataclass(frozen=True)
class Simulator:
    log_return_distribution: scipy.stats.rv_continuous

    @classmethod
    def from_historical_prices(
        cls, historical_prices: pd.Series, expected_return: float
    ) -> "Simulator":
        historical_log_returns = np.log(historical_prices).diff().dropna()
        loc, scale = scipy.stats.laplace.fit(historical_log_returns)
        return cls(
            log_return_distribution=scipy.stats.laplace(
                np.log(1 + expected_return), scale
            )
        )

    def sample_returns(self, num_steps: int) -> np.ndarray:
        return np.exp(self.log_return_distribution.rvs(num_steps)) - 1

    def sample_savings(
        self, num_steps: int, start_amount: float, added_per_step: float
    ) -> np.ndarray:
        growth_series = 1 + np.concatenate(
            [[0], self.sample_returns(num_steps - 1)], axis=0
        )
        cumulative_growth = np.cumprod(growth_series)
        start_amount_growth = start_amount * cumulative_growth
        added = np.concatenate(
            [[0], np.full(shape=num_steps - 1, fill_value=added_per_step)], axis=0
        )
        added_growth = np.cumsum(added / cumulative_growth) * cumulative_growth
        return start_amount_growth + added_growth
