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

    def sample_returns(self, num_months: int):
        return np.exp(self.log_return_distribution.rvs(num_months)) - 1
