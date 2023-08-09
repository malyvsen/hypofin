from pydantic import BaseModel


class Request(BaseModel):
    initial_investment: float
    monthly_addition: float
    bond_fraction: float
    goal_price: float | None


class Response(BaseModel):
    success_probability: list[float]
    """The probability of achieving the goal over time."""
    gain_probability: list[float]
    """The probability of making money over time."""
    loss_probability: list[float]
    """The probability of losing money over time."""
    bank_trajectory: list[float]
    scenarios: list["Response.Scenario"]

    class Scenario(BaseModel):
        savings_trajectory: list[float]
        goal_trajectory: list[float] | None
