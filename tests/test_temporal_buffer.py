from self_healing_vio.temporal_buffer import TemporalBuffer, compute_trend


def test_temporal_buffer_keeps_latest_items():
    buffer = TemporalBuffer[int](max_size=3)
    buffer.append(1)
    buffer.append(2)
    buffer.append(3)
    buffer.append(4)

    assert buffer.values() == [2, 3, 4]
    assert buffer.is_full


def test_compute_trend():
    trend = compute_trend([1.0, 2.0, 4.0])
    assert trend.first == 1.0
    assert trend.last == 4.0
    assert trend.delta == 3.0
    assert trend.mean == 7.0 / 3.0


def test_compute_trend_empty():
    trend = compute_trend([])
    assert trend.delta == 0.0
    assert trend.mean == 0.0
