# Safety Notes

## Current Risk

`J1` carries the highest load. It has already entered overload protection once and recovered after power cycling.

## First-Pass Rules

- Do not jump directly to target angles.
- Move in small interpolated steps.
- Keep forward-reaching poses brief.
- Return to home between calibration measurements.
- Keep one hand near power shutoff during early tests.
- Recheck servo temperature after high-load poses.

## Initial Joint Limits

These are conservative first-pass limits, not final mechanical limits.

| Joint | Initial range |
| --- | --- |
| `J0` | `120..180` |
| `J1` | `150..185` |
| `J2` | `130..200` |
| `J3` | `130..200` |
| `J4` | `0..300` |
| `J5` | gripper event range `0..150` |

## Power

- Servo power should be separate from Raspberry Pi or Jetson logic power.
- Grounds must be common.
- Confirm each servo supports the supplied voltage.
- If a servo stops responding after load, check for overload, over-temperature, or low-voltage protection.
