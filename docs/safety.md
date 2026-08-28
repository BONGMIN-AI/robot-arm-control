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

## Configured Joint Limits

These limits match `kinematics/joint_config.py` and the URDF model. Saved
teaching poses outside these ranges require the explicit `--allow-unsafe`
override and should only be replayed after hardware clearance is confirmed.

| Joint | Configured range |
| --- | --- |
| `J0` | `0..300` |
| `J1` | `50..250` |
| `J2` | `0..300` |
| `J3` | `0..300` |
| `J4` | `0..300` |
| `J5` | `0..150` |

## Power

- Servo power should be separate from Raspberry Pi or Jetson logic power.
- Grounds must be common.
- Confirm each servo supports the supplied voltage.
- If a servo stops responding after load, check for overload, over-temperature, or low-voltage protection.
