# Self-Healing VIO — Research Framework Document

This document is the technical core of the project: the architecture, the failure taxonomy, the diagnosis model, the recovery policy, the uncertainty/health formulation, the evaluation protocol, and the implementation plan. It is written to the level of detail expected in an ICRA/IROS system paper's method section, and is meant to be read alongside `README.md`.

---

## 0. Design Principles

1. **Interpretability before learning.** Every learned component has an interpretable, non-learned baseline (rule table, Bayesian lookup) it must beat before being adopted. This is what makes the ablations publishable — you can always ask "does the AI component actually help, or does a hand-tuned rule do just as well?"
2. **No privileged information at inference time.** Diagnosis and recovery must operate on signals actually available onboard (image, IMU, estimator internals). Ground-truth fault labels are used only for training/evaluation in simulation, never as an inference-time input.
3. **Closed-loop, not open-loop.** A "failure predictor" alone is a classifier paper. The contribution here is that diagnosis actually changes what the estimator does, and that change is evaluated end-to-end on trajectory accuracy — not just detection AUC.
4. **One interpretable scalar output.** Whatever the internal complexity, the framework must expose a single calibrated number (the NHI) that a planner or operator can threshold on without understanding the internals.

---

## 1. Architecture — Module Contracts

Each block in the README pipeline diagram is a ROS2 node (and a plain-Python/C++ class for offline batch evaluation) with a fixed message contract, so components can be swapped/ablated independently.

| Module | Input | Output | Rate |
|---|---|---|---|
| Perception (frontend) | image(s), IMU | tracked features, reprojection residuals, IMU preintegration | camera rate |
| Failure Detection | frontend outputs + estimator internals | `HealthVector` (12 floats, `[0,1]`) | camera rate |
| Failure Diagnosis | `HealthVector`, short history window | `DiagnosisPosterior` (5 floats, sums to 1) | 1–5 Hz |
| Recovery Policy | `DiagnosisPosterior`, `HealthVector`, action history | `RecoveryAction` (discrete, from 18-action space) | on-trigger (event-driven, rate-limited) |
| Adaptive Reconfiguration | `RecoveryAction` | reconfigured frontend/backend parameters | on-trigger |
| Health Monitoring | all of the above, streamed | logged health trace, trigger events | camera rate |
| Confidence-aware Estimation | reconfigured frontend + backend | pose, covariance, `NHI(t)` | camera rate |

`HealthVector`, `DiagnosisPosterior`, and `RecoveryAction` are defined as ROS2 `.msg` files in `src/self_healing_vio/ros2/msg/`, shown fully in §8.

---

## 2. Failure Detection — 12 Signals

For each signal below: **what it measures**, **how it's computed online**, and **why it matters causally**.

1. **Low texture** — Shannon entropy / gradient-magnitude histogram of the current frame within a normalized window. Low-texture scenes (sky, blank walls, snow) starve the frontend of trackable features long before feature count itself collapses.
2. **Motion blur** — Variance-of-Laplacian sharpness metric, cross-checked against IMU angular velocity magnitude at exposure time (rolling-shutter-aware). Motion blur is a *camera/motion* interaction, distinguishing it from static low texture.
3. **Dynamic scenes** — Ratio of outlier (non-static) feature tracks after epipolar/RANSAC consistency check to total tracks; optionally a lightweight semantic mask (person/vehicle detector) as an auxiliary signal.
4. **Fast rotation** — Gyro magnitude relative to a calibrated per-platform threshold; predicts imminent feature-track loss due to large inter-frame appearance change even before it happens.
5. **Poor feature tracking** — KLT/optical-flow tracking success rate and mean track length over the active window.
6. **IMU consistency** — Mahalanobis distance between IMU-preintegrated relative motion and the vision-only relative motion estimate; large values indicate calibration drift, clock skew, or vibration-induced IMU noise.
7. **Sensor desynchronization** — Cross-correlation of camera/IMU timestamps against the expected trigger model; flags dropped frames or timestamp jitter.
8. **Low image entropy** — Global histogram entropy of the frame (complementary to signal 1 but tuned for illumination collapse — e.g., overexposure/underexposure — rather than texture).
9. **Feature collapse** — Absolute count of high-quality (corner-response-thresholded) features versus a minimum-for-stable-estimation threshold, tracked with hysteresis to avoid chattering.
10. **High reprojection error** — Mean/median reprojection error of active map points after the latest bundle-adjustment or filter update; a direct estimator-internal health signal.
11. **Large innovation residuals** — Normalized innovation squared (NIS) of the EKF/factor-graph update; the classical filter-consistency diagnostic, generalized here as one signal among many rather than the sole trigger.
12. **Tracking drift** — Short-horizon consistency check: re-triangulation error of recently tracked points against the current pose estimate, used as an early proxy for drift that hasn't yet caused catastrophic loss.

