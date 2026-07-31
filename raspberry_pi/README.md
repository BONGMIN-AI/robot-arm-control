# Raspberry Pi Control

This folder will contain low-level servo control code.

Planned responsibilities:

- Send servo angle commands.
- Read current servo positions if supported.
- Apply joint limits.
- Move through interpolated steps instead of jumping directly to target angles.
- Handle gripper open/close on `J5`.

Safety notes:

- Use a separate servo power supply.
- Share ground with Raspberry Pi.
- Do not power multiple servos directly from Raspberry Pi 5V.
- Move `J1` slowly because it carries the highest load.

## Hardware

- Servo: DYNAMIXEL AX-12A
- Protocol: DYNAMIXEL Protocol 1.0
- Bus: 3-pin TTL Half-Duplex UART
- Servo IDs: `J0=0`, `J1=1`, `J2=2`, `J3=3`, `J4=4`, `J5=5`
- Control method: packet communication, not PWM

## Principle

The Python controller sends Protocol 1.0 packets to each servo ID:

1. Open the serial port.
2. Enable torque on IDs `0..5`.
3. Set a safe moving speed.
4. Generate interpolated poses.
5. Send each servo goal position step by step.
6. Close the serial port.

AX-12A position units are `0..1023` for `0..300 deg`.

## Raspberry Pi Setup

```bash
python3 -m pip install dynamixel-sdk
```

Typical device names:

```bash
/dev/ttyUSB0
/dev/ttyAMA0
/dev/ttyS0
```

## Dry Run

Run without moving hardware:

```bash
python3 raspberry_pi/move_once.py 150 180 180 150 150 150 --step 10 --mock
```

## Real Move

Use only after confirming power, wiring, IDs, and emergency stop:

```bash
python3 raspberry_pi/move_once.py 150 180 180 150 150 150 --device /dev/ttyUSB0 --step 2 --delay 0.05 --speed 80
```
