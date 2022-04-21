from dataclasses import dataclass
import numpy as np

import chalicelib.predictions as predictions
from .country import Country
from .trajectory import ExplainedTrajectory


@dataclass(frozen=True)
class User:
    current_savings: float
    monthly_savings: float
    goal_price: float
    risk_preference: float
    country: Country

    @property
    def bond_allocation(self):
        return 1 - self.stock_allocation

    @property
    def stock_allocation(self):
        return self.risk_preference / 100

    def sample_trajectory(self, num_months: int):
        """An example trajectory for inflation-adjusted, taxed savings"""
        inflation = self.country.inflation.sample_returns(num_months)
        stock_returns = predictions.stocks().sample_returns(
            num_months=num_months, inflation=inflation
        )
        bond_returns = self.country.bonds.sample_returns(
            num_months=num_months, inflation=inflation
        )
        combined_returns = (
            stock_returns * self.stock_allocation + bond_returns * self.bond_allocation
        )
        pre_tax = ExplainedTrajectory.infer_savings(
            start_amount=self.current_savings,
            additions=self._inflated_additions(inflation),
            returns=combined_returns,
        )
        post_tax = self.country.tax_system.apply(pre_tax)
        return self._deinflated_savings(inflated=post_tax, inflation=inflation)

    def sample_bank_trajectory(self, num_months: int):
        """An example trajectory if the user kept money in the bank, adjusted for inflation"""
        inflation = self.country.inflation.sample_returns(num_months)
        account_balance = ExplainedTrajectory.infer_savings(
            start_amount=self.current_savings,
            additions=self._inflated_additions(inflation),
            returns=np.full(fill_value=0, shape=num_months),
        )
        return self._deinflated_savings(inflated=account_balance, inflation=inflation)

    def _inflated_additions(self, inflation: np.ndarray):
        return np.repeat(self.monthly_savings, len(inflation)) * np.cumprod(
            1 + inflation
        )

    def _deinflated_savings(self, inflated: ExplainedTrajectory, inflation: np.ndarray):
        deinflated = inflated.savings / np.concatenate([[1], np.cumprod(1 + inflation)])
        return ExplainedTrajectory.infer_returns(
            savings=deinflated,
            additions=np.repeat(self.monthly_savings, len(inflation)),
        )
