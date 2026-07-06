from self_healing_vio.controller import SelfHealingVioController
from self_healing_vio.health import VioHealthSignals


def test_controller_outputs_nominal_decision_for_good_signals():
    output = SelfHealingVioController().step(
        VioHealthSignals(
            tracking_ok=True,
            tracked_features=180,
            mean_reprojection_error=1.0,
            image_brightness=0.9,
            blur_score=0.9,
            imu_consistency=0.9,
        )
    )
    assert output.health_level == 'healthy'
    assert output.recovery_decision.action == 'continue_nominal_tracking'


def test_controller_outputs_recovery_for_bad_signals():
    output = SelfHealingVioController().step(
        VioHealthSignals(
            tracking_ok=False,
            tracked_features=3,
            mean_reprojection_error=12.0,
            image_brightness=0.1,
            blur_score=0.1,
            imu_consistency=0.1,
        )
    )
    assert output.health_level == 'critical'
    assert output.recovery_decision.action == 'trigger_relocalization'
