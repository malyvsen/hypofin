from chalice import Chalice
import numpy as np


app = Chalice(app_name="hypofin")


@app.route("/", methods=["POST"], cors=True)
def index():
    request_data = app.current_request.json_body
    num_steps = 256
    sure_evolution = np.linspace(
        request_data["current_savings"], request_data["goal_price"], num=num_steps
    )
    risk_growth = np.cumprod(
        np.full(shape=num_steps, fill_value=1 + request_data["risk_preference"] * 1e-4)
    )
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
    }
