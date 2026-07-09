"""Regression tests for the SHIELD-VIO Synthetic Demo pipeline."""
from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

from shield_vio.simulation.synthetic_vio import (
    SyntheticVIOConfig,
    compute_risk,
    run_synthetic_vio,
    shield_state,
    visual_quality,
)
from scripts.evaluate_experiment import evaluate
from scripts.generate_figures import generate_figures


def test_synthetic_vio_outputs_required_csvs(tmp_path: Path) -> None:
    out = tmp_path / "synthetic"
    summary = run_synthetic_vio(SyntheticVIOConfig(output_dir=str(out), duration_s=4.0, seed=3))
    assert summary["label"] == "Synthetic Demo"
    for name in [
        "ground_truth.csv",
        "estimated_trajectory.csv",
        "uncertainty.csv",
        "visual_quality.csv",
        "risk_score.csv",
        "shield_events.csv",
        "summary.json",
    ]:
        assert (out / name).exists()
    with (out / "uncertainty.csv").open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert rows
    assert all(float(r["min_eig"]) > -1e-8 for r in rows)


def test_risk_score_is_normalized() -> None:
    q = visual_quality(feature_count=50, outlier_rate=0.4, blur=0.7, light=0.5)
    risk = compute_risk(trace=1.0, nis=3.0, vq=q, severity=0.8)
    assert 0.0 <= q <= 1.0
    assert 0.0 <= risk <= 1.0


def test_shield_activation_rules() -> None:
    cfg = SyntheticVIOConfig()
    assert shield_state(0.1, 0.9, 120, cfg) == "NORMAL"
    assert shield_state(0.9, 0.9, 120, cfg) == "HALT"
    assert shield_state(0.2, 0.1, 120, cfg) == "RELOCALIZE_REQUESTED"


def test_evaluation_metrics_and_figures_smoke(tmp_path: Path) -> None:
    out = tmp_path / "synthetic"
    run_synthetic_vio(SyntheticVIOConfig(output_dir=str(out), duration_s=4.0, seed=4))
    metrics = evaluate(out, tmp_path / "metrics")
    assert metrics["label"] == "Synthetic Demo"
    assert np.isfinite(metrics["ate_rmse_m"])
    figures = generate_figures(out, tmp_path / "assets" / "figures", tmp_path / "results" / "figures")
    assert figures
    assert all(p.exists() for p in figures)
