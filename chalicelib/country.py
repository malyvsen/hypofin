from dataclasses import dataclass

import chalicelib.predictions as predictions
from .tax_system import TaxSystem, CapitalGainsTaxSystem, WealthTaxSystem


@dataclass(frozen=True)
class Country:
    name: str
    tax_system: TaxSystem

    @property
    def bonds(self):
        return predictions.bonds(self.name)

    @property
    def inflation(self):
        return predictions.inflation(self.name)

    def default_probability(self, num_months: float):
        monthly = predictions.monthly_default_probability(self.name)
        return 1 - (1 - monthly) ** num_months


countries = {
    country.name: country
    for country in [
        Country(name="poland", tax_system=CapitalGainsTaxSystem(0.19)),
        Country(name="netherlands", tax_system=WealthTaxSystem(0.012)),
    ]
}
