import numpy as np
from pathlib import Path
from shield_vio.core.math import normalize_quaternion
from shield_vio.estimation.state import VIOState, STATE_DIM
from shield_vio.estimation.eskf import ErrorStateEKF
from shield_vio.frontend.features import visual_quality_score
from shield_vio.uncertainty.metrics import nees, nis, covariance_report, normalized_risk
from shield_vio.safety.shield import SafetyShield, ShieldAction
from shield_vio.evaluation.metrics import ate, rpe

def test_quaternion_normalization():
    q = normalize_quaternion(np.array([2.,0,0,0])); assert np.isclose(np.linalg.norm(q), 1.0)

def test_imu_propagation_and_psd():
    s = ErrorStateEKF().propagate(VIOState(), np.array([0,0,9.81]), np.zeros(3), 0.01)
    assert s.covariance.shape == (STATE_DIM, STATE_DIM)
    assert np.min(np.linalg.eigvalsh(s.covariance)) > 0

def test_visual_update_dimensions():
    H = np.zeros((2, STATE_DIM)); R = np.eye(2)*0.1
    s = ErrorStateEKF().update_linear(VIOState(), np.zeros(2), H, R)
    assert s.covariance.shape == (STATE_DIM, STATE_DIM)

def test_quality_risk_nees_nis_shield_metrics():
    q = visual_quality_score(100,5,0.5,0.1); assert 0 <= q <= 1
    P = np.eye(3); assert nees(np.ones(3), P) == 3.0; assert nis(np.ones(3), P) == 3.0
    r = normalized_risk(covariance_report(np.eye(15)*0.01).risk_score, q, 1.0); assert 0 <= r <= 1
    assert SafetyShield().decide(0.8,0.8).action == ShieldAction.HOVER_OR_HALT
    traj = np.zeros((4,3)); assert ate(traj, traj) == 0.0 and rpe(traj, traj) == 0.0

def test_gif_script_smoke():
    assert Path("scripts/make_demo_gif.py").exists()
