# Stage 2: Calibration (Windows)

This stage calibrates three devices: the leader arm, the follower arm, and the AmazingHand. Calibration is a prerequisite for correct teleoperation — **you must complete this stage before moving on to teleoperation**.

> **Calibration order:** leader arm → follower arm + hand → hand angles. Every step requires **terminal interaction** (physical manipulation + key presses).
>
> **⚠️ General reminder:** The serial port arguments in the commands on this page are **example placeholders** — you must replace them with the actual COM port numbers for your machine (see the ports recorded in [Stage 1](../01-environment/win.md)).

---

## Prerequisites

- Completed [Stage 1: Environment Setup](../01-environment/win.md)
- The conda environment `lerobot` is activated
- Serial ports for all three devices are recorded
- Devices are powered on with independent power supplies

---

## Step 1: Calibrate the Leader Arm

```powershell
lerobot-calibrate `
  --teleop.type=so101_leader --teleop.port=<leader-port> --teleop.id=amazing_hand_leader
```

> Replace `<leader-port>` with the actual COM port number for your machine (example: `COM54`).

**Interactive steps:**
1. Move **all joints of the leader arm to the middle position**, then press Enter
2. **Push each joint in turn through its maximum/minimum range**, then press Enter

**Verification:** The calibration file is saved automatically to
`C:\Users\<username>\.cache\huggingface\lerobot\calibration\teleoperators\so_leader\amazing_hand_leader.json`

> **⚠️ Note 1 (gripper must be calibrated):** The range of gripper servo #6 serves as the normalization reference for `gripper.pos` (0-100). Be sure to push the gripper from fully open to fully closed and calibrate it properly; otherwise the hand's open/close ratio will be distorted later.
>
> **⚠️ Note 2 (free movement):** During calibration, the arm must be able to move freely — make sure the servos are unloaded.
>
> **⚠️ Note 3 (calibration file location):** On Windows, the path is under your user profile: `%USERPROFILE%\.cache\huggingface\lerobot\calibration\`.

---

## Step 2: Calibrate the Follower Arm (with the hand connected)

```powershell
lerobot-calibrate `
  --robot.type=so101_amazing_hand --robot.port=<follower-port> --robot.hand_port=<hand-port> --robot.id=amazing_hand_follower
```

> Replace `<follower-port>` / `<hand-port>` with the actual COM port numbers (example: `COM58` / `COM11`).

**Interactive steps:**
1. Move the follower arm's **5 joints** (no joint #6) to the middle position, then press Enter
2. Move each joint through its full range of motion, then press Enter

**Verification:** The calibration file is saved to
`C:\Users\<username>\.cache\huggingface\lerobot\calibration\robots\so101_amazing_hand\amazing_hand_follower.json`

> **⚠️ Note 1 (hand torque enabled automatically):** When this command connects, it **automatically enables torque on all 8 hand servos** (the log shows `enabling AmazingHand torque`). The hand will open when calibration finishes — this is normal.
>
> **⚠️ Note 2 (no hand GUI is launched):** Hand angles do **not** use lerobot's `RangeFinderGUI`; this step is complete as soon as follower-arm calibration ends. Hand angles are handled by the dedicated tool in Step 3.
>
> **⚠️ Note 3 (serial port in use):** This step occupies the hand's serial port. Do **not** run other processes that use that port at the same time.

---

## Step 3: Calibrate Hand Angles + Gripper Direction (dedicated GUI)

```powershell
lerobot-calibrate-amazing-hand --hand_port <hand-port> --leader_port <leader-port>
```

> Replace `<hand-port>` / `<leader-port>` with the actual COM port numbers (example: `COM11` / `COM54`). `--leader_port` is used to calibrate the **gripper direction** at the same time (see below).

**GUI steps:**
1. Drag the four finger sliders (index/middle/ring/thumb) to make the hand **fully open**, then click **`Save Open`**
2. Drag the sliders to make the hand **fully clenched into a fist**, then click **`Save Close`**
3. **Open the leader arm's gripper**, then click **`Capture Open`** (the GUI shows `gripper.pos` in real time; it should be close to 100 when open)
4. **Pinch the leader arm's gripper closed**, then click **`Capture Close`** (it should be close to 0 when pinched shut)
5. **Auto-save:** once all four values are set, a green banner `AUTO-SAVED to ...\hand_angles.json` appears at the top of the window, and the terminal prints the path as well
6. Close the window (the hand's torque is released automatically)

**Verification:** The angle and gripper mapping is saved to
`C:\Users\<username>\.cache\huggingface\lerobot\calibration\robots\so101_amazing_hand\hand_angles.json`

> **⚠️ Note 1 (this step is mandatory):** **You must run this step on every new computer and for every hand.** The angles in the config are AmazingHand's official generic defaults and serve only as a fallback; when `hand_angles.json` exists, your measured values are preferred. Skipping this calibration may lead to the wrong open/close direction or range.
>
> **⚠️ Note 2 (loaded automatically):** Every time the robot starts, it reads `hand_angles.json` (including `gripper_open_pos`/`gripper_close_pos`) to override the config defaults — **no code changes required**. The gripper direction varies from one leader arm to another, so a one-time calibration is enough.
>
> **⚠️ Note 3 (slider semantics):** Moving a slider toward `+` drives that finger's m1 toward `+angle` and m2 toward `-angle` (mirrored). Judge open vs. clenched by the **hand's actual pose**; there is no need to focus on the angle values.
>
> **⚠️ Note 4 (precise calibration):** When calibrating the "fully open" position, do not overextend (fingers skewing or splaying apart); for "fully clenched", do not over-squeeze (which keeps the servos under constant pressure). Otherwise the open/close motion will overshoot during teleoperation.
>
> **⚠️ Note 5 (Capture order):** `Capture Open` / `Capture Close` correspond to the **leader arm's gripper** opening/closing, not the hand's fingers. If the hand opens in the wrong direction, it is most likely that this was captured backwards or the hand angles were calibrated backwards; simply recalibrate.
>
> **⚠️ Note 6 (GUI does not open):** Make sure `pygame` is installed (it is included in the `amazinghand` extra). If it still does not open, check whether a graphical desktop environment is available.

---

## Recalibration

If you only need to recalibrate part of the setup:
- **Hand only** → run Step 3 only
- **Follower arm only** → run Step 2 only (this also enables hand torque as a side effect)
- **Full recalibration** → Steps 1 → 2 → 3

> **⚠️ Note:** Steps 2 and 3 **cannot be run at the same time** (both occupy the hand's serial port).

---

Once this stage is complete, proceed to [Stage 3: Teleoperation](../03-teleoperation/win.md).

---

## Troubleshooting

| Symptom | Cause | Solution |
|---|---|---|
| Leader arm calibration reports a 2307 model error | Arm bus contaminated / serial port conflict | Confirm the hand's serial port is not connected at the same time; this project avoids this by driving the hand over rustypot |
| No GUI is launched when calibrating the hand | Wrong command used | You must use `lerobot-calibrate-amazing-hand` (not `lerobot-calibrate`) |
| Hand driver reports `Operation timed out` | Serial port busy / timing | Confirm the hand's serial port is not in use, then retry |
| Calibration file not found | Wrong path | Check `%USERPROFILE%\.cache\huggingface\lerobot\calibration\` |
| Serial port cannot be opened | Wrong COM number | Use `lerobot-find-port` to reconfirm |
