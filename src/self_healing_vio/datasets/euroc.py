import csv
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class EurocImageFrame:
    timestamp_ns: int
    path: Path

    @property
    def timestamp_s(self) -> float:
        return self.timestamp_ns * 1e-9


@dataclass
class EurocImuMeasurement:
    timestamp_ns: int
    gyro_x: float
    gyro_y: float
    gyro_z: float
    accel_x: float
    accel_y: float
    accel_z: float

    @property
    def timestamp_s(self) -> float:
        return self.timestamp_ns * 1e-9


@dataclass
class EurocGroundTruthPose:
    timestamp_ns: int
    tx: float
    ty: float
    tz: float
    qw: float
    qx: float
    qy: float
    qz: float

    @property
    def timestamp_s(self) -> float:
        return self.timestamp_ns * 1e-9


class EurocDataset:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.mav0 = self.root / 'mav0'
        self.cam0_dir = self.mav0 / 'cam0' / 'data'
        self.cam1_dir = self.mav0 / 'cam1' / 'data'
        self.imu_csv = self.mav0 / 'imu0' / 'data.csv'
        self.ground_truth_csv = self.mav0 / 'state_groundtruth_estimate0' / 'data.csv'

    def cam0_images(self) -> List[EurocImageFrame]:
        return self._image_frames(self.cam0_dir)

    def cam1_images(self) -> List[EurocImageFrame]:
        return self._image_frames(self.cam1_dir)

    def _image_frames(self, directory: Path) -> List[EurocImageFrame]:
        frames = []
        for image_path in sorted(directory.glob('*.png')):
            try:
                timestamp_ns = int(image_path.stem)
            except ValueError:
                continue
            frames.append(EurocImageFrame(timestamp_ns=timestamp_ns, path=image_path))
        return frames

    def imu_measurements(self) -> List[EurocImuMeasurement]:
        if not self.imu_csv.exists():
            return []
        measurements = []
        with self.imu_csv.open('r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if not row or row[0].startswith('#'):
                    continue
                measurements.append(
                    EurocImuMeasurement(
                        timestamp_ns=int(row[0]),
                        gyro_x=float(row[1]),
                        gyro_y=float(row[2]),
                        gyro_z=float(row[3]),
                        accel_x=float(row[4]),
                        accel_y=float(row[5]),
                        accel_z=float(row[6]),
                    )
                )
        return measurements

    def ground_truth(self) -> List[EurocGroundTruthPose]:
        if not self.ground_truth_csv.exists():
            return []
        poses = []
        with self.ground_truth_csv.open('r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if not row or row[0].startswith('#'):
                    continue
                poses.append(
                    EurocGroundTruthPose(
                        timestamp_ns=int(row[0]),
                        tx=float(row[1]),
                        ty=float(row[2]),
                        tz=float(row[3]),
                        qw=float(row[4]),
                        qx=float(row[5]),
                        qy=float(row[6]),
                        qz=float(row[7]),
                    )
                )
        return poses

    def summary(self) -> dict:
        return {
            'root': str(self.root),
            'num_cam0_images': len(self.cam0_images()),
            'num_cam1_images': len(self.cam1_images()),
            'num_imu_measurements': len(self.imu_measurements()),
            'num_ground_truth_poses': len(self.ground_truth()),
        }
