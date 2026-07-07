"""ROS2-facing dataclasses used before custom message definitions exist.

These classes are not a replacement for `.msg` definitions. They document the
planned payloads for the future ROS2 bridge while keeping the current Python
prototype executable without ROS2 installed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class HealthMonitorMessage:
    """Prototype payload for a health-monitor publication."""

    stamp: float
    health_scores: Mapping[str, float]
    diagnosis: Mapping[str, float]
    nhi: float


@dataclass(frozen=True)
class RecoveryCommand:
    """Prototype payload for a recovery command publication."""

    stamp: float
    action: str
    reason: str = ""
