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