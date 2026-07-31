# Calibration Notes

## Hardware

- Servo count: 6
- `J0`: base yaw
- `J1`: shoulder pitch
- `J2`: elbow pitch
- `J3`: wrist pitch
- `J4`: gripper roll
- `J5`: gripper open/close
- Servo range note: 300 deg range, center at 150 deg

## Dimensions

All values are approximate millimeters.

| Name | Meaning | Value |
| --- | --- | ---: |
| `B0` | floor/table to J0 rotation center | 85 |
| `H0` | J0 rotation center to J1 axis center | 49 |
| `L1` | J1 axis center to J2 axis center | 109 |
| `L2` | J2 axis center to J3 axis center | 109 |
| `L3` | J3 axis center to J4 axis center | 63 |
| `L4` | J4 axis center to gripper center/tool point | 104 |

## Coordinate Convention

- Origin: base center projected onto the floor/table
- `x`: left/right
- `y`: forward
- `z`: height from floor/table

## Direction Convention

- `J0`: plus is counterclockwise
- `J1`: plus leans forward
- `J2`: plus leans forward
- `J3`: plus leans forward
- `J4`: plus is counterclockwise roll
- `J5`: gripper open/close, excluded from position kinematics

## Measurements

| Pose | Servo Angles `J0 J1 J2 J3 J4` | Predicted `x y z` | Measured `x y z` | Note |
| --- | --- | --- | --- | --- |
| A | `150 150 150 150 150` | `0 0 519` | `0 17 518` | gripper center |
| B | `150 180 180 150 150` | `0 293.5 366.4` | `0 325 325` | J1 load sag likely |
| G1 | `150 180 150 150 150` | `0 192.5 467.4` | `0 205 454` | J1 load sag |
| G2 | `180 180 150 150 150` | `-96.2 166.7 467.4` | `-95 179 454` | J0 verified |
| G3 | `120 180 150 150 150` | `96.2 166.7 467.4` | `98 173 454` | J0 verified |
| E1 | `150 150 170 150 150` | `0 94.4 502.4` | `0 85 503` | J2 |
| E2 | `150 150 180 150 150` | `0 138.0 482.0` | `0 135 485` | J2 |
| E3 | `150 150 190 150 150` | `0 177.4 454.4` | `0 187 445` | J2 |
| F1 | `150 150 150 170 150` | `0 57.1 508.9` | `0 59 512` | J3 |
| F2 | `150 150 150 180 150` | `0 83.5 496.6` | `0 77 501` | J3 |
| F3 | `150 150 150 190 150` | `0 107.3 479.9` | `0 91 485` | J3 |

## Current Findings

- `J0` rotation is consistent after re-measurement.
- `J2` and `J3` are close enough for first-pass forward kinematics.
- `J1` is the highest-load joint and can sag under load.
- `J1` entered overload protection once and recovered after power cycling.
- Keep forward-reaching poses brief until torque/current/temperature behavior is understood.

## Next Steps

1. Add safe motion interpolation.
2. Add joint limit configuration.
3. Add inverse kinematics for target `x y z`.
4. Add Raspberry Pi servo driver code.
5. Install ROS2 on Jetson AGX after confirming Jetson Ubuntu version.

