# SHIELD-VIO Synthetic Demo Audit

This audit records the repository transformation focused on a working, reproducible synthetic VIO demonstration. All numbers produced by this pipeline are marked **Synthetic Demo** and must not be interpreted as real-world benchmark evidence.

## Scientific audit

Severity: high. A safety-aware VIO repository needs executable evidence that uncertainty, visual degradation, risk scoring, and shield states are coupled. The new `shield_vio/simulation/synthetic_vio.py` implements a deterministic EKF-like synthetic scenario with ground truth, IMU noise, visual measurements, feature dropout, low-light, motion-blur proxies, covariance growth, NEES/NIS, risk scores, and shield events.

## Engineering audit

Severity: high. The most important gap was the lack of a single command producing metrics, figures, GIF, and MP4. `scripts/run_all.py` now orchestrates simulation, evaluation, figure generation, and demo rendering. `scripts/run_synthetic_demo.py`, `scripts/evaluate_experiment.py`, `scripts/generate_figures.py`, and `scripts/make_demo_gif.py` expose each step separately.

## Reproducibility audit

Severity: high. Synthetic data must be deterministic. The demo uses explicit random seeds, writes CSV/JSON artifacts, and stores all generated output paths under `results/`, `assets/figures/`, `assets/gifs/`, and `assets/videos/`. `configs/default.yaml` documents the default synthetic scenario.

## Visual presentation audit

Severity: medium. The new figure script generates trajectory comparison, covariance trace, risk timeline, visual quality timeline, shield timeline, NEES/NIS consistency, degradation timeline, and simple architecture/pipeline/shield diagrams from code.

## PhD-readiness audit

Severity: medium. The pipeline is a research prototype, not a production VIO system. It is appropriate for demonstrating uncertainty-aware failure monitoring and safety-shield logic, but real EuRoC/TUM-VI/KITTI experiments, calibrated uncertainty, robust visual front-end integration, and closed-loop safety validation remain planned work.

## Commit-ready verification target

```bash
python scripts/run_all.py
pytest -q
```

Expected generated outputs include:

- `results/synthetic_demo/ground_truth.csv`
- `results/synthetic_demo/estimated_trajectory.csv`
- `results/synthetic_demo/uncertainty.csv`
- `results/synthetic_demo/visual_quality.csv`
- `results/synthetic_demo/risk_score.csv`
- `results/synthetic_demo/shield_events.csv`
- `results/metrics/summary.json`
- `results/metrics/metrics.csv`
- `results/figures/*.png`
- `assets/figures/*.png`
- `assets/gifs/demo.gif`
- `assets/videos/demo.mp4` when ffmpeg is available
- `results/videos/shield_vio_demo.gif`
- `results/videos/shield_vio_demo.mp4` when ffmpeg is available
