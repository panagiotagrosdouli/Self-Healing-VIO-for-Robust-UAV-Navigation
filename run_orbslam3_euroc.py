import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / 'src'))

import yaml

from self_healing_vio.orbslam3.runner import OrbSlam3RunConfig, OrbSlam3Runner
from self_healing_vio.orbslam3.trajectory import load_tum_trajectory


def parse_args():
    parser = argparse.ArgumentParser(description='Run ORB-SLAM3 on a EuRoC MAV sequence.')
    parser.add_argument('--config', default='configs/orbslam3_euroc.yaml')
    parser.add_argument('--dry-run', action='store_true', help='Print command without executing ORB-SLAM3.')
    return parser.parse_args()


def load_run_config(path: str | Path) -> OrbSlam3RunConfig:
    raw = yaml.safe_load(Path(path).read_text(encoding='utf-8'))
    cfg = raw['orbslam3']
    return OrbSlam3RunConfig(
        executable=Path(cfg['executable']),
        vocabulary=Path(cfg['vocabulary']),
        settings=Path(cfg['settings']),
        sequence_path=Path(cfg['sequence_path']),
        output_trajectory=Path(cfg['output_trajectory']),
        timeout_seconds=cfg.get('timeout_seconds'),
    )


def main():
    args = parse_args()
    config = load_run_config(args.config)
    runner = OrbSlam3Runner(config)
    command = runner.build_command()

    print('ORB-SLAM3 command:')
    print(' '.join(command))

    if args.dry_run:
        return

    result = runner.run()
    poses = load_tum_trajectory(result.output_trajectory)
    print(f'Return code: {result.return_code}')
    print(f'Estimated poses: {len(poses)}')
    print(f'Trajectory: {result.output_trajectory}')


if __name__ == '__main__':
    main()
