# SHIELD-VIO visual research guide

This page collects repository-native generated diagrams used to communicate the research architecture without relying on external image hosting.

## System overview

<p align="center">
  <img src="../assets/readme/shield_vio_research_overview.svg" alt="SHIELD-VIO research overview" width="100%" />
</p>

## Real visual feature tracking

<p align="center">
  <img src="../assets/readme/feature_tracking_pipeline.svg" alt="Feature tracking pipeline" width="100%" />
</p>

The diagram summarizes the implemented OpenCV frontend: Shi–Tomasi detection, pyramidal Lucas–Kanade tracking, forward–backward rejection, persistent IDs, and visual-health diagnostics.

## IMU preintegration and 15-state ESKF

<p align="center">
  <img src="../assets/readme/eskf_pipeline.svg" alt="IMU preintegration and ESKF pipeline" width="100%" />
</p>

This is a research-prototype estimator view. It does not imply production-quality VIO performance.

## Calibrated failure prediction

<p align="center">
  <img src="../assets/readme/failure_prediction_pipeline.svg" alt="Failure prediction and domain-shift pipeline" width="100%" />
</p>

The visual distinguishes raw diagnostics, detector scores, probability calibration, conformal bounds, and domain-shift gating.

## Navigation shielding and recovery

<p align="center">
  <img src="../assets/readme/navigation_shield_state_machine.svg" alt="Navigation shield state machine" width="100%" />
</p>

The shield is supervisory research logic with hysteresis and emergency overrides. It is not a formally verified controller.

## Evidence boundary

These diagrams are explanatory documentation. They do not constitute new experiment results, public-dataset evidence, ROS 2 validation, simulator validation, hardware validation, or formal safety guarantees.
