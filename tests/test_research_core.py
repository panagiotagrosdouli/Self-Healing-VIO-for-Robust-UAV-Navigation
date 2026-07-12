import numpy as np

from shield_vio.domain_shift.detector import RollingShiftDetector, ShiftState
from shield_vio.estimation.error_state_ekf import ErrorStateEKF
from shield_vio.failure_detection.conformal import SplitConformalRisk
from shield_vio.preintegration.imu_preintegrator import IMUPreintegrator


def test_stationary_preintegration_is_zero_without_gravity_in_measurement():
    p = IMUPreintegrator(0.05, 0.005)
    for _ in range(100):
        p.integrate(np.zeros(3), np.zeros(3), 0.01)
    result = p.result()
    assert np.allclose(result.delta_position_m, 0.0)
    assert np.allclose(result.delta_velocity_mps, 0.0)
    assert np.allclose(result.delta_rotation, np.eye(3), atol=1e-10)
    assert np.min(np.linalg.eigvalsh(result.covariance)) >= -1e-12


def test_constant_acceleration_preintegration():
    p = IMUPreintegrator(0.05, 0.005)
    for _ in range(100):
        p.integrate(np.array([1.0, 0.0, 0.0]), np.zeros(3), 0.01)
    result = p.result()
    assert np.allclose(result.delta_velocity_mps, [1.0, 0.0, 0.0], atol=1e-9)
    assert np.allclose(result.delta_position_m, [0.5, 0.0, 0.0], atol=1e-9)


def test_eskf_normalizes_quaternion_and_joseph_update_is_psd():
    ekf = ErrorStateEKF()
    ekf.propagate(np.array([0.0, 0.0, 9.80665]), np.array([0.0, 0.0, 0.1]), 0.01)
    nis = ekf.update_position(np.array([0.1, 0.0, 0.0]), np.eye(3) * 0.01)
    assert nis >= 0.0
    assert np.isclose(np.linalg.norm(ekf.state.quaternion_wxyz), 1.0)
    assert np.min(np.linalg.eigvalsh(ekf.state.covariance)) >= -1e-12


def test_split_conformal_reports_empirical_coverage():
    model = SplitConformalRisk(coverage=0.8).fit(
        np.array([0.1, 0.2, 0.7, 0.8, 0.4]), np.array([0, 0, 1, 1, 0])
    )
    result = model.predict(np.array([0.2, 0.8]))
    assert np.all(result.lower <= result.upper)
    assert 0.0 <= model.empirical_coverage(result, np.array([0, 1])) <= 1.0


def test_shift_detector_escalates_on_sustained_distribution_change():
    detector = RollingShiftDetector({"nis": (3.0, 1.0)}, window=6)
    assessment = None
    for _ in range(6):
        assessment = detector.update({"nis": 9.0})
    assert assessment is not None
    assert assessment.state is ShiftState.SEVERE_SHIFT
    assert assessment.confidence_multiplier < 1.0
