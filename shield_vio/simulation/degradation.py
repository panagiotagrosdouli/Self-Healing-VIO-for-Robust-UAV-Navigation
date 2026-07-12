"""Deterministic visual and inertial degradation injection.

All injected episodes are explicit and serializable.  This module does not
claim to reproduce every physical sensor failure; it provides controlled,
seeded perturbations for detector and shield experiments.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np


@dataclass(frozen=True)
class DegradationSpec:
    kind: str
    start_s: float
    duration_s: float
    severity: float
    seed: int = 0

    def __post_init__(self) -> None:
        if self.start_s < 0 or self.duration_s <= 0:
            raise ValueError("start_s must be non-negative and duration_s positive")
        if not 0.0 <= self.severity <= 1.0:
            raise ValueError("severity must be in [0, 1]")

    @property
    def end_s(self) -> float:
        return self.start_s + self.duration_s

    def active(self, timestamp_s: float) -> bool:
        return self.start_s <= timestamp_s < self.end_s

    def manifest(self) -> dict[str, Any]:
        return {**asdict(self), "end_s": self.end_s}


def degrade_image(image: np.ndarray, timestamp_s: float, spec: DegradationSpec) -> np.ndarray:
    """Apply one seeded degradation to an image, preserving dtype and shape."""
    if not spec.active(timestamp_s):
        return image.copy()
    rng = np.random.default_rng(spec.seed + int(round(timestamp_s * 1_000_000)))
    x = image.astype(np.float32)
    s = spec.severity
    if spec.kind == "darkness":
        x *= 1.0 - 0.9 * s
    elif spec.kind == "overexposure":
        x = x + (255.0 - x) * 0.9 * s
    elif spec.kind == "noise":
        x += rng.normal(0.0, 45.0 * s, x.shape)
    elif spec.kind == "reduced_contrast":
        mean = np.mean(x, axis=(0, 1), keepdims=True)
        x = mean + (x - mean) * (1.0 - 0.9 * s)
    elif spec.kind == "feature_dropout":
        mask = rng.random(x.shape[:2]) < 0.75 * s
        x[mask] = np.mean(x)
    elif spec.kind == "occlusion":
        h, w = x.shape[:2]
        width = max(1, int(w * 0.7 * s))
        x[:, :width] = 0
    elif spec.kind == "frame_dropout":
        x[...] = 0
    else:
        raise ValueError(f"unsupported visual degradation: {spec.kind}")
    return np.clip(x, 0, 255).astype(image.dtype)


def degrade_imu(
    accel: np.ndarray,
    gyro: np.ndarray,
    timestamp_s: float,
    spec: DegradationSpec,
) -> tuple[np.ndarray, np.ndarray, bool]:
    """Return degraded accelerometer, gyroscope and packet-valid flag."""
    a = np.asarray(accel, dtype=float).copy()
    g = np.asarray(gyro, dtype=float).copy()
    if a.shape != (3,) or g.shape != (3,):
        raise ValueError("accel and gyro must be 3-vectors")
    if not spec.active(timestamp_s):
        return a, g, True
    rng = np.random.default_rng(spec.seed + int(round(timestamp_s * 1_000_000)))
    s = spec.severity
    if spec.kind == "imu_noise":
        a += rng.normal(0.0, 2.0 * s, 3)
        g += rng.normal(0.0, 0.2 * s, 3)
    elif spec.kind == "bias_drift":
        elapsed = timestamp_s - spec.start_s
        a += elapsed * s * np.array([0.3, -0.2, 0.15])
        g += elapsed * s * np.array([0.02, -0.015, 0.01])
    elif spec.kind == "scale_factor":
        a *= 1.0 + 0.25 * s
        g *= 1.0 - 0.20 * s
    elif spec.kind == "saturation":
        a = np.clip(a, -2.0 * (1.0 - 0.8 * s), 2.0 * (1.0 - 0.8 * s))
        g = np.clip(g, -0.5 * (1.0 - 0.8 * s), 0.5 * (1.0 - 0.8 * s))
    elif spec.kind == "axis_failure":
        a[0] *= 1.0 - s
        g[0] *= 1.0 - s
    elif spec.kind == "packet_dropout":
        return a, g, False
    else:
        raise ValueError(f"unsupported IMU degradation: {spec.kind}")
    return a, g, True
