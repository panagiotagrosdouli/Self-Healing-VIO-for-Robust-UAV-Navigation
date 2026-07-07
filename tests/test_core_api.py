from self_healing_vio.core import FailureCause, HealthLevel, HealthVector, RecoveryAction
from self_healing_vio.core.metrics import health_level_from_nhi, navigation_health_index


def test_health_vector_clips_scores():
    vector = HealthVector({"good": 1.2, "bad": -0.5, "mid": 0.5})
    assert vector.as_dict() == {"good": 1.0, "bad": 0.0, "mid": 0.5}


def test_navigation_health_index_range():
    nhi = navigation_health_index({"image_entropy": 0.5, "imu_consistency": 1.0})
    assert 0.0 <= nhi <= 100.0


def test_health_level_from_nhi():
    assert health_level_from_nhi(90.0) == HealthLevel.HEALTHY
    assert health_level_from_nhi(50.0) == HealthLevel.WARNING
    assert health_level_from_nhi(10.0) == HealthLevel.CRITICAL


def test_core_enums_are_stable_strings():
    assert FailureCause.CAMERA.value == "camera"
    assert RecoveryAction.REQUEST_HOVER.value == "request_hover"
