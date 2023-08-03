import numpy as np

from hypofin.tax_system import CapitalGainsTaxSystem, WealthTaxSystem
from hypofin.trajectory import ExplainedTrajectory


def test_capital_gains():
    pre_tax = ExplainedTrajectory.infer_returns(
        savings=np.array([10, 12, 10, 13]), additions=np.array([1, 1, 2])
    )
    post_tax = CapitalGainsTaxSystem(tax=0.5).apply(pre_tax)
    assert np.allclose(post_tax.savings, [10, 11.5, 10, 13])


def test_wealth():
    pre_tax = ExplainedTrajectory.infer_savings(
        start_amount=10, additions=np.array([1, 1, 2]), returns=np.array([0.5, -0.5, 1])
    )
    post_tax = WealthTaxSystem(tax=1 - (1 - 0.25) ** 12).apply(pre_tax)
    assert np.allclose(post_tax.returns, [0.25, -0.75, 0.75])
