"""Deterministic synthetic SHIELD-VIO scenario generator.

This module is a scientifically honest synthetic demo, not a real-world VIO benchmark.
It simulates a planar robot, noisy IMU/visual measurements, visual degradation, EKF-like
fusion, uncertainty growth, normalized risk, and shield events.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import csv
import json
import math
from typing import Iterable

import numpy as np

SHIELD_STATES = ("NORMAL", "WARNING", "SLOW_DOWN", "HALT", "RELOCALIZE_REQUESTED")


@dataclass(frozen=True)
class DegradationEvent:
    """Synthetic visual degradation event."""

    name: str
    start: float
    end: float
    severity: float

    def active(self, t: float) -> bool:
        return self.start <= t <= self.end


@dataclass
class SyntheticVIOConfig:
    """Configuration for the synthetic SHIELD-VIO demo."""

    seed: int = 7
    duration_s: float = 20.0
    dt: float = 0.05
    visual_dt: float = 0.2
    imu_accel_noise: float = 0.055
    visual_noise: float = 0.055
    bias_walk: float = 0.0015
    output_dir: str = "results/synthetic_demo"
    risk_threshold_warning: float = 0.45
    risk_threshold_slow: float = 0.62
    risk_threshold_halt: float = 0.82
    visual_quality_threshold: float = 0.35
    events: list[DegradationEvent] = field(
        default_factory=lambda: [
            DegradationEvent("feature dropout", 6.0, 9.0, 0.70),
            DegradationEvent("low-light", 10.0, 13.0, 0.65),
            DegradationEvent("motion blur", 14.0, 17.0, 0.85),
        ]
    )


def default_config() -> SyntheticVIOConfig:
    return SyntheticVIOConfig()


def ground_truth_state(t: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return planar position, velocity, and acceleration for the synthetic robot."""
    pos = np.array([0.22 * t, 1.15 * math.sin(0.28 * t), 0.18 * math.sin(0.55 * t)])
    vel = np.array([0.22, 1.15 * 0.28 * math.cos(0.28 * t), 0.18 * 0.55 * math.cos(0.55 * t)])
    acc = np.array([0.0, -1.15 * 0.28**2 * math.sin(0.28 * t), -0.18 * 0.55**2 * math.sin(0.55 * t)])
    return pos, vel, acc


def active_degradation(events: Iterable[DegradationEvent], t: float) -> tuple[str, float]:
    names = [e.name for e in events if e.active(t)]
    severity = max((e.severity for e in events if e.active(t)), default=0.0)
    return "+".join(names) if names else "nominal", severity


def visual_quality(feature_count: int, outlier_rate: float, blur: float, light: float) -> float:
    feature_term = min(1.0, feature_count / 140.0)
    score = 0.48 * feature_term + 0.24 * (1.0 - outlier_rate) + 0.16 * (1.0 - blur) + 0.12 * light
    return float(np.clip(score, 0.0, 1.0))


def covariance_metrics(P: np.ndarray) -> tuple[float, float, float]:
    eps = 1e-9
    trace = float(np.trace(P))
    sign, logdet = np.linalg.slogdet(P + np.eye(P.shape[0]) * eps)
    entropy_proxy = float(0.5 * max(logdet, -80.0)) if sign > 0 else 0.0
    return trace, float(logdet), entropy_proxy


def compute_risk(trace: float, nis: float, vq: float, severity: float) -> float:
    cov_risk = 1.0 - math.exp(-trace / 2.3)
    nis_risk = 1.0 - math.exp(-max(nis, 0.0) / 10.0)
    risk = 0.42 * cov_risk + 0.25 * (1.0 - vq) + 0.18 * severity + 0.15 * nis_risk
    return float(np.clip(risk, 0.0, 1.0))


