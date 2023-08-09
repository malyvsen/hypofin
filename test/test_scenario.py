import numpy as np

from hypofin import Scenario
from hypofin.data import historical_inflation_pln


def test_hypothesize_inflation_accuracy():
    """Hypothesize lots of scenarios and see whether they resemble history."""
    scenarios = [
        Scenario.hypothesize(len(historical_inflation_pln()) * 12) for _ in range(1000)
    ]
    realized_inflation = (1 + historical_inflation_pln()).prod()
    scenarios_below_realized = [
        scenario
        for scenario in scenarios
        if (1 + scenario.inflation).prod() < realized_inflation
    ]
    assert 0.4 < len(scenarios_below_realized) / len(scenarios) < 0.6


def test_cumulative_inflation():
    scenario = Scenario(
        inflation=np.full(fill_value=1, shape=3),
        stock_returns=np.full(fill_value=-0.1, shape=3),
    )
    assert np.allclose(scenario.cumulative_inflation, [0, 1, 3, 7])


def test_inflated_price():
    scenario = Scenario(
        inflation=np.full(fill_value=0.5, shape=3),
        stock_returns=np.full(fill_value=-0.1, shape=3),
    )
    assert np.allclose(scenario.inflated_price(8), [8, 12, 18, 27])
