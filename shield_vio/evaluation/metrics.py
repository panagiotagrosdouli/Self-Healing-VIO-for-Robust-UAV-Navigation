"""Evaluation metrics for VIO and failure detection."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np

@dataclass
class DetectionMetrics:
    precision: float
    recall: float
    false_alarm_rate: float
    time_to_detection: float | None

def ate(est: np.ndarray, gt: np.ndarray) -> float:
    est = np.asarray(est, dtype=float); gt = np.asarray(gt, dtype=float)
    if est.shape != gt.shape or est.ndim != 2 or est.shape[1] < 3: raise ValueError("ATE expects matching Nx3+ trajectories")
    return float(np.sqrt(np.mean(np.sum((est[:,:3] - gt[:,:3])**2, axis=1))))

def rpe(est: np.ndarray, gt: np.ndarray, delta: int = 1) -> float:
    est = np.asarray(est, dtype=float); gt = np.asarray(gt, dtype=float)
    if delta <= 0 or len(est) <= delta or est.shape != gt.shape: raise ValueError("Invalid trajectories or delta")
    return float(np.sqrt(np.mean(np.sum(((est[delta:,:3]-est[:-delta,:3]) - (gt[delta:,:3]-gt[:-delta,:3]))**2, axis=1))))

def failure_detection_metrics(pred: np.ndarray, labels: np.ndarray, timestamps: np.ndarray | None = None) -> DetectionMetrics:
    p = np.asarray(pred, dtype=bool); y = np.asarray(labels, dtype=bool); tp = int(np.sum(p & y)); fp = int(np.sum(p & ~y)); fn = int(np.sum(~p & y)); tn = int(np.sum(~p & ~y))
    ttd = None
    if timestamps is not None and np.any(y) and np.any(p & y): ttd = max(0.0, float(np.asarray(timestamps)[np.argmax(p & y)] - np.asarray(timestamps)[np.argmax(y)]))
    return DetectionMetrics(tp/max(tp+fp,1), tp/max(tp+fn,1), fp/max(fp+tn,1), ttd)
