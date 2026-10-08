# Stage 4: Data Collection (Linux)

In this stage you record a teleoperation dataset — samples of "joint angles + camera images" collected under manual control, for later training. Dataset quality directly determines policy performance, so **operate in a disciplined and consistent manner**. This stage records **entirely locally — no HF login required**.

---

## Prerequisites

- [Stage 3: Teleoperation](../03-teleoperation/linux.md) completed, with directions verified
- Cameras connected and their indexes recorded (`lerobot-find-cameras`)
- Local dataset storage path decided (this document uses `~/lerobot_data` as the example; you can choose your own)

---

## Step 1: Confirm the Camera Indexes

```bash
lerobot-find-cameras
```

Note the camera numbers. For example:
- No. 0: wrist camera (wrist)
- No. 1: top camera (top)

> **⚠️ Note (camera index):** `index_or_path` is the camera index (0/1/2...) or a video stream path. The numbering differs from computer to computer, so always confirm it first.

---

## Step 2: Record the Dataset (Save Locally, No Login Required)

```bash
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

> Replace `<follower-port>` / `<hand-port>` / `<leader-port>` with the actual device paths; replace the camera `index_or_path` values with your camera indexes.
>
> **💡 Note:**
> - `--dataset.root=~/lerobot_data`: saves the dataset to the specified **local path** — **no HF login required** (if omitted, it defaults to `~/.cache/huggingface/lerobot/datasets/...`).
> - `--dataset.push_to_hub=false`: **disables upload** (by default it tries to push to HF, which requires login). Change it to `true` only when you want to share the dataset.
> - `--dataset.repo_id=soarm_amazing_hand_pick`: dataset name; reference it with the **same name** during training.
> - `--display_data=true` requires rerun (if not installed: `pip install "rerun-sdk>=0.24.0,<0.34.0"`) and a graphical environment, or drop the parameter (recording is unaffected).

---

## Parameters

| Parameter | Description |
|---|---|
| `--robot.cameras` | Camera configuration. `index_or_path` is the camera index; `width/height/fps` are **required** |
| `--dataset.repo_id` | Dataset name (used as the local identifier) |
| `--dataset.root` | Local dataset storage path. **Required for purely local recording** — avoids the default path being out of your control |
| `--dataset.push_to_hub` | `false` = local only (recommended default); `true` = push to HF (requires login) |
| `--dataset.num_episodes` | Number of episodes to record |
| `--dataset.episode_time_s` | **Maximum seconds recorded per episode** (default 60). Press Enter to end the episode early once the task is complete; otherwise the episode ends automatically when the time is up |
| `--dataset.single_task` | Task description, written into the dataset metadata |
| `--display_data=true` | Show the live recording view (optional) |

---

## Recording Guidelines

**Per-episode procedure:**
1. Reset the robot arm + hand to the **initial position**
2. Press Enter in the terminal to start recording
3. Operate the leader arm to perform the task (e.g. pick up the cube) — **move slowly and consistently**
4. Press Enter to end the episode once the task is complete (**if you don't, it records for up to 60 seconds**, controlled by `--dataset.episode_time_s`; the episode ends automatically when time is up)
5. Repeat until `num_episodes` is reached

> **⚠️ Note 1 (consistent initial position):** Start every episode from the **same initial position** to avoid a messy data distribution. Fixing one reset pose is recommended.
>
> **⚠️ Note 2 (consistent motions):** For the same task, use a similar motion trajectory (approach angle, grasp location, speed) — the policy learns faster and more stably.
>
> **⚠️ Note 3 (recording quality):** Prefer a few high-quality episodes over a large batch of messy samples. 20 episodes is the starting point for ACT; 30-50 episodes are recommended for complex tasks.
>
> **⚠️ Note 4 (camera consistency):** During recording, avoid occluding the cameras and strong lighting changes — image consistency affects generalization.

---

## Data Storage

- **Local recording**: data is saved under the directory specified by `--dataset.root` (example: `~/lerobot_data/soarm_amazing_hand_pick`).
- **Referencing for training**: for training, simply use the **same `--dataset.repo_id` + `--dataset.root`** — no need to move files manually:
  ```bash
  lerobot-train --dataset.repo_id=soarm_amazing_hand_pick --dataset.root=~/lerobot_data ...
  ```
- **HF upload scenario** (optional): see [Optional: Upload the Dataset to Hugging Face](#optional-upload-the-dataset-to-hugging-face) below.

> **⚠️ Note (local vs cloud):** By default this tutorial stays fully local — `--dataset.push_to_hub=false` ensures HF login is never triggered. Add `true` only when you want to share the dataset.

---

## Optional: Upload the Dataset to Hugging Face

To share the dataset to the cloud (multi-user / multi-machine training, or handing it off to your team), follow the steps below. **Skip this section if you train locally only.**

### 1. Log In

Activate the lerobot environment first, then log in (the new Hugging Face CLI uses the `hf` command, no longer `huggingface-cli`):

```bash
hf auth login
```

Paste a **Write**-permission token generated at https://huggingface.co/settings/tokens, then verify:

```bash
hf auth whoami
```

### 2. Enable Upload During Recording

In the recording command from [Step 2](#step-2-record-the-dataset-save-locally-no-login-required), make two changes:

```bash
--dataset.repo_id=<your-hf-username-or-org>/soarm_amazing_hand_pick \
--dataset.push_to_hub=true \
--dataset.private=true \
```

> **⚠️ Note 1 (organization name):** When uploading under an enterprise/organization, use the **organization name** in `repo_id` (not your personal username), and your account must be a member with write permission in that organization. When uploading under your personal account, use your username instead.
>
> **⚠️ Note 2 (network):** Direct connections to `huggingface.co` from mainland China often time out. **Mirrors such as hf-mirror.com only support downloads, not uploads** — uploading requires a direct connection to the official site (proxy/VPN or an enterprise leased line). You can test connectivity first with `curl -I https://huggingface.co`.
>
> **⚠️ Note 3 (permissions):** The token must be a **Write** token; uploading with a read-only token fails with a 403 error.
>
> **⚠️ Note 4 (private):** `--dataset.private=true` makes the repository private; for internal sharing you can drop it or set `false`.

