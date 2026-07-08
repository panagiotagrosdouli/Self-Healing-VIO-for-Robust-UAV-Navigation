# SHIELD-VIO: Ασφαλής Οπτικο-Αδρανειακή Οδομετρία

Το SHIELD-VIO μελετά πώς ένα σύστημα Visual-Inertial Odometry μπορεί να ανιχνεύει πότε η εκτίμηση κατάστασης γίνεται αναξιόπιστη και να προστατεύει την πλοήγηση από μη ασφαλείς αποτυχίες αντίληψης.

Το αποθετήριο είναι ερευνητικό πρωτότυπο. Δεν δηλώνει state-of-the-art αποτελέσματα και δεν αναφέρει benchmark αριθμούς χωρίς αναπαραγώγιμα πειράματα.

## Εκκίνηση

```bash
python -m pip install -e '.[dev]'
pytest -q
python scripts/run_synthetic_experiment.py --scenario nominal --seed 7
python scripts/make_demo_gif.py
```

Implemented: ESKF scaffold, quaternion/covariance utilities, uncertainty metrics, visual quality, IMU consistency, safety shield, ATE/RPE, synthetic demo.

Prototype: synthetic degradation experiments and GIF/video generation.

Planned: EuRoC/TUM-VI/KITTI benchmarks, ROS2 node, RViz, hardware validation, website.
