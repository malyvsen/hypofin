from chalice import Chalice

from hypofin import AggregateTrajectory, User, countries, predictions

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
            samples=portfolio_trajectories,
            quantile=0.5,
        ),
        AggregateTrajectory.from_samples(
            scenario_id="pessimistic",
            samples=portfolio_trajectories,
            quantile=0.25,
        ),
        AggregateTrajectory.from_samples(
            scenario_id="worst",
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
                "scenario_id": trajectory.scenario_id,
                "probability": 1 - trajectory.quantile,
                "months_to_goal": trajectory.months_to_goal(user.goal_price),
                "trajectory": list(trajectory.savings[:num_relevant_months]),
            }
            for trajectory in quantile_trajectories + [bank_trajectory]
        ],
        "example_trajectories": [
            list(trajectory.savings) for trajectory in portfolio_trajectories[:64]
        ],
        "allocation": [
            dict(
                **user.safe_investment.metadata,
                current_fraction=user.safe_allocation,
                current_amount=user.current_savings * user.safe_allocation,
                monthly_fraction=user.safe_allocation,
                monthly_amount=user.monthly_savings * user.safe_allocation,
            ),
            dict(
                **predictions.stocks().metadata,
                current_fraction=user.stock_allocation,
                current_amount=user.current_savings * user.stock_allocation,
                monthly_fraction=user.stock_allocation,
                monthly_amount=user.monthly_savings * user.stock_allocation,
            ),
        ],
    }
