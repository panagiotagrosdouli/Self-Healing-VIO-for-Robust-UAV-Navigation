"""Deterministic fault injectors for synthetic degradation studies."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


def _clip_uint8(image: np.ndarray) -> np.ndarray:
    return np.clip(image, 0, 255).astype(np.uint8)


@dataclass(frozen=True)
class MotionBlurInjection:
    """Apply a simple horizontal box blur to approximate motion blur."""

    kernel_size: int = 7

    def apply(self, image: np.ndarray) -> np.ndarray:
        kernel = max(1, int(self.kernel_size))
        padded = np.pad(image.astype(float), ((0, 0), (kernel // 2, kernel // 2)), mode="edge")
        out = np.zeros_like(image, dtype=float)
        for offset in range(kernel):
            out += padded[:, offset : offset + image.shape[1]]
        return _clip_uint8(out / kernel)


@dataclass(frozen=True)
class LowTextureInjection:
    """Blend an image toward its mean intensity to remove texture."""

    severity: float = 0.7

    def apply(self, image: np.ndarray) -> np.ndarray:
        alpha = float(np.clip(self.severity, 0.0, 1.0))
        mean = np.mean(image)
        return _clip_uint8((1.0 - alpha) * image.astype(float) + alpha * mean)


@dataclass(frozen=True)
class FeatureDropout:
    """Reduce a feature count by a fixed dropout probability."""

    dropout_probability: float = 0.5

    def apply(self, feature_count: int) -> int:
        keep = 1.0 - float(np.clip(self.dropout_probability, 0.0, 1.0))
        return max(0, int(round(feature_count * keep)))


@dataclass(frozen=True)
class ImuBiasInjection:
    """Add a deterministic bias vector to an IMU residual vector."""

    bias: tuple[float, float, float] = (0.05, 0.05, 0.05)

    def apply(self, residual: np.ndarray) -> np.ndarray:
        return np.asarray(residual, dtype=float) + np.asarray(self.bias, dtype=float)
