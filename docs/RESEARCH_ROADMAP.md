# SHIELD-VIO Research Roadmap

This roadmap defines the scientific work required to move SHIELD-VIO from a strong research prototype toward a publishable, externally reproducible robotics research system.

The objective is not to accumulate features. The objective is to answer a small set of falsifiable research questions with transparent evidence, controlled baselines, and explicit limitations.

## Research thesis

Visual–inertial autonomy should not expose only a pose estimate. It should expose when the estimate is becoming unreliable, how confident that diagnosis is, how early failure can be predicted, and which downstream protective action is justified.

SHIELD-VIO studies this thesis through four linked questions:

1. Can estimator-health signals predict localization failure earlier than trajectory-error thresholds alone?
2. Do probability calibration and conformal risk bounds remain informative under controlled domain shift?
3. Does a stateful navigation shield reduce unsafe command execution without excessive intervention?
4. Which signals, degradations, and policy mechanisms are responsible for any observed benefit?

## Evidence ladder

Claims must advance through the following levels in order.

| Level | Evidence | Permitted claim |
|---|---|---|
| L0 | Unit and invariant tests | The implementation satisfies local numerical or logical properties |
| L1 | Deterministic synthetic experiments | The method behaves as expected in controlled scenarios |
| L2 | Repeated synthetic experiments | The effect is statistically stable across seeds and scenario parameters |
| L3 | Public dataset evaluation | The method transfers to recorded real sensor data |
| L4 | Simulator closed loop | Protective actions improve task-level safety metrics in interactive simulation |
| L5 | Hardware experiments | The system operates on a physical platform under a documented protocol |

No result at one level may be described as evidence for a higher level.

## Core hypotheses

### H1 — Early failure prediction

Health-aware predictors provide earlier warning than baselines using only pose error, covariance trace, or fixed innovation thresholds.

Primary metrics:

- area under the precision–recall curve;
- detection lead time before failure;
- false alarms per minute;
- missed-failure rate;
- time-to-detection distribution.

Required baselines:

- covariance-trace threshold;
- NIS threshold;
- visual-feature-count threshold;
- logistic predictor without shift features;
- oracle threshold selected on the test sequence, reported only as an upper bound.

Acceptance criterion:

- improvement must be reported with confidence intervals across sequences or seeds;
- no single metric may be used to claim superiority;
- threshold selection must use validation data only.

### H2 — Calibrated risk under shift

Calibration and conformal risk bounds remain more informative than raw detector scores under degradations and distribution shift.

Primary metrics:

- Brier score;
- negative log likelihood;
- expected calibration error;
- maximum calibration error;
- empirical conformal coverage;
- bound width;
- calibration degradation as shift severity increases.

Required comparisons:

- raw score;
- Platt or logistic calibration;
- isotonic calibration when sufficient data exist;
- split-conformal bound;
- calibration trained in-domain and evaluated out-of-domain.

Acceptance criterion:

- report reliability diagrams and sample counts per bin;
- report both sharpness and coverage;
- do not describe a score as a probability unless calibration has been evaluated.

### H3 — Protective navigation

A stateful shield reduces unsafe downstream commands compared with an unshielded controller and stateless threshold policies.

Primary metrics:

- collision or constraint-violation rate;
- unsafe command duration;
- intervention count;
- unnecessary intervention rate;
- mission completion rate;
- recovery success rate;
- time spent in each shield state.

Required baselines:

- no shield;
- stateless stop threshold;
- covariance-only policy;
- risk-only policy without hysteresis;
- full stateful shield.

Acceptance criterion:

- safety gains must be accompanied by utility costs;
- emergency-stop performance must not hide excessive false interventions;
- policy thresholds must be frozen before test evaluation.

### H4 — Component responsibility

Observed gains are attributable to identifiable components rather than scenario-specific tuning.

Required ablations:

- remove visual-health features;
- remove IMU-health features;
- remove consistency features;
- remove calibration;
- remove domain-shift state;
- remove hysteresis and dwell time;
- replace recovery selection with halt-only behavior.

Acceptance criterion:

- report effect sizes, uncertainty, and failure cases;
- negative results remain part of the record;
- tuning budgets must be comparable across ablations.

## Benchmark protocol

### Public datasets

Initial targets:

- EuRoC MAV;
- TUM-VI.

For every sequence, record:

- dataset and sequence identifier;
- exact input paths or download instructions;
- camera and IMU rates;
- calibration files used;
- coordinate-frame conventions;
- synchronization and interpolation policy;
- start and end timestamps;
- random seed where applicable;
- software commit SHA;
- configuration file hash;
- hardware and runtime environment.

