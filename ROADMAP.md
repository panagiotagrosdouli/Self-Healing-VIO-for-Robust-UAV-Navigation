# SHIELD-VIO Roadmap

## Phase 1: Research Skeleton

- Define the formal problem, notation, health vector, diagnosis posterior, and recovery action space.
- Add PhD proposal, V4RL alignment document, and publication-positioning material.
- Keep claims explicitly separated into implemented prototype, planned integration, and research hypotheses.

## Phase 2: Health Monitoring Prototype

- Implement lightweight Python detectors for entropy, blur, feature collapse, IMU consistency, and reprojection error.
- Add Navigation Health Index computation.
- Add Bayesian diagnosis and rule-based recovery baseline.
- Provide a runnable synthetic demo and unit tests.

## Phase 3: VIO Backend Integration

- Select primary backend: OpenVINS, VINS-Fusion, ORB-SLAM3, or Kimera-VIO.
- Implement adapters for feature count, residuals, covariance, timestamps, and backend reset hooks.
- Validate that SHIELD-VIO can run passively without changing estimator behavior.

## Phase 4: ROS2 Real-Time System

- Implement ROS2 health monitor node.
- Publish health vector, NHI, diagnosis posterior, and recovery action topics.
- Add launch files, message definitions, and runtime parameter loading.
- Profile latency and compute usage on onboard hardware.

## Phase 5: Dataset Benchmark

- Build benchmark scripts for EuRoC MAV, TUM-VI, UZH-FPV, Hilti, and Newer College.
- Add controlled degradation: blur, low texture, masking, timestamp offsets, IMU noise, and exposure shifts.
- Compare nominal VIO, monitoring-only VIO, rule-based recovery, and learned recovery.

## Phase 6: PhD/Paper Submission Package

- Finalize ablations and statistical analysis.
- Prepare ICRA/IROS/RA-L paper draft.
- Add reproducibility scripts, result tables, and figure generation.
- Package the repository as a serious doctoral research artifact.