def shield_state(risk: float, vq: float, feature_count: int, cfg: SyntheticVIOConfig) -> str:
    if feature_count < 12 or vq < 0.18:
        return "RELOCALIZE_REQUESTED"
    if risk >= cfg.risk_threshold_halt:
        return "HALT"
    if risk >= cfg.risk_threshold_slow:
        return "SLOW_DOWN"
    if risk >= cfg.risk_threshold_warning or vq < cfg.visual_quality_threshold:
        return "WARNING"
    return "NORMAL"


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def run_synthetic_vio(config: SyntheticVIOConfig | None = None) -> dict[str, object]:
    """Run the full deterministic synthetic VIO demo and write CSV/JSON outputs."""
    cfg = config or default_config()
    rng = np.random.default_rng(cfg.seed)
    out = Path(cfg.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    n = int(round(cfg.duration_s / cfg.dt)) + 1
    times = np.linspace(0.0, cfg.duration_s, n)
    x = np.zeros(6)  # p_xyz, v_xyz
    P = np.eye(6) * 0.035
    bias = np.zeros(3)
    Q_base = np.diag([0.002, 0.002, 0.002, 0.018, 0.018, 0.018])
    R_base = np.eye(3) * cfg.visual_noise**2

    gt_rows: list[dict[str, object]] = []
    est_rows: list[dict[str, object]] = []
    unc_rows: list[dict[str, object]] = []
    vq_rows: list[dict[str, object]] = []
    risk_rows: list[dict[str, object]] = []
    shield_rows: list[dict[str, object]] = []
    prev_state = "NORMAL"
    visual_counter = 0.0
    nis = 0.0

    for t in times:
        p_gt, v_gt, a_gt = ground_truth_state(float(t))
        event_name, severity = active_degradation(cfg.events, float(t))
        bias += rng.normal(0.0, cfg.bias_walk * math.sqrt(cfg.dt), 3)
        imu_acc = a_gt + bias + rng.normal(0.0, cfg.imu_accel_noise * (1.0 + 1.4 * severity), 3)

        F = np.eye(6)
        F[:3, 3:] = np.eye(3) * cfg.dt
        B = np.vstack([0.5 * cfg.dt**2 * np.eye(3), cfg.dt * np.eye(3)])
        x = F @ x + B @ imu_acc
        P = F @ P @ F.T + Q_base * (1.0 + 4.0 * severity) * cfg.dt

        visual_counter += cfg.dt
        feature_count = int(max(4, round(155 * (1.0 - 0.82 * severity) + rng.normal(0, 8))))
        outlier_rate = float(np.clip(0.04 + 0.55 * severity + rng.normal(0, 0.025), 0.0, 0.95))
        blur = float(np.clip(0.1 + (0.75 * severity if "motion blur" in event_name else 0.2 * severity), 0.0, 1.0))
        light = float(np.clip(1.0 - (0.82 * severity if "low-light" in event_name else 0.12 * severity), 0.05, 1.0))
        vq = visual_quality(feature_count, outlier_rate, blur, light)

        if visual_counter >= cfg.visual_dt and feature_count >= 8:
            visual_counter = 0.0
            R = R_base * (1.0 + 14.0 * (1.0 - vq) + 4.0 * severity)
            z = p_gt + rng.normal(0.0, math.sqrt(R[0, 0]), 3)
            H = np.hstack([np.eye(3), np.zeros((3, 3))])
            innov = z - H @ x
            S = H @ P @ H.T + R
            K = P @ H.T @ np.linalg.inv(S)
            x = x + K @ innov
            P = (np.eye(6) - K @ H) @ P @ (np.eye(6) - K @ H).T + K @ R @ K.T
            nis = float(innov.T @ np.linalg.inv(S) @ innov)
        else:
            nis = float(nis * 0.95 + severity * 8.0)

        P = 0.5 * (P + P.T)
        min_eig = float(np.min(np.linalg.eigvalsh(P)))
        if min_eig < 1e-9:
            P += np.eye(6) * (1e-9 - min_eig)

        trace, logdet, entropy = covariance_metrics(P)
        err = x[:3] - p_gt
        nees = float(err.T @ np.linalg.inv(P[:3, :3] + np.eye(3) * 1e-9) @ err)
        risk = compute_risk(trace, nis, vq, severity)
        state = shield_state(risk, vq, feature_count, cfg)
        changed = state != prev_state
        prev_state = state

        gt_rows.append({"t": t, "x": p_gt[0], "y": p_gt[1], "z": p_gt[2], "vx": v_gt[0], "vy": v_gt[1], "vz": v_gt[2]})
        est_rows.append({"t": t, "x": x[0], "y": x[1], "z": x[2], "vx": x[3], "vy": x[4], "vz": x[5]})
        unc_rows.append({"t": t, "trace": trace, "logdet": logdet, "entropy_proxy": entropy, "nees": nees, "nis": nis, "min_eig": min_eig})
        vq_rows.append({"t": t, "visual_quality": vq, "feature_count": feature_count, "outlier_rate": outlier_rate, "blur_proxy": blur, "light_proxy": light, "event": event_name})
        risk_rows.append({"t": t, "risk_score": risk, "event_severity": severity, "event": event_name})
        shield_rows.append({"t": t, "state": state, "active": state != "NORMAL", "transition": changed, "event": event_name})

    _write_csv(out / "ground_truth.csv", gt_rows)
    _write_csv(out / "estimated_trajectory.csv", est_rows)
    _write_csv(out / "uncertainty.csv", unc_rows)
    _write_csv(out / "visual_quality.csv", vq_rows)
    _write_csv(out / "risk_score.csv", risk_rows)
    _write_csv(out / "shield_events.csv", shield_rows)

    gt = np.array([[r["x"], r["y"], r["z"]] for r in gt_rows], dtype=float)
    est = np.array([[r["x"], r["y"], r["z"]] for r in est_rows], dtype=float)
    ate = float(np.sqrt(np.mean(np.sum((est - gt) ** 2, axis=1))))
    final_error = float(np.linalg.norm(est[-1] - gt[-1]))
    event_mask = np.array([r["event"] != "nominal" for r in risk_rows])
    active_mask = np.array([r["active"] for r in shield_rows])
    tp = int(np.sum(event_mask & active_mask)); fp = int(np.sum(~event_mask & active_mask)); fn = int(np.sum(event_mask & ~active_mask))
    precision = float(tp / (tp + fp)) if tp + fp else 0.0
    recall = float(tp / (tp + fn)) if tp + fn else 0.0
    summary = {
        "label": "Synthetic Demo",
        "seed": cfg.seed,
        "duration_s": cfg.duration_s,
        "samples": n,
        "ate_rmse_m": ate,
        "final_position_error_m": final_error,
        "max_risk": float(max(r["risk_score"] for r in risk_rows)),
        "mean_visual_quality": float(np.mean([r["visual_quality"] for r in vq_rows])),
        "shield_activation_rate": float(np.mean(active_mask)),
        "failure_detection_precision": precision,
        "failure_detection_recall": recall,
        "status_counts": {s: int(sum(r["state"] == s for r in shield_rows)) for s in SHIELD_STATES},
        "disclaimer": "Synthetic Demo only; not a real-world benchmark or state-of-the-art claim.",
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(run_synthetic_vio(), indent=2))
