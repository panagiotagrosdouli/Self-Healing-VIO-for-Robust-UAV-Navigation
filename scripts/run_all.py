"""Run the full SHIELD-VIO Synthetic Demo pipeline end to end."""
from __future__ import annotations

import json
from pathlib import Path

from scripts.evaluate_experiment import evaluate
from scripts.generate_figures import generate_figures
from scripts.make_demo_gif import render_demo
from shield_vio.simulation.synthetic_vio import SyntheticVIOConfig, run_synthetic_vio


def main() -> None:
    results = Path("results/synthetic_demo")
    summary = run_synthetic_vio(SyntheticVIOConfig(output_dir=str(results)))
    metrics = evaluate(results)
    figures = generate_figures(results)
    videos = render_demo(results)
    report = {
        "label": "Synthetic Demo",
        "simulation": summary,
        "metrics": metrics,
        "figures": [str(p) for p in figures],
        "videos": videos,
        "disclaimer": "Synthetic Demo only; not a real-world benchmark.",
    }
    Path("results").mkdir(exist_ok=True)
    Path("results/run_all_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
