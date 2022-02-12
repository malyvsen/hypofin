from dataclasses import dataclass

from .tax_system import TaxSystem


@dataclass(frozen=True)
class User:
    current_savings: float
    monthly_savings: float
    goal_price: float
    risk_preference: float
    tax_system: TaxSystem