---

## Step 3: Replay Verification (Optional but Recommended)

Once recording is complete, you can replay an episode with `lerobot-replay` to verify **data quality and that the robot's recorded motions are correct**. During replay, the robot automatically re-enacts that episode's motions (including the hand's open/close).

```bash
lerobot-replay \
  --robot.type=so101_amazing_hand \
  --robot.port=<follower-port> \
  --robot.hand_port=<hand-port> \
  --robot.id=amazing_hand_follower \
  --dataset.repo_id=soarm_amazing_hand_pick \
  --dataset.root=~/lerobot_data \
  --dataset.episode=0
```

> Replace `<follower-port>` / `<hand-port>` with the actual device paths; `--dataset.episode` is the index of the episode to replay (**starting from 0** — with 20 recorded episodes, the values are `0`-`19`).

> **💡 Note:** Before replay, move the follower arm + hand **back to the initial position** to avoid motion conflicts; the robot moves on its own during replay, so **do not intervene manually**. If the replayed motion clearly differs from what was recorded, the data quality is suspect — re-record that episode.

---

After completing this stage, continue to [Stage 5: Model Training](../05-training/linux.md).

---

## Troubleshooting

| Symptom | Cause | Solution |
|---|---|---|
| Camera not found | Wrong index / permissions / missing driver | Confirm with `lerobot-find-cameras`; check `/dev/video*` permissions (join the `video` group) |
| Recording interrupted | Serial port timeout | Confirm the three devices' serial ports are not occupied, then retry |
| Image all black / garbled | Wrong camera configuration | Check `index_or_path`/`fps` |
| No permission on `/dev/video*` | User not in the video group | Run `sudo usermod -a -G video $USER`, then log in again |
| Dataset is empty | Not recorded correctly | Confirm you press Enter to start/end each episode |
