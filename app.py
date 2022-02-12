from chalice import Chalice
import numpy as np
from chalicelib import User, tax_systems


app = Chalice(app_name="hypofin")


@app.route("/", methods=["POST"], cors=True)
def index():
    request_data = app.current_request.json_body
    user = User(
        current_savings=request_data["current_savings"],
        monthly_savings=request_data["monthly_savings"],
        goal_price=request_data["goal_price"],
        risk_preference=request_data["risk_preference"],
        tax_system=tax_systems["poland"],
    )
    num_steps = 256
    sure_evolution = np.linspace(
        request_data["current_savings"], request_data["goal_price"], num=num_steps
    )
    risk_growth = np.cumprod(
        np.full(shape=num_steps, fill_value=1 + request_data["risk_preference"] * 1e-4)
    )
    stock_allocation = user.risk_preference / 100
    return {
        "strata": [
            {
                "probability": 0.5,
                "num_years": 7,
                "evolution": list(sure_evolution * risk_growth),
            },
            {
                "probability": 0.75,
                "num_years": 13,
                "evolution": list(sure_evolution * risk_growth**0.5),
            },
            {
                "probability": 1,
                "num_years": 17,
                "evolution": list(sure_evolution),
            },
        ],
        "bank_variant": {
            "num_years": 14,
            "evolution": list(sure_evolution * risk_growth**0.25),
        },
        "example_evolutions": [
            list(
                request_data["current_savings"]
                * np.cumprod(np.random.uniform(0.95, 1.1, size=256))
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
