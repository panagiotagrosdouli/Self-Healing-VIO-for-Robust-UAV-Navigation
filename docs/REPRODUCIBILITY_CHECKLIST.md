# Reproducibility Checklist

Use this checklist before merging any experiment, benchmark, README evidence update, technical report, or release.

## Scope and claims

- [ ] The research question and hypothesis are stated before the results.
- [ ] The validation level is identified: unit, synthetic, repeated synthetic, public dataset, simulator, or hardware.
- [ ] Claims do not exceed the available evidence level.
- [ ] Limitations and known failure cases are documented.
- [ ] No institutional affiliation, publication, DOI, or benchmark status is implied unless it is real and verifiable.

## Data and protocol

- [ ] Dataset name, version, sequence identifiers, and acquisition source are recorded.
- [ ] Development, validation, and test splits are declared.
- [ ] Test data were not used for tuning.
- [ ] Coordinate frames, units, timestamp conventions, and synchronization rules are documented.
- [ ] Failure labels are operationally defined.
- [ ] Injected degradation is not automatically used as the failure label.
- [ ] Any excluded sequence, interval, or run is listed with a reason.

## Configuration and provenance

- [ ] The exact Git commit SHA is recorded.
- [ ] The resolved configuration is saved.
- [ ] Configuration hashes are included where practical.
- [ ] Random seeds are recorded.
- [ ] Dependency and Python versions are recorded.
- [ ] Hardware and operating-system details are recorded when runtime results are reported.
- [ ] The command used to generate the result is documented.

## Baselines and comparisons

- [ ] Baselines answer the same task under the same data split.
- [ ] Thresholds and hyperparameters are selected on validation data only.
- [ ] Tuning effort is reasonably comparable across methods.
- [ ] Ablations remove one identifiable component at a time.
- [ ] Oracle or test-selected results are labelled clearly and are not presented as deployable methods.

## Metrics and statistics

- [ ] Primary metrics were selected before final evaluation.
- [ ] Safety improvements are reported together with utility costs.
- [ ] Calibration reports include reliability, sharpness, and sample counts.
- [ ] Repeated studies state the number of seeds or sequences.
- [ ] Effect sizes and uncertainty intervals are reported.
- [ ] Failed runs and missing values are visible rather than silently discarded.
- [ ] Multiple metrics are used when one metric could hide important failure modes.

## Artifacts

- [ ] Raw metrics are retained.
- [ ] Event logs are retained.
- [ ] Figures are generated from raw artifacts by code.
- [ ] A manifest links configurations, results, logs, and figures.
- [ ] README or paper figures can be regenerated without manual data editing.
- [ ] Large external artifacts have stable download or archival instructions.

## Software quality

- [ ] Unit and numerical-invariant tests pass.
- [ ] Static checks pass.
- [ ] New public interfaces have tests and documentation.
- [ ] Errors identify malformed data, frame mismatch, unit mismatch, and missing calibration clearly.
- [ ] The experiment fails loudly rather than producing a plausible but invalid result.

## Release readiness

- [ ] The changelog distinguishes implementation from validation.
- [ ] Citation metadata matches the released version.
- [ ] The repository tag matches the code used for reported results.
- [ ] Archived artifacts correspond to the tagged release.
- [ ] Every principal claim maps to a reproducible table, figure, or experiment output.
