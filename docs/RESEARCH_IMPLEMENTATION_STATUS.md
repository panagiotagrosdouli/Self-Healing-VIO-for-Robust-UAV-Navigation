# SHIELD-VIO research implementation status

## Implemented in `feature/phd-shield-vio`

- Typed and validated core records with SI-unit field names, frame identifiers, covariance validation, quaternion normalization, and deterministic dictionary serialization.
- OpenCV Shi–Tomasi/Lucas–Kanade feature tracking with persistent IDs, forward–backward rejection, replenishment, exclusion-mask balancing, track age, survival rate, outlier ratio, blur variance, and brightness.
- Bias-aware IMU preintegration research prototype for delta position, velocity, rotation, covariance, and first-order bias Jacobians.
- Fifteen-dimensional error-state EKF research prototype for position, velocity, attitude, accelerometer bias, and gyroscope bias, including Joseph-form position update, quaternion normalization, covariance symmetrization/PSD repair, and external-pose reset.
- Split-conformal scalar risk intervals with explicit exchangeability limitation and empirical coverage evaluation.
- Rolling transparent domain-shift detector with four shift states and a detector-confidence multiplier.
- Numerical unit tests for simple preintegration motion, ESKF covariance/quaternion invariants, conformal interval behavior, and sustained shift escalation.

## Classification

| Subsystem | Classification |
|---|---|
| Existing synthetic pipeline and media | Implemented / Synthetic Validation |
| OpenCV feature frontend | Research Prototype |
| IMU preintegration | Research Prototype / analytical unit tests added |
| Error-state EKF | Research Prototype / numerical invariant tests added |
| Conformal risk bounds | Experimental |
| Domain-shift detector | Experimental |
| Public dataset execution | Planned / Pending Dataset Execution |
| ROS2 execution | Planned / Hardware Validation Required |
| Production VIO, formal safety, hardware safety | Not claimed |

## Validation boundary

This branch was authored through the GitHub connector because the execution sandbox could not resolve `github.com`, so the repository could not be cloned and commands such as `pytest`, Ruff, Black, Docker, or experiment runners could not be executed locally in this session. CI must therefore be treated as the first executable verification step. No dataset metrics, benchmark comparisons, calibrated-performance claims, or hypothesis confirmations are reported.

## Next executable slice

1. Run CI and repair any formatting, import, or numerical failures.
2. Connect feature observations and preintegrated IMU increments to an executable ESKF scenario.
3. Add explicit degradation manifests and train/calibration/test splits.
4. Add calibrated logistic baseline, Brier/ECE/reliability plots, and warning-lead-time evaluation.
5. Couple calibrated risk and shift state to the navigation shield and recovery policy.
6. Add mocked EuRoC/TUM-VI fixtures before any real dataset claim.
