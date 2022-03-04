from dataclasses import dataclass
import numpy as np

from .country import Country
from .portfolio import MixedPortfolio
from .predictions import bond_portfolio, stock_portfolio, monthly_inflation


@dataclass(frozen=True)
class User:
    current_savings: float
    monthly_savings: float
    goal_price: float
    risk_preference: float
    country: Country

    @property
    def portfolio(self):
        return MixedPortfolio(
            riskless_component=MixedPortfolio.Component(
                weight=self.bond_allocation, portfolio=bond_portfolio()
            ),
            risky_component=MixedPortfolio.Component(
                weight=self.stock_allocation, portfolio=stock_portfolio()
            ),
        )

    @property
    def bond_allocation(self):
        return 1 - self.stock_allocation

    @property
    def stock_allocation(self):
        return self.risk_preference / 100

    def savings_quantile_cached(self, num_months: int, quantile: float):
        """The inflation-adjusted, taxed savings quantile"""
        additions = self.monthly_additions(num_months)
        pre_tax = self.portfolio.savings_quantile_cached(
            additions=additions, quantile=quantile
        )
        return self.apply_losses(pre_tax, monthly_additions=additions)

    def apply_losses(self, monthly_savings: np.ndarray, monthly_additions: np.ndarray):
        post_tax = self.country.tax_system.tax_savings(
            monthly_savings=monthly_savings,
            monthly_additions=monthly_additions,
        )
        return post_tax / np.cumprod(
            np.full(shape=monthly_savings.shape, fill_value=1 + monthly_inflation())
        )

    def bank_savings(self, num_months: int):
        """The user's savings if they were to keep money in the bank"""
        monthly_additions = self.monthly_additions(num_months=num_months)
        return self.apply_losses(
            np.cumsum(monthly_additions), monthly_additions=monthly_additions
        )

    def monthly_additions(self, num_months: int) -> np.ndarray:
        return np.array(
            [self.current_savings] + [self.monthly_savings] * (num_months - 1)
        ) * np.cumprod(np.full(shape=num_months, fill_value=1 + monthly_inflation()))
