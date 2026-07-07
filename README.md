# Self-Healing VIO: Failure-Aware, Self-Diagnosing Visual-Inertial Navigation for Autonomous UAVs

> *"Can a Visual-Inertial Odometry system know when it is about to fail, understand why, and repair itself before a human ever has to intervene?"*

[![Build Status](https://img.shields.io/badge/CI-passing-brightgreen)]()
[![ROS2](https://img.shields.io/badge/ROS2-Humble%2FJazzy-blue)]()
[![License](https://img.shields.io/badge/license-MIT-lightgrey)]()
[![Docker](https://img.shields.io/badge/docker-ready-blue)]()

---

## 1. Motivation

Visual-Inertial Odometry (VIO) is the backbone of GPS-denied UAV autonomy, but every deployed pipeline — ORB-SLAM3, VINS-Fusion, OpenVINS, OKVIS, Kimera-VIO — shares the same structural weakness: **they are designed to estimate state assuming the sensing pipeline is healthy, and they degrade silently.** By the time an operator (or a downstream planner) notices drift, feature collapse, or a diverged filter, the vehicle has often already accumulated unrecoverable error or entered an unsafe state.

Failure in VIO is rarely a single discrete event. It is a **process** — texture starts thinning, reprojection error creeps up, the IMU preintegration and visual innovation start to disagree, feature tracks fragment under motion blur — long before the system formally "loses tracking." This project treats VIO robustness as a **monitoring, diagnosis, and control problem**, not just an estimation problem.

**Self-Healing VIO** is a modular framework that:

1. **Monitors** its own perceptual and estimation health continuously, using an interpretable multi-signal health state.
2. **Detects** the onset of degradation before catastrophic failure (feature collapse, tracking loss, divergence).
3. **Diagnoses** the probable *root cause* of degradation (camera, environment, motion, sensor, or algorithmic).
4. **Selects and executes** a recovery action from a structured action space, using a learned online policy.
5. **Reports** a single interpretable scalar — the **Navigation Health Index (NHI, 0–100)** — that downstream planners, safety monitors, or human operators can consume directly.

This repository is the reference implementation, benchmark suite, and experimental record for that research direction.

---

## 2. Core Research Question

> **How can a VIO system autonomously detect that it is becoming unreliable, identify the source of failure, recover online, and continue operating without human intervention?**

This decomposes into four falsifiable sub-questions, each with a corresponding experiment in Section 8:

| # | Sub-question | Experiment |
|---|---|---|
| RQ1 | Can VIO health be estimated as a continuous, calibrated signal *before* tracking loss, rather than as a binary lost/tracking flag? | Failure-prediction lead-time study (Sec. 8.3) |
| RQ2 | Can the *cause* of degradation be inferred with useful accuracy from onboard signals alone (no privileged simulator state)? | Diagnosis confusion-matrix study (Sec. 8.4) |
| RQ3 | Does closing the loop — automatically executing a recovery action conditioned on diagnosis — improve trajectory accuracy and uptime versus a static baseline? | Recovery ablation study (Sec. 8.5) |
| RQ4 | Does an online-adapting policy (bandit/RL) outperform a fixed rule-based recovery table as failure modes drift across sequences/domains? | Policy comparison study (Sec. 8.6) |

---

## 3. System Architecture

```
                         ┌────────────────────────────┐
   Stereo/Mono Camera →  │        PERCEPTION          │
   IMU (accel/gyro)   →  │  (frontend, IMU preint.)   │
                         └──────────────┬─────────────┘
                                        │  raw + intermediate signals
                                        ▼
                         ┌────────────────────────────┐
                         │     FAILURE DETECTION       │  ← 12 detectors, Sec. 4
                         │  (per-signal health scores)  │
                         └──────────────┬─────────────┘
                                        │  health signal vector h(t)
                                        ▼
                         ┌────────────────────────────┐
                         │     FAILURE DIAGNOSIS        │  ← causal probability head, Sec. 5
                         │  P(camera, env, motion,      │
                         │    sensor, algorithm | h(t))  │
                         └──────────────┬─────────────┘
                                        │ diagnosis posterior d(t)
                                        ▼
                         ┌────────────────────────────┐
                         │  RECOVERY POLICY (learned)   │  ← contextual bandit, Sec. 6
                         │  selects a_t ∈ action space   │
                         └──────────────┬─────────────┘
                                        │ recovery action a_t
                                        ▼
                         ┌────────────────────────────┐
                         │ ADAPTIVE VIO RECONFIGURATION │
                         │ (detector/weights/reset/etc.) │
                         └──────────────┬─────────────┘
                                        │ reconfigured estimator
                                        ▼
                         ┌────────────────────────────┐
                         │    HEALTH MONITORING LOOP    │──┐
                         │  (closes the loop each frame) │  │
                         └──────────────┬─────────────┘  │
                                        │                 │
                                        ▼                 │
                         ┌────────────────────────────┐   │
                         │ CONFIDENCE-AWARE STATE EST.  │   │
                         │  pose + covariance + NHI(t)   │   │
                         └──────────────┬─────────────┘   │
                                        └─────────────────┘
                                        ▼
                              Pose, Uncertainty, NHI(t)
                              → planner / safety monitor
```

Full module-by-module design, interfaces, and message schemas are in [`RESEARCH_FRAMEWORK.md`](./RESEARCH_FRAMEWORK.md).

---

## 4. Failure Detection (12 signals)

Each detector outputs a normalized score in `[0, 1]` (1 = healthy) plus a raw diagnostic value, published as a ROS2 topic under `/vio_health/<signal>`:

`low_texture`, `motion_blur`, `dynamic_scene`, `fast_rotation`, `feature_tracking_quality`, `imu_consistency`, `sensor_desync`, `image_entropy`, `feature_collapse`, `reprojection_error`, `innovation_residual`, `tracking_drift`.

Details, thresholds, and estimators for each are in `RESEARCH_FRAMEWORK.md §2`.

## 5. Failure Diagnosis

A lightweight probabilistic head maps the 12-dimensional health vector to a distribution over five causal categories — **camera, environment, motion, sensor, algorithm** — using a lookup-table Bayesian model as the interpretable baseline and a small MLP/GNN as the learned alternative. See `RESEARCH_FRAMEWORK.md §3`.

## 6. Recovery Actions & Policy

An 18-action recovery space (detector switching, RANSAC/covariance retuning, relocalization, keyframe reinsertion, semantic filtering, partial map reset, etc.), selected online by a **contextual bandit** (default), with **Decision Transformer** and **Bayesian Optimization** as ablation baselines. Full trade-off analysis in `RESEARCH_FRAMEWORK.md §4`.

## 7. Navigation Health Index (NHI)

A single 0–100 scalar fusing state uncertainty, sensor uncertainty, perception uncertainty, and estimated navigation risk into one calibrated, interpretable number for downstream consumers. Formulation in `RESEARCH_FRAMEWORK.md §5`.

## 8. Evaluation

**Datasets:** EuRoC MAV, TUM-VI, UZH-FPV, Hilti SLAM Challenge, Newer College, plus a custom Gazebo/PX4-SITL and AirSim degradation benchmark for controlled fault injection.

**Baselines:** ORB-SLAM3, VINS-Fusion, OpenVINS, OKVIS, Kimera-VIO.

**Metrics:** ATE, RPE, tracking-success rate, recovery latency, recovery success rate, failure-prediction lead time and accuracy, runtime, energy draw, confidence calibration (ECE).

Full protocol, sequence lists, and ablation matrix in `RESEARCH_FRAMEWORK.md §6`.

## 9. Novel Contributions

1. **Self-Healing VIO** — the first closed-loop detect→diagnose→recover architecture for VIO evaluated with a standard SLAM benchmark protocol.
2. **Failure-aware visual frontend** — a frontend that reports calibrated per-signal health, not just feature counts.
3. **Causal failure diagnosis for VIO** — attributing degradation to a specific root cause rather than a generic "tracking lost" flag.
4. **Online recovery policy under distribution shift** — contextual-bandit recovery selection that adapts as failure modes change across sequences.
5. **Navigation Health Index** — a single calibrated, interpretable robustness scalar suitable for safety monitors and mission planners.

Novelty justification for each is in `RESEARCH_FRAMEWORK.md §7`.

## 10. Repository Structure

```
configs/                  Experiment & module configs (yaml)
docs/RESEARCH_FRAMEWORK.md Full technical design document
paper/                    Paper draft, figures, BibTeX
src/self_healing_vio/
  perception/             Frontend, IMU preintegration adapters
  detection/              12 failure-detection modules
  diagnosis/              Causal diagnosis head (Bayesian + learned)
  recovery/                Action space + policies (bandit/DT/BO)
  fusion/                  Confidence-aware EKF / factor-graph backend
  health/                  NHI computation + calibration
  ros2/                    ROS2 nodes, launch files, message defs
scripts/                  Dataset prep, fault-injection, benchmarking
experiments/              Ablation & benchmark definitions (yaml)
tests/                    Unit + integration tests
docker/                   Reproducible build environment
.github/workflows/        CI (lint, unit tests, smoke SLAM run)
results/                  Generated outputs (git-ignored)
```

## 11. Getting Started

```bash
git clone https://github.com/panagiotagrosdouli/Self-Healing-VIO-for-Robust-UAV-Navigation
cd Self-Healing-VIO-for-Robust-UAV-Navigation
docker build -t self-healing-vio -f docker/Dockerfile .
docker run -it --rm -v $(pwd):/workspace self-healing-vio
# inside container
colcon build --symlink-install
source install/setup.bash
ros2 launch self_healing_vio euroc_baseline.launch.py sequence:=MH_04_difficult
```

## 12. Roadmap

- [x] Reproducible ORB-SLAM3 / EuRoC baseline
- [ ] 12-signal health monitor (frame-rate real time, C++)
- [ ] Bayesian diagnosis baseline + learned diagnosis head
- [ ] Recovery action space + rule-based controller
- [ ] Contextual-bandit recovery policy, ablated against DT/BO
- [ ] Navigation Health Index + calibration study
- [ ] Full benchmark across EuRoC/TUM-VI/UZH-FPV/Hilti/Newer College
- [ ] Fault-injection benchmark in Gazebo/PX4-SITL and AirSim
- [ ] Submission draft (ICRA/IROS target)

## 13. Future Work

Multi-agent health sharing for swarm relocalization, semantic-level failure diagnosis (learned scene understanding as a diagnosis feature), hardware-in-the-loop validation on a real UAV platform, and extending the NHI to a full risk-aware trajectory replanner.

## 14. Citation

```bibtex
@misc{selfhealingvio2026,
  title        = {Self-Healing VIO: Failure-Aware, Self-Diagnosing Visual-Inertial
                  Navigation for Autonomous UAVs},
  author       = {Grosdouli, Panagiota},
  year         = {2026},
  howpublished = {\url{https://github.com/panagiotagrosdouli/Self-Healing-VIO-for-Robust-UAV-Navigation}},
  note         = {Research repository}
}
```

## 15. License

MIT (code) — see `LICENSE`. Dataset licenses (EuRoC, TUM-VI, UZH-FPV, Hilti, Newer College) remain with their respective owners; see `docs/DATASETS.md`.
