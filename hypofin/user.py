from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    current_savings: float
    monthly_savings: float
    goal_price: float
    risk_preference: float