Each signal is exposed both as a raw value (for logging/diagnosis) and a **normalized health score** `h_i(t) ∈ [0,1]` via a signal-specific squashing function (typically a calibrated logistic, fit per-dataset in the calibration experiment, §6.5).

```
HealthVector h(t) = [h_1(t), ..., h_12(t)]   ∈ [0,1]^12
```

---

## 3. Failure Diagnosis

**Goal:** map `h(t)` (and a short history, e.g. last 2 s) to a probability distribution over five causal categories:

```
d(t) = [P(camera), P(environment), P(motion), P(sensor), P(algorithm)],   Σ d_i = 1
```

### 3.1 Baseline: Bayesian lookup model (interpretable)

A hand-specified conditional probability table `P(cause | h_i above/below threshold)` per signal, combined via naive-Bayes assumption:

```
P(cause_k | h(t)) ∝ P(cause_k) · Π_i P(h_i(t) | cause_k)
```

Each `P(h_i | cause_k)` is a Beta distribution fit offline from simulation runs with known injected fault type (Gazebo/AirSim fault injection, §6). This baseline is fully interpretable — every diagnosis decision can be traced to which signals drove it — and is the required comparison point for any learned diagnosis head.

### 3.2 Learned alternative: small MLP / GNN

- **MLP:** `h(t)` concatenated with a 1–2 s sliding window (flattened or summarized via mean/slope features) → 2 hidden layers (64/32 units) → softmax over 5 causes. Cheap enough for onboard inference (<1 ms).
- **GNN alternative:** model the 12 signals as nodes in a graph with edges encoding known physical dependencies (e.g., motion_blur ↔ fast_rotation, imu_consistency ↔ sensor_desync), message-passing to produce a diagnosis embedding. Motivated by the fact that failure signals are not i.i.d. — a GNN can exploit known structural correlations the naive-Bayes baseline ignores. This is the "reach" variant proposed for the second paper iteration, not the primary claim.

### 3.3 Ground truth for training/evaluation

Only available in simulation (Gazebo/PX4-SITL/AirSim) where the fault injector (§6.2) knows the true injected cause. On real datasets (EuRoC etc.), diagnosis is evaluated qualitatively / via downstream recovery success, since no ground-truth cause label exists — this limitation should be stated explicitly in the paper.

---

## 4. Recovery Actions & Policy

### 4.1 Action space (18 actions)

| Category | Actions |
|---|---|
| Frontend detector | switch feature detector (FAST↔ORB↔SuperPoint), adapt FAST threshold, switch descriptor (ORB↔BRIEF↔SuperPoint desc.) |
| Frontend robustness | adapt RANSAC threshold, feature masking, dynamic-object rejection, semantic filtering, adaptive window size |
| Backend weighting | increase IMU weight / decrease visual weight (and inverse), adaptive EKF covariance inflation, adaptive factor-graph edge weights |
| Structural recovery | keyframe reinsertion, relocalization, partial map reset, online parameter re-tuning (exposure/gain if camera driver exposes it) |
| No-op | do nothing (explicit action, needed so the policy can learn *not* to intervene on transient noise) |

### 4.2 Policy options — comparative analysis

