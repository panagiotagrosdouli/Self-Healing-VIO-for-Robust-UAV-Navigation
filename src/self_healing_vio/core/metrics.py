"""Metric utilities for SHIELD-VIO."""

from __future__ import annotations

from typing import Mapping

import numpy as np

from .state import HealthVector
from .types import HealthLevel


def clip_unit(value: float) -> float:
    """Clip a numeric value to [0, 1]."""

    return float(np.clip(value, 0.0, 1.0))


def clip_nhi(value: float) -> float:
    """Clip a Navigation Health Index value to [0, 100]."""

    return float(np.clip(value, 0.0, 100.0))


def weighted_health_score(scores: HealthVector | Mapping[str, float], weights: Mapping[str, float] | None = None) -> float:
    """Compute a normalized weighted health score in [0, 1]."""

    score_map = scores.as_dict() if isinstance(scores, HealthVector) else {str(k): clip_unit(float(v)) for k, v in scores.items()}
    if not score_map:
        raise ValueError("at least one health score is required")
    weight_map = weights or {name: 1.0 for name in score_map}
    total_weight = sum(max(float(weight_map.get(name, 0.0)), 0.0) for name in score_map)
    if total_weight <= 0.0:
        raise ValueError("at least one positive weight is required")
    fused = sum(max(float(weight_map.get(name, 0.0)), 0.0) * score for name, score in score_map.items())
    return clip_unit(fused / total_weight)


def navigation_health_index(
    scores: HealthVector | Mapping[str, float],
    weights: Mapping[str, float] | None = None,
    risk: float = 0.0,
    risk_penalty: float = 0.0,
) -> float:
    """Compute the SHIELD-VIO Navigation Health Index in [0, 100]."""

    fused = weighted_health_score(scores, weights)
    penalized = fused - max(float(risk_penalty), 0.0) * clip_unit(float(risk))
    return clip_nhi(100.0 * penalized)


def health_level_from_nhi(nhi: float, warning_threshold: float = 70.0, critical_threshold: float = 35.0) -> HealthLevel:
    """Map NHI to a discrete health level."""

    value = clip_nhi(nhi)
    if value >= warning_threshold:
        return HealthLevel.HEALTHY
    if value >= critical_threshold:
        return HealthLevel.WARNING
    return HealthLevel.CRITICAL
