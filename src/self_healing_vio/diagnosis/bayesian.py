"""Interpretable Bayesian failure diagnosis baseline."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

import numpy as np


DEFAULT_CAUSES = ("nominal", "camera", "environment", "motion", "sensor", "algorithm")


@dataclass
class BayesianFailureDiagnosis:
    """Maps normalized health scores to a posterior over failure causes.

    This model is deliberately simple and inspectable. It uses manually specified
    detector likelihood sensitivities as an initial research baseline.
    """

    priors: Mapping[str, float] = field(default_factory=lambda: {
        "nominal": 0.45,
        "camera": 0.12,
        "environment": 0.13,
        "motion": 0.12,
        "sensor": 0.10,
        "algorithm": 0.08,
    })
    sensitivities: Mapping[str, Mapping[str, float]] = field(default_factory=lambda: {
        "camera": {"image_entropy": 0.7, "motion_blur": 0.9, "feature_collapse": 0.4},
        "environment": {"image_entropy": 0.8, "feature_collapse": 0.9},
        "motion": {"motion_blur": 0.8, "imu_consistency": 0.4, "reprojection_error": 0.5},
        "sensor": {"imu_consistency": 1.0},
        "algorithm": {"reprojection_error": 1.0, "feature_collapse": 0.3},
        "nominal": {},
    })

    def infer(self, health_scores: Mapping[str, float]) -> dict[str, float]:
        if not health_scores:
            raise ValueError("health_scores must not be empty")

        log_probs: dict[str, float] = {}
        for cause, prior in self.priors.items():
            log_p = float(np.log(max(prior, 1e-12)))
            if cause == "nominal":
                degradation = np.mean([1.0 - float(np.clip(v, 0.0, 1.0)) for v in health_scores.values()])
                log_p += float(np.log(max(1.0 - degradation, 1e-6)))
            else:
                cause_sens = self.sensitivities.get(cause, {})
                evidence = 0.0
                for signal, score in health_scores.items():
                    sensitivity = cause_sens.get(signal, 0.05)
                    evidence += sensitivity * (1.0 - float(np.clip(score, 0.0, 1.0)))
                log_p += evidence
            log_probs[cause] = log_p

        max_log = max(log_probs.values())
        probs = {cause: float(np.exp(value - max_log)) for cause, value in log_probs.items()}
        norm = sum(probs.values())
        return {cause: value / norm for cause, value in probs.items()}
