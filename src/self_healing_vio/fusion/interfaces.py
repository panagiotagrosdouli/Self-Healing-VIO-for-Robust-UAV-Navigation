"""Backend-agnostic interfaces for future VIO integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Protocol

import numpy as np


@dataclass
class HealthAwareState:
    """State estimate augmented with health metadata."""

    timestamp: float
    pose: np.ndarray
    covariance: np.ndarray | None
    health_scores: Mapping[str, float]
    nhi: float


class VIOBackendAdapter(Protocol):
    """Protocol implemented by OpenVINS/VINS/ORB-SLAM/Kimera adapters."""

    def get_reprojection_error(self) -> float:
        """Return current mean reprojection error in pixels."""
        ...

    def get_feature_count(self) -> int:
        """Return current number of tracked features."""
        ...

    def apply_recovery_action(self, action: str) -> None:
        """Apply a backend-specific recovery action."""
        ...
