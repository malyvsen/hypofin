from chalicelib.user import User
from chalicelib.country import countries


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
