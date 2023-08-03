import numpy as np

from hypofin.country import countries
from hypofin.user import User


def test_start_amount_consistency():
    user = User(
        risk_preference=50,
        monthly_savings=0,
        goal_price=200,
        current_savings=100,
        country=countries["poland"],
    )
    assert (
        user.sample_trajectory(10).start_amount
        == user.sample_bank_trajectory(10).start_amount
        == user.current_savings
    )


def test_risk_behavior():
    low_risk_user = User(
        risk_preference=10,
        monthly_savings=5,
        goal_price=230,
        current_savings=180,
        country=countries["poland"],
    )
    low_risk_trajectories = [
        low_risk_user.sample_trajectory(num_months=10) for _ in range(16)
    ]
    high_risk_user = User(
        risk_preference=90,
        monthly_savings=5,
        goal_price=230,
        current_savings=180,
        country=countries["poland"],
    )
    high_risk_trajectories = [
        high_risk_user.sample_trajectory(num_months=10) for _ in range(16)
    ]
    assert np.all(
        np.min([trajectory.savings[1:] for trajectory in low_risk_trajectories], axis=0)
        > np.min(
            [trajectory.savings[1:] for trajectory in high_risk_trajectories], axis=0
        )
    )
    assert np.all(
        np.max([trajectory.savings[1:] for trajectory in low_risk_trajectories], axis=0)
        < np.max(
            [trajectory.savings[1:] for trajectory in high_risk_trajectories], axis=0
        )
    )
