from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class TaxSystem:
    def tax_savings(
        self, monthly_savings: np.ndarray, monthly_additions: np.ndarray
    ) -> np.ndarray:
        """The saved amount after tax, new money was being added as per monthly_additions"""
        raise NotImplementedError()


@dataclass(frozen=True)
class CapitalGainsTaxSystem(TaxSystem):
    tax: float

    def tax_savings(
        self, monthly_savings: np.ndarray, monthly_additions: np.ndarray
    ) -> np.ndarray:
        excess_savings = monthly_savings - np.cumsum(monthly_additions)
        negative_excess = np.minimum(excess_savings, 0)
        positive_excess = np.maximum(excess_savings, 0)
        return monthly_savings + negative_excess + positive_excess * (1 - self.tax)


@dataclass(frozen=True)
class WealthTaxSystem(TaxSystem):
    tax: float

    def tax_savings(
        self, monthly_savings: np.ndarray, monthly_additions: np.ndarray
    ) -> np.ndarray:
        monthly_tax = 1 - (1 - self.tax) ** (1 / 12)
        monthly_returns = (monthly_savings - monthly_additions) / np.concatenate(
            [[1], monthly_savings[:-1]]
        ) - 1
        taxed_returns = monthly_returns - monthly_tax
        cumulative_taxed_growth = np.cumprod(1 + taxed_returns)
        return (
            np.cumsum(monthly_additions / cumulative_taxed_growth)
            * cumulative_taxed_growth
        )


tax_systems = {
    "poland": CapitalGainsTaxSystem(tax=0.19),
    "netherlands": WealthTaxSystem(tax=0.012),
}
