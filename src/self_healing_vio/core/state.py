"""Typed state containers for SHIELD-VIO.

These dataclasses provide a stable internal representation for health vectors,
diagnosis results, recovery decisions, and VIO state summaries. They coexist
with the legacy API used by the current tests.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

import numpy as np

from .types import FailureCause, HealthLevel, RecoveryAction


def _as_float_map(values: Mapping[str, float]) -> dict[str, float]:
    return {str(k): float(v) for k, v in values.items()}


@dataclass(frozen=True)
class HealthVector:
    """Normalized detector health vector.

    Scores are expected to lie in [0, 1], where 1 denotes nominal operation and
    0 denotes severe degradation. The class clips values to protect downstream
    fusion and diagnosis modules from invalid numeric input.
    """

    scores: Mapping[str, float]
    timestamp: float | None = None
    metadata: Mapping[str, object] = field(default_factory=dict)

    def as_dict(self) -> dict[str, float]:
        return {name: float(np.clip(value, 0.0, 1.0)) for name, value in _as_float_map(self.scores).items()}

    def mean(self) -> float:
        values = list(self.as_dict().values())
        if not values:
            raise ValueError("HealthVector requires at least one score")
        return float(np.mean(values))


@dataclass(frozen=True)
class DiagnosisResult:
    """Posterior distribution over degradation causes."""

    posterior: Mapping[FailureCause | str, float]
    dominant_cause: FailureCause | str | None = None

    def normalized(self) -> dict[str, float]:
        raw = {str(k.value if isinstance(k, FailureCause) else k): max(float(v), 0.0) for k, v in self.posterior.items()}
        total = sum(raw.values())
        if total <= 0.0:
            raise ValueError("Diagnosis posterior must have positive mass")
        return {cause: value / total for cause, value in raw.items()}

    def dominant(self) -> str:
        if self.dominant_cause is not None:
            return str(self.dominant_cause.value if isinstance(self.dominant_cause, FailureCause) else self.dominant_cause)
        posterior = self.normalized()
        return max(posterior, key=posterior.get)


@dataclass(frozen=True)
class NavigationHealthState:
    """Autonomy-facing health summary."""

    health_vector: HealthVector
    nhi: float
    level: HealthLevel
    diagnosis: DiagnosisResult | None = None

    def clipped_nhi(self) -> float:
        return float(np.clip(self.nhi, 0.0, 100.0))


@dataclass(frozen=True)
class VIOState:
    """Minimal backend-agnostic VIO state summary.

    This intentionally stores only commonly available quantities. Backend-specific
    factor graph, EKF, or sliding-window details should live in backend adapters.
    """

    timestamp: float
    pose: np.ndarray | None = None
    velocity: np.ndarray | None = None
    covariance: np.ndarray | None = None
    tracked_features: int | None = None
    mean_reprojection_error: float | None = None


@dataclass(frozen=True)
class RecoveryDecision:
    """Typed recovery decision for new SHIELD-VIO modules."""

    action: RecoveryAction | str
    priority: int
    reason: str = ""
    confidence: float | None = None

    def action_name(self) -> str:
        return str(self.action.value if isinstance(self.action, RecoveryAction) else self.action)
