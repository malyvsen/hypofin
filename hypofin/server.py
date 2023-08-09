import numpy as np
from fastapi import FastAPI

from .caching import refresh_daily
from .portfolio import Portfolio
from .scenario import Scenario
from .schemas import Request, Response
from .trajectory import Trajectory

NUM_MONTHS = 50 * 12
NUM_SIMULATIONS = 1000

server = FastAPI()


@server.post("/")
def root(request: Request):
    portfolio = Portfolio(
        initial_investment=request.initial_investment,
        monthly_addition=request.monthly_addition,
        bond_fraction=request.bond_fraction,
    )
    trajectories = [
        Trajectory(portfolio=portfolio, scenario=scenario)
        for scenario in hypothetical_scenarios()
    ]
    gain_probability = np.mean(
        [trajectory.gain_indicator for trajectory in trajectories], axis=0
    )
    return Response(
        success_probability=(
            None
            if request.goal_price is None
            else np.mean(
                [
                    trajectory.success_indicator(initial_goal_price=request.goal_price)
                    for trajectory in trajectories
                ],
                axis=0,
            )
        ),
        gain_probability=gain_probability,
        loss_probability=1 - gain_probability,
        bank_trajectory=portfolio.total_investment(NUM_MONTHS),
        scenarios=[
            Response.Scenario(
                savings_trajectory=trajectory.post_tax_savings,
                goal_trajectory=(
                    None
                    if request.goal_price is None
                    else trajectory.scenario.prices(request.goal_price)
                ),
            )
            for trajectory in trajectories
        ],
    )


@refresh_daily
def hypothetical_scenarios():
    return [Scenario.hypothesize(num_months=NUM_MONTHS) for _ in range(NUM_SIMULATIONS)]
