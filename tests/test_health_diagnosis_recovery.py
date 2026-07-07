from self_healing_vio.diagnosis import BayesianFailureDiagnosis
from self_healing_vio.health import NavigationHealthIndex
from self_healing_vio.recovery import RuleBasedRecoveryPolicy


def test_nhi_range_0_to_100():
    nhi = NavigationHealthIndex().compute({"a": 1.0, "b": 0.0, "c": 0.5})
    assert 0.0 <= nhi <= 100.0


def test_diagnosis_probabilities_sum_to_one():
    posterior = BayesianFailureDiagnosis().infer({
        "image_entropy": 0.4,
        "motion_blur": 0.2,
        "feature_collapse": 0.6,
        "imu_consistency": 0.9,
        "reprojection_error": 0.8,
    })
    assert abs(sum(posterior.values()) - 1.0) < 1e-9
    assert all(0.0 <= value <= 1.0 for value in posterior.values())


def test_recovery_policy_returns_valid_action():
    policy = RuleBasedRecoveryPolicy()
    posterior = BayesianFailureDiagnosis().infer({"motion_blur": 0.1, "image_entropy": 0.4})
    action = policy.select_action({"motion_blur": 0.1, "image_entropy": 0.4}, posterior, nhi=40.0)
    assert action.value in policy.valid_actions
