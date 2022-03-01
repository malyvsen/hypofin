from chalice import Chalice
from chalicelib import (
    MixedPortfolio,
    bank_portfolio,
    bond_portfolio,
    stock_portfolio,
    tax_systems,
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
        tax_system=tax_systems[request_data["tax_system"]],
    )

    stock_allocation = user.risk_preference / 100
    portfolio = MixedPortfolio(
        riskless_component=MixedPortfolio.Component(
            weight=1 - stock_allocation, portfolio=bond_portfolio()
        ),
        risky_component=MixedPortfolio.Component(
            weight=stock_allocation, portfolio=stock_portfolio()
        ),
    )

    max_months = 50 * 12
    strata = {
        probability: user.tax_system.tax_savings(
            monthly_savings=portfolio.savings_quantile_cached(
                additions=user.monthly_additions(max_months), quantile=1 - probability
            ),
            monthly_additions=user.monthly_additions(max_months),
        )
        for probability in [0.5, 0.75, 1]
    }

    num_relevant_months = evolution_months(strata[1], goal_price=user.goal_price)
    if num_relevant_months is None:
        num_relevant_months = max_months

    bank_evolution = bank_portfolio().sample_savings(
        additions=user.monthly_additions(max_months)
    )
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
            "num_years": evolution_years(bank_evolution, goal_price=user.goal_price),
            "evolution": list(bank_evolution[:num_relevant_months]),
        },
        "example_evolutions": [
            list(
                user.tax_system.tax_savings(
                    monthly_savings=portfolio.sample_savings(
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
                "current_fraction": 1 - stock_allocation,
                "current_amount": user.current_savings * (1 - stock_allocation),
                "monthly_fraction": 1 - stock_allocation,
                "monthly_amount": user.current_savings * (1 - stock_allocation),
            },
            {
                "name": "Lyxor Core MSCI World (DR) UCITS ETF - Acc",
                "isin": "LU1781541179",
                "current_fraction": stock_allocation,
                "current_amount": user.current_savings * stock_allocation,
                "monthly_fraction": stock_allocation,
                "monthly_amount": user.current_savings * stock_allocation,
            },
        ],
    }


def evolution_months(evolution, goal_price):
    (success_indices,) = np.where(evolution >= goal_price)
    return (success_indices[0] + 1) if len(success_indices) > 0 else None


def evolution_years(evolution, goal_price):
    months = evolution_months(evolution, goal_price=goal_price)
    return int((months + 11) / 12) if months is not None else None
