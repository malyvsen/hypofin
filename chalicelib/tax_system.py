from dataclasses import dataclass
import numpy as np
import pandas as pd
from typing import Union


accepted_types = Union[np.ndarray, pd.Series]


@dataclass(frozen=True)
class TaxSystem:
    def tax_savings(self, monthly_savings: accepted_types) -> accepted_types:
        raise NotImplementedError()


@dataclass(frozen=True)
class CapitalGainsTaxSystem(TaxSystem):
    tax: float

    def tax_savings(self, monthly_savings: accepted_types) -> accepted_types:
        # FIXME: we don't pay capital gains tax on amounts added per month
        first_savings = np.array(monthly_savings)[0]
        excess_savings = monthly_savings - first_savings
        negative_excess = np.minimum(excess_savings, 0)
        positive_excess = np.maximum(excess_savings, 0)
        return monthly_savings + negative_excess + positive_excess * (1 - self.tax)


@dataclass(frozen=True)
class WealthTaxSystem(TaxSystem):
    tax: float

    def tax_savings(self, monthly_savings: accepted_types) -> accepted_types:
        monthly_multiplier = (1 - self.tax) ** (1 / 12)
        return monthly_savings * np.cumprod(
            np.full_like(monthly_savings, monthly_multiplier)
        )


tax_systems = {
    "poland": CapitalGainsTaxSystem(tax=0.19),
    "netherlands": WealthTaxSystem(tax=0.012),
}
