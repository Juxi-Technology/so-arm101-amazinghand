# Stage 6: Deployment and Evaluation (Linux)

In this stage you load the trained policy, let the robot **execute tasks autonomously**, and record evaluation videos to verify the results. This is the final step of the whole pipeline and the key test of your training results.

---

## Prerequisites

- Completed [Stage 5: Model Training](../05-training/linux.md)
- Training produced `outputs/train/soarm_amazing_hand_pick/checkpoints/last/pretrained_model/`
- Camera indices recorded

---

## Step 1: Verify the Model Files

```bash
ls outputs/train/soarm_amazing_hand_pick/checkpoints/last/pretrained_model
```

It should contain model files such as `model.safetensors`.

> **⚠️ Note (model path):** `--policy.path` must point to the `pretrained_model` directory (config + weights), not the checkpoint root directory.

---

## Step 2: Autonomous Evaluation (No Recording)

```bash
lerobot-rollout \
  --strategy.type=base \
  --policy.path=outputs/train/soarm_amazing_hand_pick/checkpoints/last/pretrained_model \
  --device=cuda \
  --robot.type=so101_amazing_hand \
  --robot.port=<follower-port> \
  --robot.hand_port=<hand-port> \
  --robot.id=amazing_hand_follower \
  --robot.cameras='{
    top: {type: opencv, index_or_path: 1, width: 640, height: 480, fps: 30},
    wrist: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 30}
  }' \
  --task="Pick up the cube with the dexterous hand" \
  --duration=60 \
  --play_sounds=false
```

> Replace `<follower-port>` / `<hand-port>` with the actual device paths; verify the camera `index_or_path` values with `lerobot-find-cameras`.

> **⚠️ Note (must use `lerobot-rollout`):** Use `lerobot-rollout` for deployment evaluation, **not** `lerobot-record` — the latter requires `--teleop.type` and cannot be used for autonomous policy execution.

### Parameters

| Parameter | Description |
|---|---|
| `--strategy.type=base` | Autonomous execution with **no recording** (pure evaluation). Options: `episodic` (record evaluation data), `sentry` (continuous recording + auto upload), `highlight` (ring buffer saved by keypress), `dagger` (human-in-the-loop) |
| `--policy.path` | Trained model directory; **must point to `pretrained_model`** (contains `config.json` + weights), not the checkpoint root directory |
| `--device` | `cuda` or `cpu`. **Always use `cuda` if you have an NVIDIA GPU**; CPU inference is 5-10x slower and the robot's motion will be noticeably slow |
| `--robot.type` | `so101_amazing_hand` (follower arm + dexterous hand combo) |
| `--robot.port` | Follower arm serial port |
| `--robot.hand_port` | Hand serial port |
| `--robot.id` | Robot identifier; must match the one used during calibration |
| `--robot.cameras` | Camera configuration; **camera names and index order must match training** |
| `--task` | Task description; **must match the `--dataset.single_task` used during training exactly** |
| `--duration` | Number of seconds to run. `60` = run for 60 seconds then stop automatically; `0` = unlimited (stop manually with `Ctrl+C`) |
| `--play_sounds` | Voice announcements. On machines without a TTS backend, `false` is recommended (avoids errors and blocking) |
| `--display_data=true` | Open the Rerun visualization window (optional; uses extra CPU) |

> **💡 Other tunable parameters:**
> - `--fps=30`: control frequency (default 30). If inference can't keep up, the warning reports the actual frame rate
> - `--policy.n_action_steps`: number of actions executed consecutively after each inference (default 100). **Don't lower this on slow machines** — lowering it makes "re-inference" more frequent and the motion stuttery; keeping the default is actually smoother (one trajectory in a single pass)
> - `--interpolation_multiplier`: action interpolation multiplier; a larger value makes motion smoother
> - `--return_to_initial_position=false`: keep the current pose at the end instead of automatically returning to the initial position

---

## Step 3: (Optional) Record Evaluation Data

If you only need to verify the success rate, Step 2 is enough (**it produces no files**). To save evaluation data for analysis or extra recordings, switch to the `episodic` strategy and specify a dataset:

```bash
lerobot-rollout \
  --strategy.type=episodic \
  --policy.path=outputs/train/soarm_amazing_hand_pick/checkpoints/last/pretrained_model \
  --device=cuda \
  --robot.type=so101_amazing_hand \
  --robot.port=<follower-port> \
  --robot.hand_port=<hand-port> \
  --robot.id=amazing_hand_follower \
  --robot.cameras='{
    top: {type: opencv, index_or_path: 1, width: 640, height: 480, fps: 30},
    wrist: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 30}
  }' \
  --task="Pick up the cube with the dexterous hand" \
  --duration=0 \
  --play_sounds=false \
  --dataset.repo_id=soarm_amazing_hand_pick_eval \
  --dataset.root=~/lerobot_data/soarm_amazing_hand_pick_eval \
  --dataset.single_task="Pick up the cube with the dexterous hand"
```