### Splits

Sequence selection must be declared before final evaluation.

- development sequences: implementation debugging only;
- validation sequences: threshold and hyperparameter selection;
- test sequences: final reporting only.

No test-sequence result may influence model, threshold, or policy selection.

### Failure definition

A failure label must be operational and reproducible. Candidate definitions include:

- trajectory error exceeds a predeclared threshold for a minimum duration;
- tracking is lost for a minimum number of frames;
- estimator reset or divergence condition occurs;
- downstream controller violates a declared safety constraint.

Every experiment must identify the exact definition used. Injected degradation is not itself a failure label.

## Statistical reporting

For repeated experiments, report:

- number of independent seeds or sequences;
- mean, median, standard deviation, and interquartile range where appropriate;
- bootstrap or analytical confidence intervals;
- paired comparisons when methods share the same scenario;
- all exclusions and failed runs;
- sensitivity to principal thresholds and hyperparameters.

Avoid significance testing without effect sizes. Avoid selecting only favorable scenarios.

## Reproducibility contract

Every result intended for the README, a report, or a paper must be generated from a command that produces:

- resolved configuration;
- software commit SHA;
- environment metadata;
- deterministic seed information;
- raw metrics;
- event logs;
- figures generated from raw artifacts;
- a manifest linking all outputs.

Pinned figures must never be edited manually after generation, except for format conversion that does not alter data.

## Engineering milestones

### Milestone A — Benchmark runner

Deliverables:

- executable EuRoC and TUM-VI sequence runner;
- timestamp synchronization tests;
- frame and unit validation;
- sequence manifest;
- graceful handling of missing or malformed data.

Definition of done:

- one command executes a declared sequence and produces a complete manifest;
- CI verifies adapters using fixtures;
- at least one real sequence is executed outside CI and documented without claiming benchmark superiority.

### Milestone B — Evaluation harness

Deliverables:

- frozen failure definitions;
- baseline implementations;
- lead-time and false-alarm metrics;
- calibration and reliability plots;
- aggregate multi-sequence reports.

Definition of done:

- all methods use identical splits and labels;
- results can be regenerated from raw artifacts;
- uncertainty intervals are included.

### Milestone C — Closed-loop simulator

Deliverables:

- documented simulator and robot model;
- navigation task suite;
- safety constraints;
- unshielded and shielded baselines;
- intervention and mission metrics.

Definition of done:

- repeated trials demonstrate both safety and utility effects;
- failures and non-improvements are retained;
- simulator evidence is labelled separately from dataset evidence.

### Milestone D — Paper-ready release

Deliverables:

- frozen release tag;
- archived artifacts;
- complete experiment matrix;
- ablation study;
- limitations and ethics statement;
- reproducibility checklist;
- citation metadata and archival identifier when actually issued.

Definition of done:

- every main claim maps to a figure or table and an executable command;
- every figure maps to raw data and a manifest;
- repository state matches the submitted manuscript.

## Recommended experiment matrix

| Experiment | Dataset / environment | Comparison | Main output |
|---|---|---|---|
| Synthetic degradation sweep | Seeded simulator | detectors and health features | robustness curves |
| Cross-seed stability | Synthetic scenarios | repeated runs | confidence intervals |
| Public-sequence failure prediction | EuRoC / TUM-VI | health-aware vs threshold baselines | PR curves and lead time |
| Calibration transfer | train-domain vs shifted-domain sequences | raw vs calibrated vs conformal | reliability and coverage |
| Shield ablation | interactive simulator | no shield, stateless, stateful | safety–utility frontier |
| Sensitivity analysis | all validated environments | thresholds and window sizes | stability plots |

## Research hygiene

- Keep hypotheses distinct from conclusions.
- Register evaluation protocols before final runs.
- Preserve negative and null results.
- Separate exploratory notebooks from release-generating scripts.
- Review coordinate frames, units, and timestamps as carefully as model code.
- Never use visual polish as a substitute for evidence.
- Never imply affiliation with ETH Zurich, UZH, or another institution unless an actual affiliation exists.

## Immediate priorities

1. Execute one complete EuRoC sequence through the current adapters.
2. Freeze a reproducible failure definition and split policy.
3. Implement baseline comparisons and lead-time metrics.
4. Add calibration reliability diagrams and empirical coverage reporting.
5. Build a minimal closed-loop simulator benchmark for shield policies.
6. Publish an experiment manifest that connects every reported result to code, configuration, and raw artifacts.
