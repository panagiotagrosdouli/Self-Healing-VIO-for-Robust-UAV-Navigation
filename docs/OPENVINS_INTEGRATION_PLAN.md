# OpenVINS Integration Plan

## Purpose

This document defines the planned interface between SHIELD-VIO and OpenVINS. The current repository does not claim a completed OpenVINS integration. Instead, it specifies the measurements, diagnostics, and recovery hooks needed to turn the Python prototype into a real-time VIO health monitor.

## Required Backend Signals

SHIELD-VIO requires the following signals from the VIO backend:

| Signal | Meaning | Candidate Source |
|---|---|---|
| tracked feature count | visual tracking support | frontend feature tracker |
| mean reprojection error | visual residual quality | update residuals |
| innovation statistics | estimator consistency | EKF update statistics |
| IMU residual norm | inertial consistency | propagation/update residuals |
| covariance trace or surrogate | estimator uncertainty | state covariance |
| reset/relocalization status | recovery result | backend services/events |

## Recovery Hooks

The planned adapter should support backend-specific implementations of:

1. reset visual frontend
2. increase feature budget
3. relax outlier rejection threshold
4. reinitialize IMU bias estimate
5. inflate covariance
6. request relocalization
7. switch to inertial fallback mode

## ROS2 Boundary

```text
OpenVINS backend
  -> residual statistics
  -> feature statistics
  -> covariance surrogate
  -> SHIELD-VIO health monitor
  -> diagnosis posterior
  -> recovery policy
  -> OpenVINS services / UAV supervisor
```

## Research Questions Enabled

- Does health-aware monitoring detect degradation before OpenVINS tracking loss?
- Which backend statistics are most predictive of localization failure?
- Can diagnosis-conditioned recovery improve estimator uptime without destabilizing the filter?
- Does uncertainty-aware health reporting improve downstream UAV safety decisions?

## Validation Plan

1. Run OpenVINS unmodified on EuRoC and TUM-VI.
2. Record residual, feature, and covariance statistics.
3. Add synthetic degradation through image blur, feature dropout, low texture, and IMU bias.
4. Compare baseline OpenVINS with SHIELD-VIO monitored OpenVINS.
5. Evaluate ATE, RPE, NHI, failure lead time, and recovery success rate.
