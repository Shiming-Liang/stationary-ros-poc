# Bug Report: Multi-arm `TrossenArmHardwareInterface` fails with duplicate spdlog logger

## Summary

When two `TrossenArmHardwareInterface` hardware plugins are loaded in the same `ros2_control_node`
process (e.g. for a Stationary AI setup), the second plugin fails to configure with:

```
[FATAL] [controller_manager]: Failed to 'configure' hardware 'follower_right_TrossenArmHardwareInterface'
[FATAL]: Failed to create TrossenArmDriver: logger with name 'trossen_arm_driver' already exists
```

## Reproduce

### Build

```bash
docker build -t stationary-ros-poc .
```

### Trigger the issue

```bash
docker run --network host -it stationary-ros-poc ros2 launch my_stationary my_stationary.launch.py
```

### Expected output

```
[FATAL] [<timestamp>] [<node>]: Failed to create TrossenArmDriver: \
  logger with name 'trossen_arm_driver' already exists
```
