from dataclasses import dataclass
from functools import cached_property

import numpy as np


@dataclass(frozen=True)
class Portfolio:
    initial_investment: float
    monthly_addition: float
    bond_fraction: float

    @cached_property
    def stock_fraction(self):
        return 1 - self.bond_fraction

    def total_investment(self, num_months: int):
        """The total invested amount over time."""
        return self.initial_investment + np.arange(num_months) * self.monthly_addition
