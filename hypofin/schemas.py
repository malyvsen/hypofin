from pydantic import BaseModel


class Request(BaseModel):
    initial_investment: float
    monthly_addition: float
    bond_fraction: float
    goal_price: float | None


class Response(BaseModel):
    success_probability: list[float]
    """The probability of achieving the goal,
    or making money at all if no goal is provided."""
    loss_probability: list[float]
    bank_trajectory: list[float]
    scenarios: list["Response.Scenario"]

    class Scenario(BaseModel):
        savings_trajectory: list[float]
        goal_trajectory: list[float] | None
