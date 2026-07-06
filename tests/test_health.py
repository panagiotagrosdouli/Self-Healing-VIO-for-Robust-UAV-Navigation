from self_healing_vio.health import VioHealthMonitor, VioHealthSignals


def test_health_monitor_reports_healthy_tracking():
    monitor = VioHealthMonitor()
    estimate = monitor.estimate(
        VioHealthSignals(
            tracking_ok=True,
            tracked_features=180,
            mean_reprojection_error=1.0,
            image_brightness=0.9,
            blur_score=0.9,
            imu_consistency=0.9,
        )
    )
    assert estimate.level == 'healthy'
    assert estimate.failure_probability < 0.5


def test_health_monitor_reports_critical_tracking():
    monitor = VioHealthMonitor()
    estimate = monitor.estimate(
        VioHealthSignals(
            tracking_ok=False,
            tracked_features=5,
            mean_reprojection_error=10.0,
            image_brightness=0.1,
            blur_score=0.1,
            imu_consistency=0.1,
        )
    )
    assert estimate.level == 'critical'
    assert estimate.failure_probability > 0.7
