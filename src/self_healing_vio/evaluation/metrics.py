"""Trajectory and health-aware benchmark metrics.

The current implementations are intentionally minimal. They provide stable API
entry points for future integration with evo, ROS bag replay, and dataset-specific
ground truth loaders.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np


@dataclass(frozen=True)
class AbsoluteTrajectoryError:
    """Root-mean-square translation error over aligned positions."""

    rmse: float
    mean: float
    max_error: float

    @classmethod
    def from_positions(cls, estimate: Sequence[Sequence[float]], ground_truth: Sequence[Sequence[float]]) -> "AbsoluteTrajectoryError":
        est = np.asarray(estimate, dtype=float)
        gt = np.asarray(ground_truth, dtype=float)
        if est.shape != gt.shape:
            raise ValueError("estimate and ground_truth must have identical shape")
        errors = np.linalg.norm(est - gt, axis=1)
        return cls(rmse=float(np.sqrt(np.mean(errors**2))), mean=float(np.mean(errors)), max_error=float(np.max(errors)))


@dataclass(frozen=True)
class RelativePoseError:
    """Placeholder relative pose error summary."""

    translational_rmse: float
    rotational_rmse_deg: float | None = None


@dataclass(frozen=True)
class BenchmarkSummary:
    """Combined localization and self-healing evaluation summary."""

    sequence: str
    ate_rmse: float
    mean_nhi: float
    minimum_nhi: float
    recovery_actions: int
