from dataclasses import dataclass
from typing import Callable, List

import chalicelib.data as data
import chalicelib.predictions as predictions
from .tax_system import TaxSystem, CapitalGainsTaxSystem, WealthTaxSystem
from .return_source import AnnotatedReturnSource


@dataclass(frozen=True)
class Country:
    name: str
    tax_system: TaxSystem
    bond_maturities: List[int]
    bonds: Callable[[int], AnnotatedReturnSource]

    @property
    def inflation(self):
        return predictions.inflation(self.name)

    def default_probability(self, num_months: float):
        monthly = predictions.monthly_default_probability(self.name)
        return 1 - (1 - monthly) ** num_months


countries = {
    country.name: country
    for country in [
        Country(
            name="poland",
            tax_system=CapitalGainsTaxSystem(0.19),
            bond_maturities=list(data.polish_bond_names.keys()),
            bonds=predictions.polish_bonds,
        ),
        Country(
            name="netherlands",
            tax_system=WealthTaxSystem(0.012),
            bond_maturities=[],
            bonds=None,
        ),
    ]
}
