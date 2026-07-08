"""Backend adapters for VIO systems.

The current repository defines contracts and simulation-safe stubs. Concrete
OpenVINS, VINS-Fusion, ORB-SLAM3, or Kimera-VIO integrations are planned work.
"""

from .openvins import OpenVINSAdapterConfig, OpenVINSHealthAdapter

__all__ = ["OpenVINSAdapterConfig", "OpenVINSHealthAdapter"]
