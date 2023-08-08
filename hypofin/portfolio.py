from dataclasses import dataclass
from functools import cached_property


@dataclass(frozen=True)
class Portfolio:
    initial_investment: float
    monthly_addition: float
    bond_fraction: float

    @cached_property
    def stock_fraction(self):
        return 1 - self.bond_fraction
