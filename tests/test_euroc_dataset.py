from self_healing_vio.datasets.euroc import EurocDataset


def test_euroc_image_loading(tmp_path):
    cam0 = tmp_path / 'mav0' / 'cam0' / 'data'
    cam1 = tmp_path / 'mav0' / 'cam1' / 'data'
    cam0.mkdir(parents=True)
    cam1.mkdir(parents=True)
    (cam0 / '1403636579763555584.png').write_bytes(b'')
    (cam1 / '1403636579763555584.png').write_bytes(b'')

    dataset = EurocDataset(tmp_path)

    assert len(dataset.cam0_images()) == 1
    assert len(dataset.cam1_images()) == 1
    assert dataset.cam0_images()[0].timestamp_ns == 1403636579763555584


def test_euroc_imu_loading(tmp_path):
    imu_dir = tmp_path / 'mav0' / 'imu0'
    imu_dir.mkdir(parents=True)
    (imu_dir / 'data.csv').write_text(
        '#timestamp,w_x,w_y,w_z,a_x,a_y,a_z\n'
        '100,0.1,0.2,0.3,9.7,0.1,-0.2\n'
    )

    dataset = EurocDataset(tmp_path)
    measurements = dataset.imu_measurements()

    assert len(measurements) == 1
    assert measurements[0].gyro_x == 0.1
    assert measurements[0].accel_x == 9.7


def test_euroc_ground_truth_loading(tmp_path):
    gt_dir = tmp_path / 'mav0' / 'state_groundtruth_estimate0'
    gt_dir.mkdir(parents=True)
    (gt_dir / 'data.csv').write_text(
        '#timestamp,p_x,p_y,p_z,q_w,q_x,q_y,q_z\n'
        '100,1.0,2.0,3.0,1.0,0.0,0.0,0.0\n'
    )

    dataset = EurocDataset(tmp_path)
    poses = dataset.ground_truth()

    assert len(poses) == 1
    assert poses[0].tx == 1.0
    assert poses[0].qw == 1.0


def test_euroc_summary(tmp_path):
    cam0 = tmp_path / 'mav0' / 'cam0' / 'data'
    cam0.mkdir(parents=True)
    (cam0 / '100.png').write_bytes(b'')

    summary = EurocDataset(tmp_path).summary()

    assert summary['num_cam0_images'] == 1
    assert summary['num_imu_measurements'] == 0
