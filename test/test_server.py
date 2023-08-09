from hypofin import Request
from hypofin.server import root


def test_known_goal():
    response = root(
        Request(
            initial_investment=100,
            monthly_addition=10,
            bond_fraction=0.5,
            goal_price=500,
        )
    )
    assert (
        len(response.success_probability)
        == len(response.gain_probability)
        == len(response.loss_probability)
        == len(response.bank_trajectory)
    )
    assert response.success_probability[0] == 0
    assert response.success_probability[-1] > 0.9
