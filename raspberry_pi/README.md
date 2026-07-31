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

