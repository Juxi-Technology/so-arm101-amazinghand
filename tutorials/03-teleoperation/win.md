# Stage 3: Teleoperation (Windows)

This stage brings up the teleoperation loop: the leader arm controls the follower arm's motion, and the gripper controls the AmazingHand's open/close motion. This is the critical stage for verifying that the entire system works correctly.

---

## Prerequisites

- Completed [Stage 1: Environment Setup](../01-environment/win.md) and [Stage 2: Calibration](../02-calibration/win.md)
- All three devices are powered on and their serial ports have been recorded

---

## Running Teleoperation

```powershell
lerobot-teleoperate --robot.type=so101_amazing_hand --robot.port=<follower-port> --robot.hand_port=<hand-port> --robot.id=amazing_hand_follower --teleop.type=so101_leader --teleop.port=<leader-port> --teleop.id=amazing_hand_leader
```

> Replace `<follower-port>` / `<hand-port>` / `<leader-port>` with the actual COM port numbers on your machine (example: `COM58` / `COM11` / `COM54`).

**Expected behavior**:
- Leader arm 5 joints → follower arm follows
- Leader arm gripper → AmazingHand open/close (proportional following: half pinch = half close)

> **💡 Parameter notes:**
> - `--robot.type=so101_amazing_hand`: follower arm + hand combined robot
> - `--robot.port`: follower arm serial port
> - `--robot.hand_port`: hand serial port
> - `--teleop.type=so101_leader`: leader arm teleoperator
> - `--teleop.port`: leader arm serial port

---

## Must Do on First Run: Direction Check

After launching, first run a **direction test** to confirm that both of the following are correct:

| Test | Action | Correct behavior |
|---|---|---|
| Arm following | Rotate each leader arm joint | The follower arm follows in the same direction |
| Hand open/close | Open/close the leader arm gripper | Gripper open → hand open; gripper closed → hand closed |

> **⚠️ Note (if the direction is reversed):**
> - **Hand open/close direction reversed** (opening the gripper closes the hand instead): this means the hand angle calibration is inaccurate. Re-run the calibration tool (including the gripper direction calibration); changes take effect automatically once saved, and **no manual file edits are needed**. See [Stage 2: Calibration](../02-calibration/win.md).
> - **Gripper mapping direction reversed** (opening the gripper closes the hand instead): same as above — during calibration, click `[Capture Open]` while the leader gripper is **open** and `[Capture Close]` while it is **closed**. The tool records and saves `gripper_open_pos`/`gripper_close_pos` automatically, and loads them automatically at startup.
>
> After making the change, **re-run teleoperation** to verify.

---

## Proportional Following Check

Once the direction is correct, verify the fine-grained proportional response:
1. **Slowly** open the gripper → the hand should open **smoothly** (no jumps)
2. Stop the gripper **halfway** → the hand should also stop halfway
3. Open/close quickly → the hand responds quickly, without stuttering

> **⚠️ Note (past issue with excessive hand travel):** If the hand closes while the gripper is only half open, it is usually because the "open/fist" positions from hand angle calibration are inaccurate. Re-run calibration step 3 (hand angle GUI) to calibrate more precise open/close positions.

---

## Optional: Visualization with Cameras

Add `--robot.cameras` to connect cameras and `--display_data=true` to open the Rerun visualization window (showing camera images + joint states in real time):

```powershell
lerobot-teleoperate `
  --robot.type=so101_amazing_hand `
  --robot.port=<follower-port> `
  --robot.hand_port=<hand-port> `
  --robot.id=amazing_hand_follower `
  --teleop.type=so101_leader `
  --teleop.port=<leader-port> `
  --teleop.id=amazing_hand_leader `
  --robot.cameras='{
    wrist: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 30, fourcc: "MJPG"},
    top: {type: opencv, index_or_path: 1, width: 640, height: 480, fps: 30, fourcc: "MJPG"}
  }' `
  --display_data=true
```

> **💡 Note:**
> - `index_or_path` is the camera index; confirm it first with `lerobot-find-cameras` (indices differ between machines).
> - `fourcc: "MJPG"` is optional and can significantly reduce USB camera bandwidth usage (by switching to MJPEG compression); add it if you see stuttering.
> - If you only need one camera, just delete the corresponding line (e.g., `top`).

> **⚠️ Note (rerun dependency):** `--display_data=true` requires the rerun visualization package; if it is not installed, run:
> ```powershell
> pip install "rerun-sdk>=0.24.0,<0.34.0"
> ```
> It also requires the Rerun Viewer executable. On Windows, if you see `Failed to find Rerun Viewer executable`, the GUI viewer is missing. This **does not affect teleoperation**; simply remove `--display_data=true`.

---

## Exiting

Press `Ctrl+C` to stop. The program automatically:
1. Releases torque on the 8 hand servos
2. Disconnects the follower/leader arm serial ports
3. Disconnects the cameras (if any)

> **⚠️ Note:** **Do not close the terminal directly** before a clean exit, or the serial port may be left occupied. If a port stays occupied after an abnormal exit, replug the USB or restart the terminal process.

---

## Troubleshooting

| Symptom | Cause | Solution |
|---|---|---|
| Hand direction reversed | Hand angle or gripper mapping reversed | See "Direction check" above; swap the angles or adjust the mapping |
| Hand opens/closes too much or too little | Hand angle calibration inaccurate | Re-run the hand angle calibration (GUI) |
| Arm does not follow | Missing calibration / wrong serial port | Confirm the follower arm is calibrated and `--robot.port` is correct |
| rerun error | Visualization dependency missing | Remove `--display_data=true` |
| Serial port occupied | Previous abnormal exit | Close the process holding it or replug the USB |
