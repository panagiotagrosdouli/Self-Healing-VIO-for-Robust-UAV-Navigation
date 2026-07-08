# System Architecture

Modules: `core`, `estimation`, `frontend`, `imu`, `uncertainty`, `safety`, `evaluation`, `visualization`, `ros2`, and `utils`.

Scientific motivation: decouple estimator uncertainty, visual degradation, IMU consistency, and navigation shielding so each claim can be tested independently.
