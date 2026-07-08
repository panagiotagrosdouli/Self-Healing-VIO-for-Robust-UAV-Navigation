from self_healing_vio.fusion import TemporalHealthFilter


def test_temporal_filter_keeps_health_bounded():
    filt = TemporalHealthFilter(initial_health=100.0)
    mean, std = filt.update(10.0)
    assert 0.0 <= mean <= 100.0
    assert std >= 0.0
