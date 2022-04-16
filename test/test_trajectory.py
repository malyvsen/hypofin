import numpy as np

from chalicelib.trajectory import ExplainedTrajectory


def test_returns_reconstruction():
    original = ExplainedTrajectory.infer_savings(
        start_amount=np.random.uniform(0, 1),
        additions=np.random.uniform(0, 1, size=4),
        returns=np.random.uniform(-0.1, 0.2, size=4),
    )
    reconstructed = ExplainedTrajectory.infer_returns(
        savings=original.savings, additions=original.additions
    )
    assert np.allclose(reconstructed.returns, original.returns)


def test_savings_reconstruction():
    original = ExplainedTrajectory.infer_returns(
        savings=np.cumsum(np.random.uniform(0, 2, size=5)),
        additions=np.random.uniform(0, 1, size=4),
    )
    reconstructed = ExplainedTrajectory.infer_savings(
        start_amount=original.start_amount,
        additions=original.additions,
        returns=original.returns,
    )
    assert np.allclose(reconstructed.savings, original.savings)
