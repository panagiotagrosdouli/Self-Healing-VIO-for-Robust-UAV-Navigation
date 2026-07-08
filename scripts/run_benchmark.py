#!/usr/bin/env python3
"""Benchmark entry point skeleton for SHIELD-VIO.

This script intentionally does not claim completed dataset evaluation. It defines
the command-line surface for future dataset replay, failure injection, VIO backend
execution, and health-aware metric aggregation.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from self_healing_vio.datasets import EuRoCAdapter, HiltiAdapter, TumViAdapter, UzhFpvAdapter


ADAPTERS = {
    "euroc": EuRoCAdapter,
    "tum_vi": TumViAdapter,
    "hilti": HiltiAdapter,
    "uzh_fpv": UzhFpvAdapter,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="SHIELD-VIO benchmark skeleton")
    parser.add_argument("--dataset", choices=sorted(ADAPTERS), required=True)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--inject-failure", default="none", choices=["none", "blur", "low_texture", "imu_bias", "feature_dropout"])
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    adapter = ADAPTERS[args.dataset]()
    sequences = adapter.discover_sequences(args.root)
    print(f"dataset={adapter.dataset_name}")
    print(f"root={args.root}")
    print(f"failure_injection={args.inject_failure}")
    print(f"num_sequences={len(sequences)}")
    for sequence in sequences:
        print(f"- {sequence.name}: camera={sequence.camera_topic}, imu={sequence.imu_topic}")
    print("Benchmark execution is planned; this command currently validates dataset discovery only.")


if __name__ == "__main__":
    main()
