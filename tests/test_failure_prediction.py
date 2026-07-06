from self_healing_vio.failure_prediction import FailureFeatures, FailurePredictor


def good_features():
    return FailureFeatures(
        tracked_features=180,
        mean_reprojection_error=1.0,
        image_brightness=0.9,
        blur_score=0.9,
        imu_consistency=0.9,
        health_score=0.9,
    )


def bad_features(step=0):
    return FailureFeatures(
        tracked_features=30 - step,
        mean_reprojection_error=8.0,
        image_brightness=0.2,
        blur_score=0.2,
        imu_consistency=0.2,
        health_score=0.25,
    )


def test_failure_predictor_reports_low_risk_for_good_features():
    predictor = FailurePredictor(window_size=3)
    prediction = predictor.update(good_features())
    assert prediction.probability < 0.4
    assert prediction.predicted_time_to_failure_frames == -1


def test_failure_predictor_reports_high_risk_for_bad_features():
    predictor = FailurePredictor(window_size=3)
    for step in range(3):
        prediction = predictor.update(bad_features(step))

    assert prediction.probability > 0.5
    assert prediction.confidence == 1.0
    assert prediction.predicted_time_to_failure_frames in {5, 10}


def test_failure_predictor_empty_prediction_is_safe():
    prediction = FailurePredictor().predict()
    assert prediction.probability == 0.0
    assert prediction.confidence == 0.0
    assert prediction.predicted_time_to_failure_frames == -1
