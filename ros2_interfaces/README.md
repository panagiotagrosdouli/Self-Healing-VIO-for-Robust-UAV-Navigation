# SHIELD-VIO ROS2 Interface Plan

This directory documents planned ROS2 message interfaces for the real-time SHIELD-VIO stack. The current repository remains a Python research prototype; these `.msg` files specify the intended integration contract for a future ROS2 package.

## Planned Topics

| Topic | Message | Purpose |
|---|---|---|
| `/shield_vio/health` | `HealthVector` | Detector scores, NHI, and uncertainty summary |
| `/shield_vio/diagnosis` | `DiagnosisPosterior` | Posterior over degradation causes |
| `/shield_vio/recovery_action` | `RecoveryAction` | Recovery command selected by the policy |

## Planned Nodes

```text
camera + imu + VIO backend
        |
        v
health_monitor_node
        |
        v
diagnosis_node
        |
        v
recovery_policy_node
        |
        v
OpenVINS / planner / UAV safety controller
```

## Integration Status

Implemented now:

- Python dataclasses mirroring these payloads
- prototype detectors and recovery policy
- OpenVINS adapter contract

Planned:

- actual ROS2 package metadata
- generated Python/C++ messages
- launch files
- QoS profiles
- lifecycle nodes
- real-time backend instrumentation
