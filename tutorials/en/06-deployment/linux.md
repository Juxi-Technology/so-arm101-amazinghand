# linux

# Stage 6: Deployment and Evaluation (Linux)

This stage loads the trained policy so the robot can **execute tasks autonomously**, and records evaluation videos to verify the results. This is the finale of the whole workflow and the key test of the training outcome.

---

## Prerequisites

- Stage 5: Model Training completed

- Training produced `outputs/train/soarm_amazing_hand_pick/checkpoints/last/pretrained_model/`

- The camera indices are recorded

---

## Step 1: Confirm the Model Files

```Bash
ls outputs/train/soarm_amazing_hand_pick/checkpoints/last/pretrained_model
```

It should contain model files such as `model.safetensors`.

> **⚠️ Note (model path)**: `--policy.path` must point to the `pretrained_model` directory (containing the config \+ weights), not the checkpoint root directory.

---

## Step 2: Deploy and Evaluate

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
  --policy.path=outputs/train/soarm_amazing_hand_pick/checkpoints/last/pretrained_model \
  --dataset.repo_id=soarm_amazing_hand_pick_eval \
  --dataset.root=~/lerobot_data \
  --dataset.push_to_hub=false \
  --dataset.num_episodes=10 \
  --dataset.single_task="Pick up the cube with the dexterous hand" \
  --display_data=true
```

> Replace `<follower_arm_port>` / `<hand_port>` with the actual paths; replace the camera `index_or_path` with your camera indices.

> **💡 Notes**: Use `lerobot-record` but **do not add ****`--teleop.type`**; the policy then controls the robot autonomously (replacing manual teleoperation). The data is saved as an evaluation set. `--dataset.root` / `--dataset.push_to_hub=false` are the same as in Stage 4; purely local saving requires no HF login.

---

## Evaluation Procedure

1. Return the robot \+ hand to the **starting position**

2. Press Enter to start: the policy executes the task autonomously

3. Observe **whether the grasp succeeds** (press Enter to continue after each episode)

4. Repeat for `num_episodes` episodes

**Evaluation metric**: success rate = successful episodes / total episodes

> **⚠️ Note 1 (reset consistency)**: Start every episode from the **same starting position**, otherwise the policy fails to generalize and the success rate will be artificially low.

> **⚠️ Note 2 (safety)**: On the first autonomous run, it is recommended to **keep a hand on the robot / run slowly** and observe, to confirm the policy's motions are reasonable. The policy may make unexpected movements.

> **⚠️ Note 3 (expected success rate)**: ACT typically achieves a 50\-80% success rate with 20 episodes of data. If it is lower than expected, go back and record more data or adjust the training step count.

> **⚠️ Note 4 (headless environment)**: `--display_data=true` requires a display server; in a GUI-less environment, remove this parameter (evaluation still runs, it just won't display in real time).

---

## Iterative Optimization

If the evaluation success rate is unsatisfactory, adjust in order of priority:

|Priority|Optimization|Action|
|---|---|---|
|1|Record more high-quality data|Go back to Stage 4 and record an additional 20\-30 more consistent episodes|
|2|Increase the training step count|Go back to Stage 5, `--steps=100000`|
|3|Check starting-position consistency|Strictly reset before every evaluation episode|
|4|Adjust the task description|Make sure `single_task` matches the task|

---

This completes the **full closed loop** of SO\-ARM101 \+ AmazingHand: calibration → teleoperation → collection → training → deployment.

---

## Troubleshooting

|Symptom|Cause|Solution|
|---|---|---|
|Model fails to load|Wrong/incomplete path|Confirm `--policy.path` points to the `pretrained_model` directory|
|Policy does not move|Camera/observation error|Confirm the camera indices match those at training time; check `/dev/video*` permissions|
|Policy moves erratically|Inconsistent starting position / poor data|Reset strictly; record more data|
|Behavior differs from training|Environment differences|Confirm the cameras, lighting, and object positions match those at recording time|

