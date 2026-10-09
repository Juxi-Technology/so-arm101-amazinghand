# win

# Stage 3: Teleoperation (Windows)

This stage starts the teleoperation loop: the leader arm drives the follower arm's motion, and the gripper controls the AmazingHand's opening and closing. This is the key stage for verifying whether the whole system works correctly.

---

## Prerequisites

- Stage 1: Environment Setup and Stage 2: Calibration completed

- The three devices are powered on and their serial ports recorded

---

## Running Teleoperation

```PowerShell
lerobot-teleoperate --robot.type=so101_amazing_hand --robot.port=<follower-port> --robot.hand_port=<hand-port> --robot.id=amazing_hand_follower --teleop.type=so101_leader --teleop.port=<leader-port> --teleop.id=amazing_hand_leader
```

> Replace `<follower_arm_com>` / `<hand_com>` / `<leader_arm_com>` with your machine's actual COM numbers (examples `COM58` / `COM11` / `COM54`).

**Expected behavior**:

- The leader arm's 5 joints → the follower arm follows

- Leader arm gripper → AmazingHand opening/closing (proportional tracking: half pinch = half closed)

> **💡 Parameter notes**:

- `--robot.type=so101_amazing_hand`: follower arm \+ hand combined robot

- `--robot.port`: follower arm serial port

- `--robot.hand_port`: hand serial port

- `--teleop.type=so101_leader`: leader arm teleoperator

- `--teleop.port`: leader arm serial port

---

## Mandatory on First Run: Direction Verification

After starting, first do a **direction test** to confirm that both of the following are correct:

|Test|Operation|Correct behavior|
|---|---|---|
|Arm tracking|Rotate each joint of the leader arm|The follower arm follows in the same direction|
|Hand opening/closing|Open/pinch the leader arm gripper|Gripper open → hand open; gripper pinched → hand closed|

> **⚠️ Note (what to do if the direction is reversed)**:

- **Hand opening/closing direction reversed** (opening the gripper closes the hand instead): this means the hand angle calibration is inaccurate. Run the calibration tool again (including the gripper direction calibration); the change takes effect automatically once saved, with **no manual file editing needed**. See Stage 2: Calibration.

- **Gripper mapping direction reversed** (opening the gripper closes the hand instead): as above. During calibration, click `[Capture Open]` when the leader arm gripper is **open** and `[Capture Close]` when it is **pinched**; the tool records and saves `gripper_open_pos`/`gripper_close_pos` automatically and loads them at startup.

> After the change, **rerun teleoperation** to verify.

---

## Proportional Tracking Verification

Once the directions are correct, verify the smoothness of the ratio:

1. **Slowly** open the gripper → the hand should open **smoothly** (no jumps)

2. Stop the gripper **halfway** → the hand should also stop halfway

3. Open and close quickly → the hand responds quickly with no lag

> **⚠️ Note (the historical issue of the hand opening/closing too far)**: If the hand closes when the gripper is only half open, it is usually because the "open/clenched" positions were inaccurate during hand angle calibration. Rerun calibration step 3 (the hand angle GUI) to calibrate more precise open/close positions.

---

## Optional: Visualization with Cameras

Add `--robot.cameras` to connect cameras and `--display_data=true` to open a Rerun visualization window (showing camera images \+ joint states in real time):

```PowerShell
lerobot-teleoperate --robot.type=so101_amazing_hand --robot.port=<follower-port> --robot.hand_port=<hand-port> --robot.id=amazing_hand_follower --teleop.type=so101_leader --teleop.port=<leader-port> --teleop.id=amazing_hand_leader --robot.cameras='{wrist: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 30, fourcc: "MJPG"},top: {type: opencv, index_or_path: 1, width: 640, height: 480, fps: 30, fourcc: "MJPG"}}' --display_data=true
```

> **💡 Notes**:

- `index_or_path` is the camera index; confirm it first with `lerobot-find-cameras` (the numbering differs across machines).

- `fourcc: "MJPG"` is optional and can significantly reduce USB camera bandwidth usage (by switching to MJPEG compression); add it if you see stuttering.

- If you only need one camera, just delete the corresponding line (e.g. `top`).

> **⚠️ Note (rerun dependency)**: `--display_data=true` requires the rerun visualization package; if it is not installed, run:

```PowerShell
pip install "rerun-sdk>=0.24.0,<0.34.0"
```

> The Rerun Viewer executable is required. On Windows, if you get `Failed to find Rerun Viewer executable`, the GUI viewer is missing. **This does not affect teleoperation**; just remove `--display_data=true`.

---

## Exiting

Press `Ctrl+C` to stop. The program automatically:

1. Releases torque on the 8 hand servos

2. Disconnects the follower arm / leader arm serial ports

3. Disconnects the cameras (if any)

> **⚠️ Note**: **Do not close the terminal directly** before exiting normally, otherwise a serial port lock may be left behind. If the port is occupied after an abnormal exit, replug the USB cable or restart the terminal process.

---

## Troubleshooting

|Symptom|Cause|Solution|
|---|---|---|
|Hand direction reversed|Hand angles or gripper mapping reversed|See "Direction Verification" above; swap the angles or adjust the mapping|
|Hand opens/closes too far / not enough|Hand angle calibration inaccurate|Recalibrate the hand angle GUI|
|Arm does not follow|Missing calibration / wrong serial port|Confirm the follower arm is calibrated and `--robot.port` is correct|
|rerun error|Visualization dependency missing|Remove `--display_data=true`|
|Serial port occupied|Previous abnormal exit|Close the process holding it or replug the USB cable|

