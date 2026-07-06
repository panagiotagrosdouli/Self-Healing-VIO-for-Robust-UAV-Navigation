from dataclasses import dataclass

from self_healing_vio.health import VioHealthEstimate


@dataclass
class RecoveryDecision:
    action: str
    priority: int
    reason: str


class RecoveryPolicy:
    def decide(self, health: VioHealthEstimate) -> RecoveryDecision:
        if health.level == 'critical':
            return RecoveryDecision(
                action='trigger_relocalization',
                priority=3,
                reason='critical VIO health requires immediate recovery',
            )
        if health.level == 'warning':
            return RecoveryDecision(
                action='increase_inertial_weight',
                priority=2,
                reason='visual tracking is degraded; rely more on inertial information',
            )
        return RecoveryDecision(
            action='continue_nominal_tracking',
            priority=1,
            reason='VIO health is stable',
        )
