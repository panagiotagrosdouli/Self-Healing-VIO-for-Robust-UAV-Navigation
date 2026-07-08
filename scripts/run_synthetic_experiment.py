"""Run deterministic synthetic SHIELD-VIO experiments."""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
from shield_vio.estimation.state import VIOState
from shield_vio.estimation.eskf import ErrorStateEKF
from shield_vio.frontend.features import visual_quality_score
from shield_vio.imu.model import imu_consistency
from shield_vio.uncertainty.metrics import covariance_report, normalized_risk
from shield_vio.safety.shield import SafetyShield
from shield_vio.visualization.plots import plot_risk_timeline, plot_trajectory
SCENARIOS = {"nominal", "motion_blur", "low_light", "feature_dropout", "imu_bias_drift", "aggressive_motion"}

def run(scenario: str, seed: int, out_dir: Path) -> dict:
    rng = np.random.default_rng(seed); ekf = ErrorStateEKF(); shield = SafetyShield(); state = VIOState(); n = 120; dt = 0.05; time = np.arange(n)*dt; gt=[]; est=[]; risk=[]; vq=[]; active=[]
    for k,t in enumerate(time):
        acc = np.array([0.2*np.sin(t),0,9.81]); gyro=np.array([0,0,0.05])
        if scenario == "imu_bias_drift": acc += np.array([0.03*k/n,0,0]); gyro += np.array([0,0,0.01*k/n])
        if scenario == "aggressive_motion": acc += rng.normal(0,1.5,3); gyro += rng.normal(0,0.7,3)
        state = ekf.propagate(state, acc, gyro, dt); feature_count=170; outlier=0.05
        if scenario == "feature_dropout": feature_count=max(5, int(170*(1-k/n)))
        if scenario == "motion_blur": outlier=min(0.8,0.05+0.7*k/n)
        if scenario == "low_light": feature_count=max(20,int(170-120*k/n)); outlier=0.2
        quality=visual_quality_score(feature_count,8,0.75,outlier); imu_q=imu_consistency(acc, gyro).combined_score; r=normalized_risk(covariance_report(state.covariance,0.08).risk_score, quality, imu_q); decision=shield.decide(r, quality, tracking_ok=feature_count>10)
        gt.append([0.5*t,0.1*np.sin(t),0]); est.append(state.position.copy()); risk.append(r); vq.append(quality); active.append(decision.active)
    out_dir.mkdir(parents=True, exist_ok=True); plot_risk_timeline(time,risk,vq,shield.warning_threshold,out_dir/"risk_timeline.png"); plot_trajectory(np.asarray(est), np.asarray(gt), out_dir/"trajectory.png")
    summary={"scenario":scenario,"seed":seed,"mean_risk":float(np.mean(risk)),"max_risk":float(np.max(risk)),"shield_activations":int(np.sum(active)),"benchmark_status":"synthetic_demo_not_real_benchmark"}; (out_dir/"summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8"); return summary
if __name__ == "__main__":
    p=argparse.ArgumentParser(); p.add_argument("--scenario", default="nominal", choices=sorted(SCENARIOS)); p.add_argument("--seed", type=int, default=7); p.add_argument("--out", default="results/synthetic/nominal"); a=p.parse_args(); print(json.dumps(run(a.scenario,a.seed,Path(a.out)), indent=2))
