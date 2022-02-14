from chalice import Chalice
import numpy as np
from chalicelib import (
    BalancedPortfolio,
    bank_portfolio,
    bond_portfolio,
    stock_portfolio,
    tax_systems,
    User,
)


app = Chalice(app_name="hypofin")


@app.route("/", methods=["POST"], cors=True)
def index():
    request_data = app.current_request.json_body
    user = User(
        current_savings=request_data["current_savings"],
        monthly_savings=request_data["monthly_savings"],
        goal_price=request_data["goal_price"],
        risk_preference=request_data["risk_preference"],
        tax_system=tax_systems[request_data["tax_system"]],
    )
    stock_allocation = user.risk_preference / 100
    portfolio = BalancedPortfolio(
        [
            BalancedPortfolio.Component(
                weight=1 - stock_allocation, portfolio=bond_portfolio()
            ),
            BalancedPortfolio.Component(
                weight=stock_allocation, portfolio=stock_portfolio()
            ),
        ]
    )
    max_months = 50 * 12
    strata = {
        probability: portfolio.quantile(
            num_steps=max_months,
            start_amount=user.current_savings,
            added_per_step=user.monthly_savings,
            quantile=1 - probability,
        )
        for probability in [0.5, 0.75, 1]
    }

    def evolution_months(evolution):
        success_indices = np.where(evolution >= user.goal_price)
        return (success_indices[0] + 1) if len(success_indices) > 0 else None

    def evolution_years(evolution):
        months = evolution_months(evolution)
        return int((months + 11) / 12) if months is not None else None

    num_relevant_months = evolution_months(strata[1])
    if num_relevant_months is None:
        num_relevant_months = max_months

    bank_evolution = bank_portfolio().sample_savings(
        num_steps=num_relevant_months,
        start_amount=user.current_savings,
        added_per_step=user.monthly_savings,
    )
    return {
        "strata": [
            {
                "probability": probability,
                "num_years": evolution_years(evolution),
                "evolution": list(evolution[:num_relevant_months]),
            }
            for probability, evolution in strata.items()
        ],
        "bank_variant": {
            "num_years": evolution_years(bank_evolution),
            "evolution": list(bank_evolution),
        },
        "example_evolutions": [
            list(
                portfolio.sample_savings(
                    num_steps=num_relevant_months,
                    start_amount=user.current_savings,
                    added_per_step=user.monthly_savings,
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
