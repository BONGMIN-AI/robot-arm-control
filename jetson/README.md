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

Current Jetson:

```text
Ubuntu 22.04.5 LTS jammy
aarch64
L4T R36.4.3
```

Recommended ROS2 distribution:

```text
ROS2 Humble
```

## Test Without ROS2

Jetson can run the same AX-12A test code as Raspberry Pi if a DYNAMIXEL TTL adapter is connected.

Dry run:

```bash
python3 raspberry_pi/move_once.py 150 180 180 150 150 150 --step 10 --mock
```

Install SDK:

```bash
python3 -m pip install dynamixel-sdk
```

Check serial ports:

```bash
ls /dev/ttyUSB*
ls /dev/ttyACM*
ls /dev/ttyTHS*
```

Real move example:

```bash
python3 raspberry_pi/move_once.py 150 180 180 150 150 150 --device /dev/ttyUSB0 --step 2 --delay 0.05 --speed 80
```

## ROS2 Humble Troubleshooting

If `sudo apt install ros-humble-desktop` fails with held or broken packages, collect:

```bash
sudo apt update
apt-mark showhold
apt-cache policy ros-humble-desktop
apt-cache policy libignition* gz-* gazebo*
sudo apt --fix-broken install
sudo dpkg --configure -a
```

Try the smaller install first:

```bash
sudo apt install ros-humble-ros-base ros-dev-tools
```

If `ros-base` works but `desktop` fails, the issue is usually GUI/simulation dependency conflict. `ros-base` is enough for robot control nodes.
