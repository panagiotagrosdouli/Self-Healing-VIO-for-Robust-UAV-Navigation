"""Configuration skeleton for future ROS2 health monitor nodes."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HealthMonitorNodeConfig:
    """Runtime configuration for a planned ROS2 health monitor node."""

    image_topic: str = "/camera/image_raw"
    imu_topic: str = "/imu/data"
    health_topic: str = "/shield_vio/health"
    diagnosis_topic: str = "/shield_vio/diagnosis"
    recovery_topic: str = "/shield_vio/recovery_action"
    publish_rate_hz: float = 30.0
