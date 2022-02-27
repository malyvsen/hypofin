from dataclasses import dataclass
import numpy as np

from .tax_system import TaxSystem


@dataclass(frozen=True)
class User:
    current_savings: float
    monthly_savings: float
    goal_price: float
    risk_preference: float
    tax_system: TaxSystem

    def monthly_additions(self, num_months: int) -> np.ndarray:
        return np.array(
            [self.current_savings] + [self.monthly_savings] * (num_months - 1)
        )
