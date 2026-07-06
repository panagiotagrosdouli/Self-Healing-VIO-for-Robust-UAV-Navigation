import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class OrbSlam3RunConfig:
    executable: Path
    vocabulary: Path
    settings: Path
    sequence_path: Path
    output_trajectory: Path
    timeout_seconds: Optional[int] = None


@dataclass
class OrbSlam3RunResult:
    return_code: int
    stdout: str
    stderr: str
    output_trajectory: Path


class OrbSlam3Runner:
    def __init__(self, config: OrbSlam3RunConfig) -> None:
        self.config = config

    def validate(self) -> None:
        required = {
            'executable': self.config.executable,
            'vocabulary': self.config.vocabulary,
            'settings': self.config.settings,
            'sequence_path': self.config.sequence_path,
        }
        for name, path in required.items():
            if not Path(path).exists():
                raise FileNotFoundError(f'ORB-SLAM3 {name} not found: {path}')

    def build_command(self) -> list[str]:
        return [
            str(self.config.executable),
            str(self.config.vocabulary),
            str(self.config.settings),
            str(self.config.sequence_path),
            str(self.config.output_trajectory),
        ]

    def run(self) -> OrbSlam3RunResult:
        self.validate()
        self.config.output_trajectory.parent.mkdir(parents=True, exist_ok=True)
        completed = subprocess.run(
            self.build_command(),
            check=False,
            capture_output=True,
            text=True,
            timeout=self.config.timeout_seconds,
        )
        return OrbSlam3RunResult(
            return_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
            output_trajectory=self.config.output_trajectory,
        )