> **⚠️ Note (base produces no files):** `--strategy.type=base` is pure evaluation and **writes no files**. Only `episodic` / `sentry` / `highlight` / `dagger` with `--dataset.repo_id` will record, and the data lands in the directory given by `--dataset.root`.

> **💡 `episodic` characteristics:** Behavior is closest to [Stage 4 recording](../04-data-collection/linux.md) — after each `episode_time_s`-second episode it enters the `reset_time_s` reset phase, during which the arm is moved back to its initial position; ideal for "evaluating while topping up the dataset". Keyboard: `n`=end the episode, `r`=re-record, `q`=stop.

---

## Evaluation Procedure

1. Reset the robot arm + hand to the **initial position** and place the object at its starting point from recording
2. Once started, the policy **begins executing automatically** (no key presses needed)
3. Observe whether the grasp succeeds
4. After an episode ends, **reset manually** (both the object and the arm back to their initial positions) and wait for the next one to begin
5. It stops automatically when the `--duration` time is up, or press `Ctrl+C` to end early

**Evaluation metric:** success rate = successful attempts / total attempts

> **⚠️ Note 1 (single-episode policy):** The policy learned the "grasp once" task and **does not loop autonomously**. After it finishes grasping it doesn't know what to do and stops; a manual reset is required to start the next episode.
>
> **⚠️ Note 2 (reset thoroughly):** It's not enough to put the object back — **the arm must also return to its initial pose**. Otherwise the policy sees images outside its training distribution and will respond sluggishly or move erratically.
>
> **⚠️ Note 3 (safety):** For the first autonomous run, stand near the emergency stop and watch to confirm the motions are reasonable. When `--duration` elapses, the program **automatically moves the arm back to its initial position before disconnecting** (the hand will open — this is normal).
>
> **⚠️ Note 4 (exit order):** Press `Ctrl+C` in the terminal first — **don't close the Rerun window first**, or the process will get stuck in gRPC pushes and `Ctrl+C` will stop working.
>
> **⚠️ Note 5 (expected success rate):** ACT typically achieves a 50-80% success rate with 20 episodes of data. If it misses at certain positions, it usually means **the training data didn't cover that spot** — just record more.
>
> **⚠️ Note 6 (headless environment):** `--display_data=true` requires a display server; drop that parameter when there's no GUI (the evaluation still runs, it just isn't displayed in real time).

---

## Iterative Optimization

If the evaluation success rate is unsatisfactory, adjust in priority order:

| Priority | Improvement | Action |
|---|---|---|
| 1 | Record additional high-quality data | Go back to [Stage 4](../04-data-collection/linux.md) and record 20-30 more consistent episodes |
| 2 | Increase training steps | Go back to [Stage 5](../05-training/linux.md), `--steps=100000` |
| 3 | Check initial-position consistency | Reset strictly every episode during evaluation |
| 4 | Adjust the task description | Make sure `single_task` matches the task |

---

This completes the **full loop** for SO-ARM101 + AmazingHand: calibration → teleoperation → data collection → training → deployment.

---

## Troubleshooting

| Symptom | Cause | Solution |
|---|---|---|
| Error asking for `--teleop.type` | `lerobot-record` was used | Deployment must use `lerobot-rollout` |
| Model fails to load | Wrong/incomplete path | Make sure `--policy.path` points to the `pretrained_model` directory |
| Policy doesn't move | Wrong camera/observation | Make sure the camera indices match training; check `/dev/video*` permissions |
| Policy moves erratically | Inconsistent initial position / poor data | Reset strictly; record more data |
| **Stuttery motion** | `--policy.n_action_steps` was lowered, re-inference too frequent | **Remove that parameter and use the default** (don't lower it on slow machines) |
| **Stops after grasping** | A single-episode policy doesn't loop autonomously | Expected behavior; manually reset the object + arm and run again |
| **Very slow + frame-rate warnings** | CPU inference (`--device=cpu`) | Switch to an NVIDIA GPU and use `--device=cuda` |
| **Ctrl+C won't stop it** | Rerun window closed first; process stuck in gRPC pushes | Press Ctrl+C in the terminal first; if already stuck, kill the process with `kill` |
| Performance differs from training | Environment differences | Make sure the camera, lighting, and object position match the recording setup |
