from dataclasses import dataclass

from .predictions import monthly_default_probability
from .tax_system import TaxSystem, CapitalGainsTaxSystem, WealthTaxSystem


@dataclass(frozen=True)
class Country:
    name: str
    tax_system: TaxSystem

    def default_probability(self, num_months: float):
        monthly = monthly_default_probability(self.name)
        return 1 - (1 - monthly) ** num_months


countries = {
    country.name: country
    for country in [
        Country(name="poland", tax_system=CapitalGainsTaxSystem(0.19)),
        Country(name="netherlands", tax_system=WealthTaxSystem(0.012)),
    ]
}
