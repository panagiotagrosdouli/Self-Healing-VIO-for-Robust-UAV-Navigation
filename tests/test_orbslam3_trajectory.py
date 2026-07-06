from self_healing_vio.orbslam3.trajectory import load_tum_trajectory


def test_load_tum_trajectory(tmp_path):
    trajectory_file = tmp_path / 'trajectory.txt'
    trajectory_file.write_text(
        '# timestamp tx ty tz qx qy qz qw\n'
        '1.0 0.1 0.2 0.3 0.0 0.0 0.0 1.0\n'
    )

    poses = load_tum_trajectory(trajectory_file)

    assert len(poses) == 1
    assert poses[0].timestamp == 1.0
    assert poses[0].tx == 0.1
    assert poses[0].qw == 1.0


def test_load_tum_trajectory_missing_file_returns_empty_list(tmp_path):
    poses = load_tum_trajectory(tmp_path / 'missing.txt')
    assert poses == []
