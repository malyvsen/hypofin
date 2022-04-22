from dataclasses import dataclass
from functools import cached_property
import numpy as np

import chalicelib.predictions as predictions
from .country import Country
from .return_source import AnnotatedReturnSource, RisklessReturnSource
from .trajectory import ExplainedTrajectory


@dataclass(frozen=True)
class User:
    current_savings: float
    monthly_savings: float
    goal_price: float
    risk_preference: float
    country: Country

    @property
    def safe_allocation(self):
        return 1 - self.stock_allocation

    @property
    def stock_allocation(self):
        return self.risk_preference / 100

    @cached_property
    def safe_investment(self):
        bank_account = AnnotatedReturnSource(
            metadata=dict(name="Bank account"),
            return_source=RisklessReturnSource(monthly_return=0),
        )
        if len(self.country.bond_maturities) == 0:
            return bank_account
        max_maturity = max(self.country.bond_maturities)
        inflation = self.country.inflation.sample_returns(max_maturity)
        for maturity in sorted(self.country.bond_maturities, reverse=True):
            bonds = self.country.bonds(maturity)
            bond_returns = bonds.sample_returns(
                num_months=max_maturity, inflation=inflation
            )
            trajectory = self._trajectory(returns=bond_returns, inflation=inflation)
            months_to_goal = trajectory.months_to_goal(self.goal_price)
            if months_to_goal is None or months_to_goal >= maturity:
                return bonds
        return bank_account

    def sample_trajectory(self, num_months: int):
        """An example trajectory for inflation-adjusted, taxed savings"""
        inflation = self.country.inflation.sample_returns(num_months)
        stock_returns = predictions.stocks().sample_returns(
            num_months=num_months, inflation=inflation
        )
        safe_returns = self.safe_investment.sample_returns(
            num_months=num_months, inflation=inflation
        )
        combined_returns = (
            stock_returns * self.stock_allocation + safe_returns * self.safe_allocation
        )
        return self._trajectory(returns=combined_returns, inflation=inflation)

    def sample_bank_trajectory(self, num_months: int):
        """An example trajectory if the user kept money in the bank, adjusted for inflation"""
        inflation = self.country.inflation.sample_returns(num_months)
        account_balance = ExplainedTrajectory.infer_savings(
            start_amount=self.current_savings,
            additions=self._inflated_additions(inflation),
            returns=np.full(fill_value=0, shape=num_months),
        )
        return self._deinflated_savings(inflated=account_balance, inflation=inflation)

    def _trajectory(self, returns: np.ndarray, inflation: np.ndarray):
        pre_tax = ExplainedTrajectory.infer_savings(
            start_amount=self.current_savings,
            additions=self._inflated_additions(inflation),
            returns=returns,
        )
        post_tax = self.country.tax_system.apply(pre_tax)
        return self._deinflated_savings(inflated=post_tax, inflation=inflation)

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
