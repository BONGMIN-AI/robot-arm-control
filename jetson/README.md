# Jetson AGX

This folder will contain high-level control code.

Planned responsibilities:

- ROS2 installation and workspace setup.
- High-level robot commands.
- Vision or AI model integration.
- Send target poses or joint commands to Raspberry Pi.

Before installing ROS2, record:

```bash
lsb_release -a
uname -m
cat /etc/nv_tegra_release
```

ROS2 distribution depends on the installed Ubuntu version.

