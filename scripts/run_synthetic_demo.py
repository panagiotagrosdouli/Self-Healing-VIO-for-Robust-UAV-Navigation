"""Run the complete SHIELD-VIO Synthetic Demo simulation."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from shield_vio.simulation.synthetic_vio import SyntheticVIOConfig, run_synthetic_vio


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="results/synthetic_demo")
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--duration", type=float, default=20.0)
    args = parser.parse_args()
    cfg = SyntheticVIOConfig(seed=args.seed, duration_s=args.duration, output_dir=str(Path(args.out)))
    summary = run_synthetic_vio(cfg)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
