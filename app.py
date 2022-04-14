from chalice import Chalice
from chalicelib import (
    countries,
    User,
)
import numpy as np


app = Chalice(app_name="hypofin")


@app.route("/", methods=["POST"], cors=True)
def index():
    return response(app.current_request.json_body)


def response(request_data):
    user = User(
        current_savings=request_data["current_savings"],
        monthly_savings=request_data["monthly_savings"],
        goal_price=request_data["goal_price"],
        risk_preference=request_data["risk_preference"],
        country=countries[request_data["country"]],
    )

    max_months = 50 * 12
    bank_trajectory = user.bank_savings(num_months=max_months)
    num_bank_months = trajectory_months(bank_trajectory, goal_price=user.goal_price)
    bank_default_probability = user.country.default_probability(
        num_months=num_bank_months or max_months
    )
    strata = {
        probability: user.savings_quantile(
            num_months=max_months, quantile=1 - probability
        )
        for probability in [0.5, 0.75, 1 - bank_default_probability]
    }

    try:
        num_relevant_months = max(
            trajectory_months(trajectory, goal_price=user.goal_price)
            for trajectory in strata.values()
        )
    except TypeError:
        num_relevant_months = max_months

    return {
        "aggregate_trajectories": [
            {
                "name": f"{probability * 100:.0f}% certainty",
                "description": f"You have a {probability * 100:.0f}% chance of having this much or more money saved up, after tax."
                + (
                    ""
                    if probability <= 0.75
                    else " This is as much certainty as you get in a bank (those go bankrupt sometimes too)."
                ),
                "probability": probability,
                "num_years": trajectory_years(trajectory, goal_price=user.goal_price),
                "trajectory": list(trajectory[:num_relevant_months]),
            }
            for probability, trajectory in strata.items()
        ]
        + [
            {
                "name": "Keeping your money in a bank",
                "description": "For comparison, this is what it would look like if you kept your money on your bank account.",
                "probability": 1 - bank_default_probability,
                "num_years": trajectory_years(
                    bank_trajectory, goal_price=user.goal_price
                ),
                "trajectory": list(bank_trajectory[:num_relevant_months]),
            }
        ],
        "example_trajectories": [
            list(
                user.apply_losses(
                    monthly_savings=user.portfolio.sample_savings(
                        additions=user.monthly_additions(num_relevant_months)
                    ),
                    monthly_additions=user.monthly_additions(num_relevant_months),
                )
            )
            for _ in range(64)
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


def trajectory_months(trajectory, goal_price):
    (success_indices,) = np.where(trajectory >= goal_price)
    return (success_indices[0] + 1) if len(success_indices) > 0 else None


def trajectory_years(trajectory, goal_price):
    months = trajectory_months(trajectory, goal_price=goal_price)
    return int((months + 11) / 12) if months is not None else None
