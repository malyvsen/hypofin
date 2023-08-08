import numpy as np

from hypofin import Portfolio, Scenario, Trajectory


def test_savings():
    portfolio = Portfolio(initial_investment=10, monthly_addition=1, bond_fraction=0)

    bad_scenario = Scenario(
        inflation=np.zeros(3),
        stock_returns=np.full(fill_value=-0.1, shape=3),
    )
    bad_trajectory = Trajectory(portfolio=portfolio, scenario=bad_scenario)
    assert np.allclose(bad_trajectory.pre_tax_savings, 10)
    assert np.allclose(bad_trajectory.post_tax_savings, 10)

    good_scenario = Scenario(
        inflation=np.zeros(3),
        stock_returns=np.full(fill_value=0.1, shape=3),
    )
    good_trajectory = Trajectory(portfolio=portfolio, scenario=good_scenario)
    assert np.allclose(good_trajectory.pre_tax_savings, [10, 12, 14.2, 16.62])
    assert np.allclose(good_trajectory.post_tax_savings, [10, 11.81, 13.782, 15.9322])
