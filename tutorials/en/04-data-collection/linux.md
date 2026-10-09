# linux

# Stage 4: Data Collection (Linux)

This stage records a teleoperation dataset: under manual control, it collects "joint angle \+ camera image" samples for later training. The dataset quality directly determines the policy's performance, so **your operation must be consistent and standardized**. This stage is **recorded entirely locally, with no HF login required**.

---

## Prerequisites

- Stage 3: Teleoperation completed and the direction verified as correct

- Cameras connected and their indices recorded (`lerobot-find-cameras`)

- A local dataset storage path decided (`~/lerobot_data` is used as the example here; you can customize it)

---

## Step 1: Confirm the Camera Indices

```Bash
lerobot-find-cameras
```

Record the camera numbers. For example:

- Camera 0: wrist camera (wrist)

- Camera 1: top camera (top)

> **⚠️ Note (camera index)**: `index_or_path` is the camera index (0/1/2\.\.\.) or a video stream path. The numbering differs across computers, so be sure to confirm it first.

---

## Step 2: Record the Dataset (saved locally, no login required)

```Bash
lerobot-record \
  --robot.type=so101_amazing_hand \
  --robot.port=<follower-port> \
  --robot.hand_port=<hand-port> \
  --robot.id=amazing_hand_follower \
  --robot.cameras='{
    wrist: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 30, fourcc: "MJPG"},
    top: {type: opencv, index_or_path: 1, width: 640, height: 480, fps: 30, fourcc: "MJPG"}
  }' \
  --teleop.type=so101_leader \
  --teleop.port=<leader-port> \
  --teleop.id=amazing_hand_leader \
  --dataset.repo_id=soarm_amazing_hand_pick \
  --dataset.root=~/lerobot_data \
  --dataset.push_to_hub=false \
  --dataset.num_episodes=20 \
  --dataset.single_task="Pick up the cube with the dexterous hand" \
  --display_data=true
```

> Replace `<follower_arm_port>` / `<hand_port>` / `<leader_arm_port>` with the actual paths; replace the camera `index_or_path` with your camera indices.

> **💡 Notes**:

- `--dataset.root=~/lerobot_data`: The dataset is saved to the specified **local path**, with **no HF login required** (if omitted, it is saved by default to `~/.cache/huggingface/lerobot/datasets/...`).

- `--dataset.push_to_hub=false`: **Disables upload** (by default it tries to push to HF, which requires login). Only change it to `true` if you need to share the dataset.

- `--dataset.repo_id=soarm_amazing_hand_pick`: The dataset name; reference it with the **same name** during training.

- `--display_data=true` requires rerun (`pip install "rerun-sdk>=0.24.0,<0.34.0"` if not installed) and a graphical environment, or omit this parameter (recording is unaffected).

---

## Parameter Reference

|Parameter|Description|
|---|---|
|`--robot.cameras`|Camera configuration. `index_or_path` is the camera index; `width/height/fps` are **required**|
|`--dataset.repo_id`|Dataset name (used as the local identifier)|
|`--dataset.root`|Local dataset storage path. **Required for purely local recording**, to avoid an uncontrollable default path|
|`--dataset.push_to_hub`|`false`=local only (recommended default); `true`=push to HF (login required)|
|`--dataset.num_episodes`|Number of episodes to record|
|`--dataset.episode_time_s`|**Maximum seconds per episode** (default 60). If the task finishes early, press Enter to end early; otherwise it ends automatically when the time is up|
|`--dataset.single_task`|Task description, written into the dataset metadata|
|`--display_data=true`|Display the recording view in real time (optional)|

---

## Recording Best Practices

**Per-episode procedure**:

1. Return the robot arm \+ hand to the **starting position**

2. Press Enter in the terminal to start recording

3. Operate the leader arm to perform the task (e.g. picking up the cube); **move slowly and consistently**

4. Press Enter to end the episode when the task is complete (**if you don't press it, recording lasts at most 60 seconds**, controlled by `--dataset.episode_time_s`, and ends automatically when the time is up)

5. Repeat until `num_episodes` is reached

> **⚠️ Note 1 (consistent starting position)**: Start every episode from the **same starting position** to avoid a messy data distribution. It is recommended to fix a single reset pose.

> **⚠️ Note 2 (consistent motion)**: Use a similar motion trajectory for the same task (approach angle, grasp position, speed); the policy learns faster and more reliably.

> **⚠️ Note 3 (recording quality)**: It is better to record fewer high-quality episodes than a large number of messy samples. 20 episodes is the starting point for ACT; 30\-50 episodes are recommended for complex tasks.

> **⚠️ Note 4 (camera real-time behavior)**: During recording, avoid occluding the cameras and avoid strong light changes; image consistency affects generalization.

---

## Data Storage

- **Local recording**: The data is saved in the directory specified by `--dataset.root` (example `~/lerobot_data/soarm_amazing_hand_pick`).

- **Training reference**: During training, just use the **same ****`--dataset.repo_id`**** \+ ****`--dataset.root`**; there is no need to move files manually:

```Bash
lerobot-train --dataset.repo_id=soarm_amazing_hand_pick --dataset.root=~/lerobot_data ...
```

- **HF login scenario** (optional): To share the dataset to the cloud, change it to `--dataset.push_to_hub=true` (requires `huggingface-cli login`). Purely local training **does not need it**.

> **⚠️ Note (local vs cloud)**: The default tutorial is entirely local, and `--dataset.push_to_hub=false` ensures that HF login is not triggered. Add `true` only if you want to share the dataset.

---

## Step 3: Replay Verification (optional but recommended)

After recording is complete, you can use `lerobot-replay` to replay a specific episode and verify **the data quality \+ whether the robot's recorded motions are correct**. During replay, the robot automatically reproduces that episode's motions (including the hand's opening and closing).

```Bash
lerobot-replay \
  --robot.type=so101_amazing_hand \
  --robot.port=<follower-port> \
  --robot.hand_port=<hand-port> \
  --robot.id=amazing_hand_follower \
  --dataset.repo_id=soarm_amazing_hand_pick \
  --dataset.root=~/lerobot_data \
  --dataset.episode=0
```

> Replace `<follower_arm_port>` / `<hand_port>` with the actual paths; `--dataset.episode` is the index of the episode to replay (**starting from 0**; if you recorded 20 episodes, use `0`\~`19`).

> **💡 Notes**: Before replaying, **move the follower arm \+ hand back to the starting position** to avoid motion conflicts; the robot moves on its own during replay, so **do not intervene manually**. If the replayed motions differ noticeably from the recording, the data quality is problematic and you should rerecord that episode.

---

Once this stage is complete, proceed to Stage 5: Model Training.

---

## Troubleshooting

|Symptom|Cause|Solution|
|---|---|---|
|Camera not found|Wrong index / permissions / missing driver|Confirm with `lerobot-find-cameras`; check `/dev/video*` permissions (join the `video` group)|
|Recording interrupted|Serial port timeout|Confirm the three devices' serial ports are not occupied, then retry|
|Image all black / garbled|Wrong camera configuration|Check `index_or_path`/`fps`|
|No permission for `/dev/video*`|User not in the video group|`sudo usermod -a -G video $USER`, then log in again|
|Dataset is empty|Recording not done correctly|Confirm you pressed Enter to start/end each episode|

