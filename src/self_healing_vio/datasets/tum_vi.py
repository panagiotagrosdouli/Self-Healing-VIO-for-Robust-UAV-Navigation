"""TUM-VI dataset adapter skeleton."""

from __future__ import annotations

from pathlib import Path

from .base import DatasetSequence


class TumViAdapter:
    """Discover TUM-VI sequences for future benchmark experiments."""

    dataset_name = "TUM-VI"

    def discover_sequences(self, root: Path) -> list[DatasetSequence]:
        sequences: list[DatasetSequence] = []
        for candidate in sorted(root.glob("*")):
            if candidate.is_dir():
                sequences.append(
                    DatasetSequence(
                        name=candidate.name,
                        root=candidate,
                        camera_topic="/cam0/image_raw",
                        imu_topic="/imu0",
                        notes="TUM-VI adapter skeleton; calibration parsing is planned.",
                    )
                )
        return sequences
