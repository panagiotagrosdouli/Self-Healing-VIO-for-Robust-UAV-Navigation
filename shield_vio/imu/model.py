"""IMU noise model and consistency checks."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class IMUNoiseModel:
    accel_noise_density: float = 0.08
    gyro_noise_density: float = 0.004
    accel_bias_random_walk: float = 0.0004
    gyro_bias_random_walk: float = 0.00002
    gravity_norm: float = 9.81

@dataclass
class IMUConsistency:
    accel_score: float
    gyro_score: float
    combined_score: float

def imu_consistency(accel: np.ndarray, gyro: np.ndarray, model: IMUNoiseModel = IMUNoiseModel()) -> IMUConsistency:
    accel_norm_error = abs(float(np.linalg.norm(accel)) - model.gravity_norm); gyro_norm = float(np.linalg.norm(gyro))
    accel_score = float(np.exp(-accel_norm_error / 6.0)); gyro_score = float(np.exp(-max(0.0, gyro_norm - 8.0) / 6.0))
    return IMUConsistency(accel_score, gyro_score, float(0.5 * (accel_score + gyro_score)))
