"""Risk-aware safety shield."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

class ShieldAction(str, Enum):
    NOMINAL = "nominal"
    LOW_CONFIDENCE = "low_confidence_mode"
    SLOW_DOWN = "slow_down"
    HOVER_OR_HALT = "hover_or_halt"
    REQUEST_RELOCALIZATION = "request_relocalization"

@dataclass
class ShieldDecision:
    active: bool
    action: ShieldAction
    reason: str
    speed_scale: float

@dataclass
class SafetyShield:
    warning_threshold: float = 0.45
    critical_threshold: float = 0.70
    min_visual_quality: float = 0.25
    def decide(self, risk: float, visual_quality: float, tracking_ok: bool = True) -> ShieldDecision:
        if not tracking_ok or visual_quality < self.min_visual_quality: return ShieldDecision(True, ShieldAction.REQUEST_RELOCALIZATION, "tracking failure or severe visual degradation", 0.0)
        if risk >= self.critical_threshold: return ShieldDecision(True, ShieldAction.HOVER_OR_HALT, "critical estimator risk", 0.0)
        if risk >= self.warning_threshold: return ShieldDecision(True, ShieldAction.SLOW_DOWN, "elevated estimator risk", 0.35)
        if risk >= 0.8 * self.warning_threshold: return ShieldDecision(True, ShieldAction.LOW_CONFIDENCE, "approaching risk threshold", 0.7)
        return ShieldDecision(False, ShieldAction.NOMINAL, "risk below threshold", 1.0)
