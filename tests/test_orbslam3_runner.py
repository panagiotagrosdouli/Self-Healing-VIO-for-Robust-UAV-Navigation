from pathlib import Path

import pytest

from self_healing_vio.orbslam3.runner import OrbSlam3RunConfig, OrbSlam3Runner


def make_config(tmp_path):
    executable = tmp_path / 'orbslam3'
    vocabulary = tmp_path / 'ORBvoc.txt'
    settings = tmp_path / 'EuRoC.yaml'
    sequence_path = tmp_path / 'MH_01_easy'
    output_trajectory = tmp_path / 'results' / 'trajectory.txt'

    executable.write_text('#!/bin/sh\n')
    vocabulary.write_text('vocab')
    settings.write_text('settings')
    sequence_path.mkdir()

    return OrbSlam3RunConfig(
        executable=executable,
        vocabulary=vocabulary,
        settings=settings,
        sequence_path=sequence_path,
        output_trajectory=output_trajectory,
    )


def test_orbslam3_runner_builds_command(tmp_path):
    config = make_config(tmp_path)
    runner = OrbSlam3Runner(config)
    assert runner.build_command() == [
        str(config.executable),
        str(config.vocabulary),
        str(config.settings),
        str(config.sequence_path),
        str(config.output_trajectory),
    ]


def test_orbslam3_runner_validates_existing_paths(tmp_path):
    runner = OrbSlam3Runner(make_config(tmp_path))
    runner.validate()


def test_orbslam3_runner_rejects_missing_executable(tmp_path):
    config = make_config(tmp_path)
    config.executable = Path('/missing/orbslam3')
    runner = OrbSlam3Runner(config)
    with pytest.raises(FileNotFoundError):
        runner.validate()
