"""Visual front-end quality metrics."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np

@dataclass
class FeatureTrackStats:
    feature_count: int
    mean_track_age: float
    spatial_coverage: float
    outlier_ratio: float
    visual_quality: float

def spatial_coverage(points: np.ndarray, image_shape: tuple[int, int], grid: tuple[int, int] = (4, 4)) -> float:
    pts = np.asarray(points, dtype=float).reshape((-1, 2)) if len(points) else np.empty((0, 2))
    if pts.size == 0: return 0.0
    h, w = image_shape[:2]; gx, gy = grid
    xs = np.clip((pts[:,0] / max(w,1) * gx).astype(int), 0, gx-1); ys = np.clip((pts[:,1] / max(h,1) * gy).astype(int), 0, gy-1)
    return float(len(set(zip(xs.tolist(), ys.tolist()))) / (gx * gy))

def visual_quality_score(feature_count: int, mean_track_age: float, coverage: float, outlier_ratio: float) -> float:
    count_score = min(max(feature_count, 0) / 180.0, 1.0); age_score = min(max(mean_track_age, 0.0) / 12.0, 1.0); coverage_score = min(max(coverage, 0.0), 1.0); inlier_score = 1.0 - min(max(outlier_ratio, 0.0), 1.0)
    return float(np.clip(0.35*count_score + 0.2*age_score + 0.25*coverage_score + 0.2*inlier_score, 0.0, 1.0))
