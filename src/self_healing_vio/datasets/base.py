"""Common dataset abstractions for VIO benchmarking."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class DatasetSequence:
    """Description of one dataset sequence used for benchmarking."""

    name: str
    root: Path
    camera_topic: str
    imu_topic: str
    ground_truth_path: Path | None = None
    notes: str = ""


class DatasetAdapter(Protocol):
    """Protocol implemented by dataset-specific adapters."""

    dataset_name: str

    def discover_sequences(self, root: Path) -> list[DatasetSequence]:
        """Return available sequences under a dataset root."""
        ...
