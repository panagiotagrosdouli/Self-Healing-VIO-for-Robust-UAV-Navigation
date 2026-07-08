from self_healing_vio.backends import OpenVINSHealthAdapter


def test_openvins_adapter_records_recovery_action():
    adapter = OpenVINSHealthAdapter(feature_count=120, reprojection_error_px=2.0)
    assert adapter.get_feature_count() == 120
    assert adapter.get_reprojection_error() == 2.0
    adapter.apply_recovery_action("request_hover")
    assert adapter.last_action == "request_hover"
