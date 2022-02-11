from chalice import Chalice
import numpy as np


app = Chalice(app_name="hypofin")


@app.route("/", methods=["POST"], cors=True)
def index():
    request_data = app.current_request.json_body
    return {
        "strata": [
            {
                "probability": 0.5,
                "num_years": 7,
                "evolution": [
                    request_data["current_savings"] * 1.03**step
                    for step in range(256)
                ],
            },
            {
                "probability": 0.75,
                "num_years": 13,
                "evolution": [
                    request_data["current_savings"] * 1.02**step
                    for step in range(256)
                ],
            },
            {
                "probability": 1,
                "num_years": 17,
                "evolution": [
                    request_data["current_savings"] * 1.01**step
                    for step in range(256)
                ],
            },
        ],
        "bank_variant": {
            "num_years": 14,
            "evolution": [
                request_data["current_savings"] * 1.015**step for step in range(256)
            ],
        },
        "example_evolutions": [
            list(
                request_data["current_savings"]
                * np.cumprod(np.random.uniform(0.95, 1.1, size=256))
            )
            for _ in range(64)
        ],
    }
