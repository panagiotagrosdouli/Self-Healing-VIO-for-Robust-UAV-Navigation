# SHIELD-VIO

**Self-Healing Intelligent Estimation and Localization for Degradation-aware Visual-Inertial Odometry**

> Can a Visual-Inertial Odometry system know when it is becoming unreliable, diagnose why, and select a recovery action before catastrophic localization failure?

[![Python Prototype](https://img.shields.io/badge/prototype-Python-blue)]()
[![ROS2](https://img.shields.io/badge/ROS2-planned-lightgrey)]()
[![License](https://img.shields.io/badge/license-MIT-lightgrey)]()

---

## Motivation

Visual-Inertial Odometry (VIO) is a foundation of GPS-denied UAV autonomy. However, practical VIO systems can degrade silently under motion blur, low texture, illumination changes, sensor inconsistency, aggressive motion, and estimator divergence. SHIELD-VIO studies VIO robustness as a closed-loop autonomy problem: monitor degradation, diagnose likely cause, and select a recovery action.

This repository currently contains a **research framework and executable Python prototype**. ROS2/C++ integration and full VIO backend coupling are planned work, not completed claims.

---

## Implemented Prototype

The current prototype includes:

- normalized detector interface with health scores in `[0, 1]`
- `ImageEntropyDetector`
- `MotionBlurDetector`
- `FeatureCollapseDetector`
- `IMUConsistencyDetector`
- `ReprojectionErrorMonitor`
- `NavigationHealthIndex` in `[0, 100]`
- `BayesianFailureDiagnosis`
- `RuleBasedRecoveryPolicy`
- synthetic degradation demo
- unit tests for detector ranges, NHI range, diagnosis normalization, and recovery actions

---

## Planned ROS2 / C++ Integration

Planned work includes:

- ROS2 health monitor node
- ROS2 messages for health vector, diagnosis posterior, NHI, and recovery action
- integration with OpenVINS, VINS-Fusion, ORB-SLAM3, or Kimera-VIO
- real-time C++ detector implementations
- dataset benchmark runner
- UAV/simulator fault-injection experiments

---

## Repository Structure

```text
configs/default.yaml              Prototype thresholds and policy settings
docs/RESEARCH_FRAMEWORK.md        Formal technical framework
docs/PHD_PROPOSAL.md              PhD-style research proposal
docs/V4RL_ALIGNMENT.md            Academic alignment with V4RL themes
paper/abstract.md                 Conference-style abstract
paper/contributions.md            Publication-style contributions
src/self_healing_vio/             Python prototype package
scripts/demo_health_monitor.py    Runnable synthetic degradation demo
tests/                            Unit tests
ROADMAP.md                        Staged implementation roadmap
```

---

## Getting Started

```bash
git clone https://github.com/panagiotagrosdouli/SHIELD-VIO.git
cd SHIELD-VIO
python -m venv .venv
source .venv/bin/activate
pip install numpy pytest
export PYTHONPATH=$PWD/src
python scripts/demo_health_monitor.py
pytest -q
```

Expected demo output includes detector scores, diagnosis probabilities, selected recovery action, and Navigation Health Index over a synthetic degradation sequence.

---

## Research Documents

- [Research Framework](docs/RESEARCH_FRAMEWORK.md)
- [PhD Proposal](docs/PHD_PROPOSAL.md)
- [V4RL Alignment](docs/V4RL_ALIGNMENT.md)
- [Roadmap](ROADMAP.md)
- [Conference Abstract](paper/abstract.md)
- [Publication Contributions](paper/contributions.md)

---

## Core Research Questions

1. Can VIO degradation be represented as a continuous health signal before tracking loss?
2. Can onboard signals infer a useful posterior over degradation causes?
3. Can diagnosis-conditioned recovery improve uptime and estimator consistency?
4. Can a Navigation Health Index provide an interpretable autonomy-facing reliability signal?
5. Can learned recovery policies outperform rule-based policies under domain shift while preserving safety constraints?

---

## Navigation Health Index

The Navigation Health Index is a scalar in `[0, 100]` computed from normalized health scores and optional risk penalties. It is intended as an interpretable reliability signal for planners, safety monitors, and human operators.

---

## Research Positioning

SHIELD-VIO is intended as a PhD-level research direction at the intersection of:

- visual-inertial navigation
- robust perception
- autonomous UAVs
- uncertainty-aware autonomy
- perception-aware robotics
- field robotics

The project does not claim that VIO can be made failure-proof. It investigates whether VIO can become more transparent, diagnosable, and recoverable under degradation.

---

## Citation

```bibtex
@misc{shieldvio2026,
  title        = {SHIELD-VIO: Self-Healing Intelligent Estimation and Localization
                  for Degradation-aware Visual-Inertial Odometry},
  author       = {Grosdouli, Panagiota},
  year         = {2026},
  howpublished = {\url{https://github.com/panagiotagrosdouli/SHIELD-VIO}},
  note         = {Research prototype}
}
```

---

## License

MIT, unless otherwise specified. Dataset licenses remain with their respective providers.
