"""Evaluate SHIELD-VIO Synthetic Demo outputs and save metrics."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np


def load_xyz(path: Path) -> np.ndarray:
    with path.open(newline="", encoding="utf-8") as f:
        return np.array([[float(r["x"]), float(r["y"]), float(r["z"])] for r in csv.DictReader(f)])


def evaluate(results: Path, out_dir: Path = Path("results/metrics")) -> dict[str, float | str]:
    gt = load_xyz(results / "ground_truth.csv")
    est = load_xyz(results / "estimated_trajectory.csv")
    errors = np.linalg.norm(est - gt, axis=1)
    steps_gt = np.diff(gt, axis=0)
    steps_est = np.diff(est, axis=0)
    rpe = np.linalg.norm(steps_est - steps_gt, axis=1)
    metrics = {
        "label": "Synthetic Demo",
        "ate_rmse_m": float(np.sqrt(np.mean(errors**2))),
        "ate_mean_m": float(np.mean(errors)),
        "rpe_rmse_m": float(np.sqrt(np.mean(rpe**2))),
        "final_error_m": float(errors[-1]),
        "samples": float(len(errors)),
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "summary.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    with (out_dir / "metrics.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(metrics.keys()))
        writer.writeheader()
        writer.writerow(metrics)
    return metrics


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--results", default="results/synthetic_demo")
    p.add_argument("--out", default="results/metrics")
    a = p.parse_args()
    print(json.dumps(evaluate(Path(a.results), Path(a.out)), indent=2))


if __name__ == "__main__":
    main()
