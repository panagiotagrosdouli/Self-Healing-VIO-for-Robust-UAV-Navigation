"""Numerical primitives for SHIELD-VIO."""
from __future__ import annotations
import numpy as np
EPS = 1e-12

def skew(v: np.ndarray) -> np.ndarray:
    x, y, z = np.asarray(v, dtype=float).reshape(3)
    return np.array([[0, -z, y], [z, 0, -x], [-y, x, 0]], dtype=float)

def normalize_quaternion(q: np.ndarray) -> np.ndarray:
    q = np.asarray(q, dtype=float).reshape(4)
    n = np.linalg.norm(q)
    if n < EPS:
        raise ValueError("Cannot normalize a near-zero quaternion")
    q = q / n
    return q if q[0] >= 0 else -q

def quat_multiply(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    aw, ax, ay, az = normalize_quaternion(a); bw, bx, by, bz = normalize_quaternion(b)
    return normalize_quaternion(np.array([aw*bw-ax*bx-ay*by-az*bz, aw*bx+ax*bw+ay*bz-az*by, aw*by-ax*bz+ay*bw+az*bx, aw*bz+ax*by-ay*bx+az*bw]))

def small_angle_quat(delta: np.ndarray) -> np.ndarray:
    delta = np.asarray(delta, dtype=float).reshape(3); theta = np.linalg.norm(delta)
    if theta < 1e-10:
        return normalize_quaternion(np.r_[1.0, 0.5 * delta])
    axis = delta / theta
    return normalize_quaternion(np.r_[np.cos(theta / 2.0), axis * np.sin(theta / 2.0)])

def quat_to_rot(q: np.ndarray) -> np.ndarray:
    w, x, y, z = normalize_quaternion(q)
    return np.array([[1-2*(y*y+z*z), 2*(x*y-w*z), 2*(x*z+w*y)], [2*(x*y+w*z), 1-2*(x*x+z*z), 2*(y*z-w*x)], [2*(x*z-w*y), 2*(y*z+w*x), 1-2*(x*x+y*y)]], dtype=float)

def nearest_psd(P: np.ndarray, jitter: float = 1e-9) -> np.ndarray:
    P = 0.5 * (P + P.T); vals, vecs = np.linalg.eigh(P); vals = np.maximum(vals, jitter)
    return vecs @ np.diag(vals) @ vecs.T

def mahalanobis_squared(r: np.ndarray, S: np.ndarray) -> float:
    r = np.asarray(r, dtype=float).reshape(-1); S = nearest_psd(np.asarray(S, dtype=float))
    return float(r.T @ np.linalg.solve(S, r))
