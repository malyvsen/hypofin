import numpy as np

from hypofin import Portfolio, Scenario, Trajectory


def test_bad_stocks():
    portfolio = Portfolio(initial_investment=10, monthly_addition=1, bond_fraction=0)
    scenario = Scenario(
        inflation=np.zeros(3),
        stock_returns=np.full(fill_value=-0.1, shape=3),
    )
    trajectory = Trajectory(portfolio=portfolio, scenario=scenario)
    assert np.allclose(trajectory.pre_tax_savings, 10)
    assert np.allclose(trajectory.post_tax_savings, 10)


def test_good_stocks():
    portfolio = Portfolio(initial_investment=10, monthly_addition=1, bond_fraction=0)
    scenario = Scenario(
        inflation=np.zeros(3),
        stock_returns=np.full(fill_value=0.1, shape=3),
    )
    trajectory = Trajectory(portfolio=portfolio, scenario=scenario)
    assert np.allclose(trajectory.pre_tax_savings, [10, 12, 14.2, 16.62])
    assert np.allclose(trajectory.post_tax_savings, [10, 11.81, 13.782, 15.9322])


def test_short_bonds():
    portfolio = Portfolio(initial_investment=10, monthly_addition=1, bond_fraction=1)
    scenario = Scenario(
        inflation=np.full(fill_value=0.01, shape=3),
        stock_returns=np.zeros(3),
    )
    trajectory = Trajectory(portfolio=portfolio, scenario=scenario)
    assert np.all(10 <= trajectory.post_tax_savings)
    assert np.all(trajectory.post_tax_savings < 15)
    assert np.all(trajectory.post_tax_savings <= trajectory.pre_tax_savings)


def test_long_bonds():
    portfolio = Portfolio(initial_investment=10, monthly_addition=1, bond_fraction=1)
    scenario = Scenario(
        inflation=np.full(fill_value=0.01, shape=24),
        stock_returns=np.zeros(24),
    )
    trajectory = Trajectory(portfolio=portfolio, scenario=scenario)
    assert np.all(10 <= trajectory.post_tax_savings)
    assert np.all(trajectory.post_tax_savings < 40)
    assert np.all(trajectory.post_tax_savings <= trajectory.pre_tax_savings)
