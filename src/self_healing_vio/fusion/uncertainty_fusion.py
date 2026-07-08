"""Uncertainty decomposition utilities for degradation-aware VIO.

SHIELD-VIO treats uncertainty as more than estimator covariance. This module
separates estimator, perceptual, inertial, and epistemic components so future
work can study whether health-aware fusion improves downstream autonomy.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


def _clip01(value: float) -> float:
    return float(max(0.0, min(1.0, value)))


@dataclass(frozen=True)
class UncertaintyBreakdown:
    """Normalized uncertainty components in [0, 1]."""

    estimator: float
    visual: float
    inertial: float
    epistemic: float

    def total(self, weights: Mapping[str, float] | None = None) -> float:
        """Weighted aggregate uncertainty in [0, 1]."""
        weights = dict(weights or {"estimator": 1.0, "visual": 1.0, "inertial": 1.0, "epistemic": 1.0})
        terms = {
            "estimator": _clip01(self.estimator),
            "visual": _clip01(self.visual),
            "inertial": _clip01(self.inertial),
            "epistemic": _clip01(self.epistemic),
        }
        denom = sum(max(v, 0.0) for v in weights.values()) or 1.0
        return _clip01(sum(terms[k] * max(weights.get(k, 0.0), 0.0) for k in terms) / denom)


class UncertaintyFusion:
    """Map health scores and backend residuals to uncertainty components."""

    def estimate(self, health_scores: Mapping[str, float], covariance_trace: float | None = None) -> UncertaintyBreakdown:
        visual = 1.0 - min(
            1.0,
            sum(health_scores.get(k, 1.0) for k in ("image_entropy", "motion_blur", "feature_collapse", "reprojection_error")) / 4.0,
        )
        inertial = 1.0 - _clip01(health_scores.get("imu_consistency", 1.0))
        estimator = _clip01((covariance_trace or 0.0) / 10.0)
        known = {"image_entropy", "motion_blur", "feature_collapse", "reprojection_error", "imu_consistency"}
        epistemic = 0.15 if not set(health_scores).issuperset(known) else 0.05
        return UncertaintyBreakdown(estimator=estimator, visual=visual, inertial=inertial, epistemic=epistemic)
