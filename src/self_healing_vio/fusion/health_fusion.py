"""Minimal health-vector fusion utilities for SHIELD-VIO.

The fusion layer converts heterogeneous detector outputs into a stable health
score dictionary that can be consumed by diagnosis, NHI computation, recovery
policies, and future ROS2 messages. It intentionally remains lightweight in the
prototype stage.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from self_healing_vio.detection import DetectorResult


@dataclass
class HealthFusion:
    """Convert detector outputs into a normalized health-score dictionary."""

    def fuse(self, results: Iterable[DetectorResult]) -> dict[str, float]:
        """Return `{detector_name: score}` for diagnosis and health indexing."""
        return {result.name: result.score for result in results}