| Approach | Sample efficiency | Onboard cost | Interpretability | Handles non-stationarity | Verdict |
|---|---|---|---|---|---|
| **Contextual bandit** (LinUCB / Thompson sampling over `(h(t), d(t))` context) | High | Very low | High (linear weights per action) | Good — updates online per episode | **Primary/default.** Best fit: recovery is a repeated single-step decision (pick action, observe short-horizon reward), not a long-horizon credit-assignment problem. |
| **Decision Transformer** | Low (needs offline trajectories) | Moderate–high | Low | Poor unless retrained/fine-tuned | Strong ablation baseline to show whether sequence modeling of past (state, action, reward) actually beats a stateless bandit — hypothesis: it won't, because recovery decisions are close to memoryless given `h(t), d(t)`. |
| **Bayesian Optimization** | High for continuous params | Low | Moderate | Poor (assumes near-stationary objective) | Reserved for *within-action* parameter tuning (e.g., optimal RANSAC threshold value once "adapt RANSAC" is chosen), not action selection itself. |
| **Reinforcement Learning (full MDP, e.g. PPO)** | Low | Moderate | Low | Good if retrained | Only justified if recovery actions have long-horizon consequences (e.g., relocalization quality depends on subsequent motion) — flagged as future work, not primary method, to keep the core claim falsifiable and cheap to reproduce. |
| **Graph Neural Network policy** | Moderate | Moderate | Low | Moderate | Considered only as the policy head paired with the GNN diagnosis model (§3.2); not primary. |

**Reward signal** for the bandit: a short-horizon (0.5–2 s) combination of Δ(reprojection error), Δ(NIS), and whether tracking was maintained, i.e., a proxy that doesn't require ground-truth pose (so it also works on real deployment, not just simulation with ground truth available for offline reward shaping/validation).

### 4.3 Why a bandit, not full RL, is the defensible default

The recovery decision is triggered by a specific health/diagnosis state and its consequence is observable almost immediately (does tracking stabilize in the next second?). This matches the contextual-bandit assumption (single-step reward, no long-horizon credit assignment) far better than it matches a full MDP. Choosing bandit-as-primary with RL/DT as ablations is itself a paper-worthy point: it argues *against* reflexively reaching for the heaviest ML tool, which the AI component section explicitly asked to be justified.

---

## 5. Uncertainty & the Navigation Health Index (NHI)

Four uncertainty streams are estimated and fused:

- **State uncertainty** `σ_state` — trace/determinant of the estimator's pose covariance (EKF covariance or factor-graph marginal covariance).
- **Sensor uncertainty** `σ_sensor` — from IMU consistency (§2.6) and sensor desync (§2.7) signals.
- **Perception uncertainty** `σ_perception` — aggregate of texture, blur, entropy, feature-collapse, reprojection-error signals.
- **Navigation risk** `R_nav` — a forward-looking term: rate of change (slope) of the above over the last window, since a *rapidly worsening* healthy-looking state is riskier than a stable moderately-degraded one.

```
NHI(t) = 100 · σ( w0 + w1·f(σ_state) + w2·f(σ_sensor) + w3·f(σ_perception) + w4·f(R_nav) )
```

where `σ(·)` is a logistic squashing function and `f(·)` are per-term normalizations. Weights `w_i` are fit via **isotonic regression / Platt scaling against empirical tracking-failure outcomes** in the fault-injection benchmark (§6.2), so that `NHI = 50` empirically corresponds to roughly a 50% chance of tracking failure within the next `Δt` seconds — i.e., NHI is *calibrated*, not just a heuristic score. Calibration quality is reported via reliability diagrams and Expected Calibration Error (ECE), addressing the "confidence calibration" metric requested for evaluation.

---

## 6. Evaluation Protocol

### 6.1 Datasets

