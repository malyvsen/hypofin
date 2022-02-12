from chalice import Chalice
import numpy as np


app = Chalice(app_name="hypofin")


@app.route("/", methods=["POST"], cors=True)
def index():
    request_data = app.current_request.json_body
    growth = np.cumprod(
        np.full(shape=256, fill_value=1 + request_data["risk_preference"] / 100)
    )
    monthly_growth = (
        np.cumsum(np.full_like(growth, request_data["monthly_savings"]) / growth)
        * growth
    )
    return {
        "strata": [
            {
                "probability": 0.5,
                "num_years": 7,
                "evolution": list(
                    request_data["current_savings"] * growth + monthly_growth
                ),
            },
            {
                "probability": 0.75,
                "num_years": 13,
                "evolution": list(request_data["current_savings"] + monthly_growth),
            },
            {
                "probability": 1,
                "num_years": 17,
                "evolution": list(
                    request_data["current_savings"] / growth + monthly_growth
                ),
            },
        ],
        "bank_variant": {
            "num_years": 14,
            "evolution": list(
                request_data["current_savings"]
                + np.cumsum(np.full_like(growth, request_data["monthly_savings"]))
            ),
        },
        "example_evolutions": [
            list(
                request_data["current_savings"]
                * np.cumprod(np.random.uniform(0.95, 1.1, size=256))
            )
            for _ in range(64)
        ],
    }
