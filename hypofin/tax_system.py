from dataclasses import dataclass

import numpy as np

from .trajectory import ExplainedTrajectory


@dataclass(frozen=True)
class TaxSystem:
    def apply(self, trajectory: ExplainedTrajectory) -> ExplainedTrajectory:
        raise NotImplementedError()


@dataclass(frozen=True)
class CapitalGainsTaxSystem(TaxSystem):
    tax: float

    def apply(self, trajectory: ExplainedTrajectory) -> ExplainedTrajectory:
        total_investment = np.cumsum(
            np.concatenate([[trajectory.start_amount], trajectory.additions])
        )
        excess_savings = trajectory.savings - total_investment
        negative_excess = np.minimum(excess_savings, 0)
        positive_excess = np.maximum(excess_savings, 0)
        return ExplainedTrajectory.infer_returns(
            savings=total_investment
            + negative_excess
            + positive_excess * (1 - self.tax),
            additions=trajectory.additions,
        )


@dataclass(frozen=True)
class WealthTaxSystem(TaxSystem):
    tax: float

    def apply(self, trajectory: ExplainedTrajectory) -> ExplainedTrajectory:
        monthly_tax = 1 - (1 - self.tax) ** (1 / 12)
        return ExplainedTrajectory.infer_savings(
            start_amount=trajectory.start_amount,
            additions=trajectory.additions,
            returns=trajectory.returns - monthly_tax,
        )