| Dataset | Role |
|---|---|
| EuRoC MAV | Primary baseline — well-characterized difficulty levels (easy/medium/difficult) |
| TUM-VI | Generalization to different camera/IMU hardware and longer indoor/outdoor sequences |
| UZH-FPV | High-speed/aggressive UAV motion — stresses fast-rotation and motion-blur detectors |
| Hilti SLAM Challenge | Construction/industrial environments — stresses low-texture and dynamic-scene detectors |
| Newer College | Long-duration, large-scale generalization test |
| Custom Gazebo + PX4-SITL | **Controlled fault injection** with ground-truth cause labels (needed for §3.3 and §5 calibration) |
| AirSim | Secondary simulator for cross-simulator generalization check (avoids overfitting the fault-injection benchmark to one simulator's rendering quirks) |

### 6.2 Fault-injection benchmark (novel contribution, Sec. 7.4 support)

A configurable Gazebo/PX4-SITL (and AirSim) scenario generator that injects, with known ground truth: synthetic motion blur, exposure/illumination steps, synthetic dynamic actors, IMU noise/bias injection, artificial frame drops, and low-texture environments (procedurally flattened textures). This is what makes RQ1/RQ2 answerable with ground truth, which the real-world datasets above cannot provide.

### 6.3 Baselines compared against

ORB-SLAM3, VINS-Fusion, OpenVINS, OKVIS, Kimera-VIO — each run (a) unmodified, and (b) wrapped with the Self-Healing layer where architecturally feasible (VINS-Fusion and OpenVINS both expose enough internal state to attach the health/diagnosis layer; ORB-SLAM3/OKVIS/Kimera-VIO are primarily accuracy baselines for (a) only, noted explicitly as a scope limitation).

### 6.4 Metrics

| Metric | Measures |
|---|---|
| ATE / RPE | Standard trajectory accuracy (via `evo`) |
| Tracking success rate | % of sequence with valid pose estimate |
| Recovery latency | Time from failure onset to recovery action execution |
| Recovery success rate | % of triggered recoveries that restore tracking within N seconds |
| Failure-prediction accuracy & lead time | Precision/recall of "will fail in next Δt" + how many seconds of warning are given |
| Runtime | Per-frame wall-clock cost of health/diagnosis/recovery overhead vs. baseline VIO |
| Energy | Estimated compute-proportional power draw (onboard-representative hardware profile, e.g. Jetson Orin) |
| Confidence calibration | ECE / reliability diagram of NHI vs. empirical failure rate |

### 6.5 Ablations

1. Detection-only vs. full closed loop (does closing the loop actually help ATE/RPE, not just detection AUC?).
2. Bayesian diagnosis vs. MLP vs. GNN diagnosis heads.
3. Bandit vs. Decision Transformer vs. Bayesian-Optimization-tuned-rule-table vs. no-policy (random valid action) recovery selection.
4. Per-signal ablation (drop each of the 12 detectors, measure ΔATE / Δrecovery-success) — this produces the "which signals actually matter" table reviewers will expect.
5. Cross-simulator generalization (Gazebo-trained policy evaluated in AirSim, and vice versa).

---

## 7. Novelty Justification (five contributions)

1. **Self-Healing VIO (closed-loop architecture).** Prior "robust VIO" work (e.g., robust cost functions, RANSAC variants) hardens individual stages; prior "failure detection" work (e.g., NIS-based filter consistency checks) stops at detection. The novelty here is a full detect→diagnose→act→re-monitor loop evaluated end-to-end on standard SLAM benchmarks with standard SLAM metrics, not just classifier metrics.
2. **Failure-aware visual frontend.** Most frontends report feature count/quality implicitly through downstream failure. This frontend reports 12 *calibrated, causally distinguishable* health signals as first-class outputs — enabling diagnosis rather than just detection.
3. **Causal failure diagnosis for VIO.** To our knowledge, no existing open VIO pipeline attributes degradation to a specific root cause (camera/environment/motion/sensor/algorithm) online; existing systems report "tracking lost," not "why."
4. **Online recovery policy under distribution shift.** Framing recovery-action selection as a contextual bandit — rather than either a fixed rule table or a heavyweight offline-trained RL policy — is a deliberately minimal, sample-efficient, non-stationarity-tolerant design choice, and the ablation against DT/RL is itself a methodological contribution (showing when heavier ML is *not* worth it).
5. **Navigation Health Index.** A single calibrated 0–100 scalar, validated via reliability diagrams against real failure outcomes, is directly consumable by a mission planner or safety monitor without requiring the consumer to understand covariance matrices or NIS statistics — this operationalizes "uncertainty-aware autonomy" into something usable outside the SLAM community.

*(Honest caveat to include in the paper's limitations section: contributions 1–4 depend partly on simulation ground truth for training/validation; real-world generalization of the diagnosis head specifically should be reported as a qualitative/behavioral validation, not a labeled-accuracy claim, since no real dataset provides ground-truth failure cause.)*

---

## 8. Implementation Plan

### 8.1 Folder structure (expanded)

```
Self-Healing-VIO-for-Robust-UAV-Navigation/
├── configs/
│   ├── datasets/            # euroc.yaml, tumvi.yaml, uzh_fpv.yaml, hilti.yaml, newer_college.yaml
│   ├── detectors/           # per-signal thresholds/calibration params
│   ├── diagnosis/           # bayesian_priors.yaml, mlp_config.yaml, gnn_config.yaml
│   ├── recovery/            # action_space.yaml, bandit_config.yaml, dt_config.yaml
│   └── experiments/         # ablation_matrix.yaml, benchmark_suite.yaml
├── docs/
│   └── RESEARCH_FRAMEWORK.md
├── paper/
│   ├── main.tex, sections/*.tex, figures/, bib/references.bib
├── src/self_healing_vio/
│   ├── perception/          # frontend.py, imu_preintegration.py, camera_models.py
│   ├── detection/
│   │   ├── low_texture.py, motion_blur.py, dynamic_scene.py, fast_rotation.py
│   │   ├── feature_tracking.py, imu_consistency.py, sensor_desync.py
│   │   ├── image_entropy.py, feature_collapse.py, reprojection_error.py
│   │   ├── innovation_residual.py, tracking_drift.py
│   │   └── health_vector.py         # aggregates the 12 into HealthVector
│   ├── diagnosis/
│   │   ├── bayesian_diagnosis.py, mlp_diagnosis.py, gnn_diagnosis.py
│   ├── recovery/
│   │   ├── action_space.py, bandit_policy.py, decision_transformer_policy.py
│   │   ├── bayes_opt_tuner.py, rule_based_policy.py (baseline), reconfigurator.py
│   ├── fusion/
│   │   ├── ekf_backend.py, factor_graph_backend.py, confidence_aware_fusion.py
│   ├── health/
│   │   ├── nhi.py, calibration.py
│   ├── ros2/
│   │   ├── msg/HealthVector.msg, DiagnosisPosterior.msg, RecoveryAction.msg, NHIStamped.msg
│   │   ├── nodes/ (one node per module above)
│   │   └── launch/euroc_baseline.launch.py, full_pipeline.launch.py
│   └── cpp/                 # performance-critical detectors reimplemented in C++ (pybind11-exposed)
├── scripts/
│   ├── download_datasets.sh, fault_injection_gazebo.py, fault_injection_airsim.py
│   ├── run_benchmark.py, run_ablation.py, generate_report.py
├── experiments/              # concrete run definitions referenced by run_benchmark.py
├── tests/
│   ├── unit/ (one test module per detector/diagnosis/policy)
│   └── integration/ (short synthetic-sequence end-to-end tests)
├── docker/
│   ├── Dockerfile, docker-compose.yaml
├── .github/workflows/
│   ├── ci.yaml (lint + unit tests), smoke.yaml (short EuRoC sequence run)
└── results/                  # git-ignored
```

### 8.2 Message contracts (ROS2 `.msg`)

```
# HealthVector.msg
std_msgs/Header header
float32 low_texture
float32 motion_blur
float32 dynamic_scene
float32 fast_rotation
float32 feature_tracking_quality
float32 imu_consistency
float32 sensor_desync
float32 image_entropy
float32 feature_collapse
float32 reprojection_error
float32 innovation_residual
float32 tracking_drift

# DiagnosisPosterior.msg
std_msgs/Header header
float32 p_camera
float32 p_environment
float32 p_motion
float32 p_sensor
float32 p_algorithm

# RecoveryAction.msg
std_msgs/Header header
uint8 action_id
string action_name
float32 confidence

# NHIStamped.msg
std_msgs/Header header
float32 nhi          # 0-100
float32 state_uncertainty
float32 sensor_uncertainty
float32 perception_uncertainty
float32 navigation_risk
```

### 8.3 Core pseudocode

**Main loop (per frame):**

```
function ON_NEW_FRAME(image, imu_batch):
    features, residuals, imu_preint = perception.process(image, imu_batch)
    h = health_vector.compute(features, residuals, imu_preint, estimator.internals())
    health_monitor.log(h)

    if trigger_condition(h):                      # e.g. any h_i below threshold, or NHI dropping fast
        d = diagnosis.infer(h, health_monitor.recent_window())
        a = recovery_policy.select_action(h, d, action_history)
        reconfigurator.apply(a, frontend, backend)
        action_history.append(a, timestamp=now())

    pose, cov = backend.update(features, residuals, imu_preint)
    nhi = nhi_module.compute(cov, h, d_or_last_known(d))
    publish(pose, cov, nhi)

    if recovery_pending():
        reward = evaluate_short_horizon_reward(h_before, h_after, cov_before, cov_after)
        recovery_policy.update(reward)             # online bandit update
```

**Contextual bandit (LinUCB) recovery selection:**

```
function SELECT_ACTION(context):                  # context = concat(h, d)
    for a in action_space:
        p[a] = theta[a]^T context + alpha * sqrt(context^T A_inv[a] context)   # UCB
    return argmax_a p[a]

function UPDATE(a, context, reward):
    A[a] += context context^T
    b[a] += reward * context
    theta[a] = A_inv[a] @ b[a]
```

**Bayesian diagnosis (naive-Bayes baseline):**

```
function INFER(h):
    for cause in {camera, environment, motion, sensor, algorithm}:
        posterior[cause] = prior[cause]
        for i in 1..12:
            posterior[cause] *= likelihood(h[i] | cause)     # fit Beta params offline
    return normalize(posterior)
```

**NHI:**

```
function COMPUTE_NHI(cov, h, d):
    s_state = normalize(trace(cov))
    s_sensor = normalize(f(h.imu_consistency, h.sensor_desync))
    s_perception = normalize(f(h.low_texture, h.motion_blur, h.image_entropy,
                                h.feature_collapse, h.reprojection_error))
    risk = normalize(slope(recent_health_window))
    logit = w0 + w1*s_state + w2*s_sensor + w3*s_perception + w4*risk
    return 100 * sigmoid(logit)      # weights fit via isotonic/Platt calibration, see §5
```

### 8.4 Languages & tooling

- **C++17**, performance-critical detectors (motion blur, entropy, reprojection error) and the fusion backend — exposed to Python via `pybind11` for the diagnosis/recovery/evaluation layers, which are pure Python for research-iteration speed.
- **Python 3.10+** for diagnosis heads, recovery policies, benchmarking scripts, and plotting (`evo`, `matplotlib`, `pandas`, `scikit-learn`, `torch` for MLP/GNN/DT variants).
- **ROS2 (Humble/Jazzy)** for the online/onboard deployment path; all nodes also runnable as plain Python classes for fast offline batch evaluation on dataset bagfiles/rosbags.
- **Docker** for a fully reproducible build (base VIO libraries + ROS2 + Python deps pinned).
- **pytest** for unit tests (one module per detector, diagnosis head, and policy) and a lightweight integration test that runs a 10-second synthetic sequence through the full closed loop end-to-end.
- **GitHub Actions CI**: lint (`ruff`/`clang-format`) + unit tests on every PR; a nightly "smoke" job runs a short EuRoC sequence through the full pipeline and checks it completes without divergence.

---

## 9. Suggested Paper Structure (for `paper/main.tex`)

1. Introduction & motivation (silent degradation problem)
2. Related work (robust VIO, failure detection, online adaptation/bandits/RL for robotics, uncertainty-aware SLAM)
3. Method: architecture, 12-signal health vector, diagnosis model, recovery policy, NHI
4. Fault-injection benchmark description
5. Experiments (RQ1–RQ4, ablations §6.5)
6. Results & discussion (including honest limitations: sim-to-real gap in diagnosis ground truth, baselines not all wrappable)
7. Conclusion & future work

Target venues in order of fit given scope: **IROS/ICRA (systems + robust perception track)** first, with a **Science Robotics / RA-L** extension if the fault-injection benchmark and NHI calibration study are developed into a standalone dataset/benchmark contribution.
