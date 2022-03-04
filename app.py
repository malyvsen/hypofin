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
    bank_evolution = user.bank_savings(num_months=max_months)
    num_bank_months = evolution_months(bank_evolution, goal_price=user.goal_price)
    bank_default_probability = user.country.default_probability(
        num_months=num_bank_months or max_months
    )
    strata = {
        probability: user.savings_quantile_cached(
            num_months=max_months, quantile=1 - probability
        )
        for probability in [0.5, 0.75, 1 - bank_default_probability]
    }

    try:
        num_relevant_months = max(
            evolution_months(evolution, goal_price=user.goal_price)
            for evolution in strata.values()
        )
    except TypeError:
        num_relevant_months = max_months

    return {
        "strata": [
            {
                "probability": probability,
                "num_years": evolution_years(evolution, goal_price=user.goal_price),
                "evolution": list(evolution[:num_relevant_months]),
            }
            for probability, evolution in strata.items()
        ],
        "bank_variant": {
            "probability": 1 - bank_default_probability,
            "num_years": evolution_years(bank_evolution, goal_price=user.goal_price),
            "evolution": list(bank_evolution[:num_relevant_months]),
        },
        "example_evolutions": [
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


def evolution_months(evolution, goal_price):
    (success_indices,) = np.where(evolution >= goal_price)
    return (success_indices[0] + 1) if len(success_indices) > 0 else None


def evolution_years(evolution, goal_price):
    months = evolution_months(evolution, goal_price=goal_price)
    return int((months + 11) / 12) if months is not None else None
