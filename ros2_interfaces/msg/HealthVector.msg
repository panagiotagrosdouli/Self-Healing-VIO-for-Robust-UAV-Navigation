# Planned ROS2 message definition for SHIELD-VIO health vectors.
# This file documents the intended interface. It is not yet packaged as a full ROS2 package.

builtin_interfaces/Time stamp
string[] detector_names
float32[] health_scores
float32 navigation_health_index
float32 uncertainty
