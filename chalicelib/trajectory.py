from dataclasses import dataclass
import numpy as np
from typing import List


@dataclass(frozen=True)
class Trajectory:
    """A sequence of savings, month-by-month."""

    savings: np.ndarray

    @property
    def start_amount(self) -> float:
        return self.savings[0]

    def years_to_goal(self, goal: float) -> int:
        """The number of years until the goal is reached, or None if it is never reached"""
        months = self.months_to_goal(goal)
        return int((months + 11) / 12) if months is not None else None

    def months_to_goal(self, goal: float) -> int:
        """The number of months until the goal is reached, or None if it is never reached"""
        (success_indices,) = np.where(self.savings >= goal)
        return success_indices[0] if len(success_indices) > 0 else None


@dataclass(frozen=True)
class ExplainedTrajectory(Trajectory):
    """A sequence of savings, month-by-month, and some extra data explaining how it was achieved."""

    additions: np.ndarray
    """additions[i] is added in-between savings[i] and savings[i + 1]"""
    returns: np.ndarray
    """returns[i] is the return between savings[i] and savings[i + 1]"""

    @classmethod
    def infer_savings(
        cls, start_amount: float, additions: np.ndarray, returns: np.ndarray
    ):
        started_additions = np.concatenate([[start_amount], additions])
        cumulative_growth = np.concatenate([[1], np.cumprod(1 + returns)])
        return cls(
            savings=np.cumsum(started_additions / cumulative_growth)
            * cumulative_growth,
            additions=additions,
            returns=returns,
        )

    @classmethod
    def infer_returns(cls, savings: np.ndarray, additions: np.ndarray):
        return cls(
            savings=savings,
            additions=additions,
            returns=(savings[1:] - additions) / savings[:-1] - 1,
        )

    def __post_init__(self):
        assert (len(self.savings) - 1) == len(self.additions) == len(self.returns)


@dataclass(frozen=True)
class AggregateTrajectory(Trajectory):
    scenario_id: str
    name: str
    description: str
    quantile: float

    @classmethod
    def from_samples(
        cls,
        scenario_id: str,
        name: str,
        description: str,
        samples: List[Trajectory],
        quantile: float,
    ):
        return cls(
            scenario_id=scenario_id,
            name=name,
            description=description,
            savings=np.quantile(
                [sample.savings for sample in samples], q=quantile, axis=0
            ),
            quantile=quantile,
        )
