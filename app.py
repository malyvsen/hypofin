from chalice import Chalice
from chalicelib import User, AggregateTrajectory, countries
import numpy as np


app = Chalice(app_name="hypofin")


@app.route("/", methods=["POST"], cors=True)
def index():
    user_data = app.current_request.json_body
    return response(
        User(
            current_savings=user_data["current_savings"],
            monthly_savings=user_data["monthly_savings"],
            goal_price=user_data["goal_price"],
            risk_preference=user_data["risk_preference"],
            country=countries[user_data["country"]],
        )
    )


def response(user: User, max_months=50 * 12):
    bank_trajectory = AggregateTrajectory.from_samples(
        scenario_id="bank",
        name="Bank account",
        description=(
            "For comparison, this is what you would get on average if you kept your money in a bank account."
            + " We show your inflation-adjusted savings, so you can see inflation eating away at your money."
        ),
        samples=[user.sample_bank_trajectory(max_months) for sample_idx in range(256)],
        quantile=0.5,
    )
    default_probability = user.country.default_probability(
        bank_trajectory.months_to_goal(user.goal_price) or max_months
    )
    portfolio_trajectories = [
        user.sample_trajectory(max_months) for sample_idx in range(1024)
    ]
    quantile_trajectories = [
        AggregateTrajectory.from_samples(
            scenario_id="average",
            name="Average scenario",
            description=(
                "This line marks the border between the top and bottom half of all scenarios."
                + " You can interpret it as an average case."
            ),
            samples=portfolio_trajectories,
            quantile=0.5,
        ),
        AggregateTrajectory.from_samples(
            scenario_id="pessimistic",
            name="Pessimistic scenario",
            description="Your savings will be above this line 75% of the time.",
            samples=portfolio_trajectories,
            quantile=0.25,
        ),
        AggregateTrajectory.from_samples(
            scenario_id="worst_case",
            name="As safe as in a bank",
            description=(
                f"Your savings will be above this line {(1 - default_probability) * 100:.1f}% of the time."
                + " This is as safe as keeping your money in a bank - those go bankrupt sometimes too."
            ),
            samples=portfolio_trajectories,
            quantile=default_probability,
        ),
    ]

    try:
        num_relevant_months = max(
            trajectory.months_to_goal(goal=user.goal_price)
            for trajectory in quantile_trajectories
        )
    except TypeError:
        num_relevant_months = max_months

    return {
        "aggregate_trajectories": [
            {
                "name": trajectory.name,
                "description": trajectory.description,
                "probability": 1 - trajectory.quantile,
                "num_years": trajectory.years_to_goal(user.goal_price),
                "trajectory": list(trajectory.savings[:num_relevant_months]),
            }
            for trajectory in [bank_trajectory] + quantile_trajectories
        ],
        "example_trajectories": [
            list(trajectory.savings) for trajectory in portfolio_trajectories[:64]
        ],
        "allocation": [
            {
                "name": "Amundi ETF J.P. Morgan GBI Global Government Bonds UCITS ETF DR",
                "isin": " LU1437016204",
                "current_fraction": user.bond_allocation,
                "current_amount": user.current_savings * user.bond_allocation,
                "monthly_fraction": user.bond_allocation,
                "monthly_amount": user.current_savings * user.bond_allocation,
            },
            {
                "name": "Lyxor Core MSCI World (DR) UCITS ETF - Acc",
                "isin": "LU1781541179",
                "current_fraction": user.stock_allocation,
                "current_amount": user.current_savings * user.stock_allocation,
                "monthly_fraction": user.stock_allocation,
                "monthly_amount": user.current_savings * user.stock_allocation,
            },
        ],
    }
