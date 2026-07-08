# Mathematical Formulation

SHIELD-VIO assumes an IMU-centric nominal state `x = (p_WI, v_WI, q_WI, b_a, b_g)`, where `p` is pose position, `v` velocity, `q` orientation, and `b_a`, `b_g` accelerometer and gyroscope biases. The 15D error state is `δx = [δp, δv, δθ, δb_a, δb_g]^T` with covariance `P`.

IMU measurements are modeled as `a_m = a + b_a + n_a` and `ω_m = ω + b_g + n_g`. The process model propagates position, velocity, quaternion orientation, biases, and covariance: `P_{k+1}=F_k P_k F_k^T + Q_k`.

For a visual residual `r = z - h(x)`, linearization gives `r ≈ H δx + n`, innovation covariance `S = HPH^T + R`, and Kalman gain `K = PH^T S^{-1}`. Consistency is monitored with `NEES = e^T P^{-1} e` and `NIS = r^T S^{-1} r`.

The uncertainty/risk layer combines covariance trace, log determinant, conditioning, visual tracking quality, IMU consistency, and innovation consistency. The safety shield maps risk to nominal, low-confidence mode, slow-down, hover/halt, or relocalization request.

Limitation: this is an ESKF scaffold for research software maturity, not a full tightly coupled VIO backend.
