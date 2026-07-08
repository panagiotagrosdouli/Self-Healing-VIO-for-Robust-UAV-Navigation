"""Uncertainty and estimator-consistency metrics."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from shield_vio.core.math import nearest_psd, mahalanobis_squared

@dataclass
class UncertaintyReport:
    covariance_trace: float
    log_determinant: float
    entropy_proxy: float
    condition_number: float
    risk_score: float

def nees(error: np.ndarray, covariance: np.ndarray) -> float:
    return mahalanobis_squared(error, covariance)

def nis(innovation: np.ndarray, innovation_covariance: np.ndarray) -> float:
    return mahalanobis_squared(innovation, innovation_covariance)

def covariance_report(P: np.ndarray, reference_trace: float = 1.0, max_condition: float = 1e8) -> UncertaintyReport:
    P = nearest_psd(np.asarray(P, dtype=float)); sign, logdet = np.linalg.slogdet(P); trace = float(np.trace(P)); cond = float(np.linalg.cond(P)); logdet = float(logdet if sign > 0 else np.inf)
    trace_risk = trace / (trace + max(reference_trace, 1e-12)); cond_risk = min(cond / max_condition, 1.0); risk = float(np.clip(0.7*trace_risk + 0.3*cond_risk, 0.0, 1.0))
    return UncertaintyReport(trace, logdet, float(0.5 * logdet), cond, risk)

def normalized_risk(uncertainty_risk: float, visual_quality: float, imu_quality: float, nis_value: float | None = None, nis_dof: int | None = None) -> float:
    penalty = 0.0
    if nis_value is not None and nis_dof: penalty = min(max(nis_value / (3.0 * nis_dof) - 1.0, 0.0), 1.0)
    return float(np.clip(0.45*uncertainty_risk + 0.30*(1-visual_quality) + 0.15*(1-imu_quality) + 0.10*penalty, 0.0, 1.0))
