"""State containers for error-state VIO."""
from __future__ import annotations
from dataclasses import dataclass, field
import numpy as np
from shield_vio.core.math import normalize_quaternion
STATE_DIM = 15

@dataclass
class VIOState:
    position: np.ndarray = field(default_factory=lambda: np.zeros(3))
    velocity: np.ndarray = field(default_factory=lambda: np.zeros(3))
    orientation: np.ndarray = field(default_factory=lambda: np.array([1.0, 0.0, 0.0, 0.0]))
    accel_bias: np.ndarray = field(default_factory=lambda: np.zeros(3))
    gyro_bias: np.ndarray = field(default_factory=lambda: np.zeros(3))
    covariance: np.ndarray = field(default_factory=lambda: np.eye(STATE_DIM) * 1e-3)
    def normalize(self) -> None:
        self.orientation = normalize_quaternion(self.orientation)
    def copy(self) -> "VIOState":
        return VIOState(*(np.copy(x) for x in (self.position, self.velocity, self.orientation, self.accel_bias, self.gyro_bias, self.covariance)))
