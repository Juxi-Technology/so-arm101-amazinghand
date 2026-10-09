# win

# Stage 2: Calibration (Windows)

This stage calibrates the three devices: the leader arm, the follower arm, and the AmazingHand hand. Calibration is a prerequisite for correct teleoperation, so **you must complete this stage before moving on to teleoperation**.

> **Calibration order**: leader arm → follower arm \+ hand → hand angles. Every step requires **terminal interaction** (physical manipulation \+ key presses).

> **⚠️ General reminder**: The serial port parameters in this page's commands are **example placeholders** and must be replaced with your machine's actual COM number (see the ports recorded in Stage 1).

---

## Prerequisites

- Stage 1: Environment Setup completed

- The conda environment `lerobot` is activated

```Plain Text
# Activate the environment
conda activate lerobot

# Enter the lerobot directory
cd ../lerobot
```

- The serial ports of the three devices are recorded

- The devices are powered on with independent power supplies

---

## Step 1: Calibrate the Leader Arm

```PowerShell
lerobot-calibrate --teleop.type=so101_leader --teleop.port=<leader-port> --teleop.id=amazing_hand_leader
```

> Replace `<leader_arm_com>` with your machine's actual COM number (example `COM54`).

**Interactive steps**:

1. Move **all joints of the leader arm to the middle position**, then press Enter

2. Push **each joint in turn to its maximum/minimum range**; press Enter when done

**Verification**: The calibration file is saved automatically to
`C:\Users\<username>\.cache\huggingface\lerobot\calibration\teleoperators\so_leader\amazing_hand_leader.json`

> **⚠️ Note 1 (the gripper must be calibrated)**: The range of gripper servo #6 serves as the normalization reference for `gripper.pos` (0\~100). Make sure to push the gripper from fully open to fully closed and calibrate it properly, otherwise the hand's opening/closing ratio will be distorted later.

> **⚠️ Note 2 (free movement)**: During calibration, the arm must be able to move freely; make sure the servos are unloaded.

> **⚠️ Note 3 (calibration file location)**: On Windows the path is the user directory `%USERPROFILE%\.cache\huggingface\lerobot\calibration\`.

---

## Step 2: Calibrate the Follower Arm (with the hand connected)

```PowerShell
lerobot-calibrate --robot.type=so101_amazing_hand --robot.port=<follower-port> --robot.hand_port=<hand-port> --robot.id=amazing_hand_follower
```

> Replace `<follower_arm_com>` / `<hand_com>` with the actual COM numbers (examples `COM58` / `COM11`).

**Interactive steps**:

1. Move the **5 joints** of the follower arm (there is no #6) to the middle position, then press Enter

2. Sweep each joint through its full range, then press Enter

**Verification**: The calibration file is saved to
`C:\Users\<username>\.cache\huggingface\lerobot\calibration\robots\so101_amazing_hand\amazing_hand_follower.json`

> **⚠️ Note 1 (hand torque is enabled automatically)**: When this command connects, it **automatically enables torque on the 8 hand servos** (the log shows `enabling AmazingHand torque`). The hand opens when calibration finishes; this is normal.

> **⚠️ Note 2 (no hand GUI pops up)**: Hand angles do **not** use lerobot's `RangeFinderGUI`; the follower arm calibration ends when it finishes. Hand angles are handled by the dedicated tool in step 3.

> **⚠️ Note 3 (serial port occupancy)**: This step occupies the hand's serial port. **Do not** run other processes that use that port at the same time.

---

## Step 3: Calibrate the Hand Angles \+ Gripper Direction (dedicated GUI)

```PowerShell
lerobot-calibrate-amazing-hand --hand_port <hand-port> --leader_port <leader-port>
```

> Replace `<hand_com>` / `<leader_arm_com>` with the actual COM numbers (examples `COM11` / `COM54`). `--leader_port` is used to calibrate the **gripper direction** in sync (see below).

**GUI steps**:

1. Drag the four finger sliders (index/middle/ring/thumb) so the hand is **fully open**, then click **`Save Open`**

2. Drag the sliders so the hand is **fully clenched**, then click **`Save Close`**

3. **Open the leader arm gripper**, then click **`Capture Open`** (the GUI displays `gripper.pos` in real time; it should be close to 100 when open)

4. **Pinch the leader arm gripper closed**, then click **`Capture Close`** (it should be close to 0 when pinched)

5. **Auto-save**: Once all four values are set, a green banner `AUTO-SAVED to ...\hand_angles.json` appears at the top of the window, and the terminal prints the path as well

6. Close the window (the hand's torque is released automatically)

**Verification**: The angles and gripper mapping are saved to
`C:\Users\<username>\.cache\huggingface\lerobot\calibration\robots\so101_amazing_hand\hand_angles.json`

> **⚠️ Note 1 (calibration is mandatory)**: **This step must be performed on every new computer / every hand**. The angles in the config are AmazingHand's official generic defaults and serve only as a fallback; when `hand_angles.json` exists, your measured values are loaded in preference. Skipping calibration may cause the opening/closing direction or range to be wrong.

> **⚠️ Note 2 (automatic loading)**: Each time the robot starts, it reads `hand_angles.json` (containing `gripper_open_pos`/`gripper_close_pos`) to override the config defaults; **no code changes are needed**. The gripper direction varies with the leader arm, so calibrating once is enough.

> **⚠️ Note 3 (slider semantics)**: Moving a slider toward `+` drives that finger's m1 toward `+angle` and m2 toward `-angle` (mirrored). Judge open/clenched by **the hand's actual pose**; you do not need to pay attention to the angle values.

> **⚠️ Note 4 (precise calibration)**: Do not overdo "fully open" (fingers slanting/spreading) or over-squeeze "fully clenched" (servos under continuous pressure). Otherwise the opening/closing will overshoot during teleoperation.

> **⚠️ Note 5 (Capture order)**: `Capture Open` / `Capture Close` correspond to the opening/closing of the **leader arm gripper**, not the hand's fingers. If the hand opens in the wrong direction, it is most likely that this was calibrated backwards or the hand angles were calibrated backwards; just recalibrate.

> **⚠️ Note 6 (GUI won't open)**: Confirm that `pygame` is installed (it is included in the `amazinghand` extra). If it still won't open, check whether a graphical desktop environment is available.

---

## Recalibration

When you only need to recalibrate one part:

- **Hand only** → run step 3 only

- **Follower arm only** → run step 2 only (it also enables hand torque along the way)

- **Recalibrate everything** → steps 1 → 2 → 3

> **⚠️ Note**: Steps 2 and 3 **cannot run at the same time** (both occupy the hand's serial port).

---

Once this stage is complete, proceed to Stage 3: Teleoperation.

---

## Troubleshooting

|Symptom|Cause|Solution|
|---|---|---|
|Leader arm calibration reports a 2307 model error|Arm bus polluted / serial port conflict<br>|Confirm the hand's serial port is not connected at the same time; in this project the hand uses rustypot, which avoids this|
|No GUI pops up for hand calibration|Wrong command used|You must use `lerobot-calibrate-amazing-hand` (not `lerobot-calibrate`)|
|Hand driver reports `Operation timed out`|Serial port busy / timing|Confirm the hand's serial port is not occupied, then retry|
|Calibration file not found|Wrong path<br>|Check `%USERPROFILE%\.cache\huggingface\lerobot\calibration\`|
|Serial port won't open|Wrong COM number|Reconfirm with `lerobot-find-port`|

