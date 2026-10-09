# win

# Stage 5: Model Training (Windows)

This stage trains a policy (ACT, etc.) on the collected dataset to produce a deployable model. Training is the most time-consuming step, so **an NVIDIA GPU is recommended**.

---

## Prerequisites

- Stage 4: Data Collection completed

- NVIDIA GPU (recommended) and the CUDA driver

- The dataset is recorded (visible in the local cache)

---

## Step 1: Confirm the GPU Environment

```PowerShell
python -c "import torch; print('CUDA:', torch.cuda.is_available(), '| GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A')"
```

**Expected output**: `CUDA: True | GPU: <your_gpu_name>`

> **⚠️ Note (CUDA torch)**: If `CUDA: False`, you have the CPU build of torch installed. You need to reinstall the CUDA build:

```PowerShell
# Official source (for overseas networks)
pip install torch --index-url https://download.pytorch.org/whl/cu128

# On networks in mainland China, prefer the Aliyun mirror
pip install torch --index-url https://mirrors.aliyun.com/pytorch-wheels/cu128
```

> Or train on CPU (`--policy.device=cpu`, but it is much slower and impractical for complex tasks).

---

## Step 2: Training

```PowerShell
lerobot-train `
  --dataset.repo_id=soarm_amazing_hand_pick `
  --dataset.root=D:\lerobot_data `
  --policy.type=act `
  --output_dir=outputs/train/soarm_amazing_hand_pick `
  --job_name=soarm_amazing_hand_pick `
  --policy.device=cuda `
  --wandb.enable=false `
  --policy.push_to_hub=false `
  --steps=60000
```

> **💡 Notes**: `--dataset.repo_id` and `--dataset.root` must be **exactly the same** as when recording in Stage 4 (`repo_id=soarm_amazing_hand_pick`, `root=D:\lerobot_data`); the local dataset will then be read with no HF login required.

---

## Parameter Reference

|Parameter|Description|
|---|---|
|`--dataset.repo_id`|Dataset name (same as when recording)|
|`--dataset.root`|Local dataset path (same as when recording)|
|`--policy.type`|Policy type; `act` is the common choice|
|`--output_dir`|Training output directory (checkpoints, logs)|
|`--job_name`|Job name (used to distinguish logs)|
|`--policy.device`|`cuda` (GPU) or `cpu`|
|`--wandb.enable`|Weight logging; `false` disables it (no wandb account needed)|
|`--policy.push_to_hub`|Whether to push the model to HF; `false` keeps it local only|
|`--steps`|Number of training steps|

---

## About the Training Process

- **checkpoints**: Saved automatically at each step to `outputs/train/soarm_amazing_hand_pick/checkpoints/`

- **Logs**: The terminal displays metrics such as loss in real time

- **Duration**: 60,000 steps usually take several hours on a consumer-grade GPU (depending on the specific card)

> **⚠️ Note 1 (adjusting the step count)**: `--steps=60000` is a typical value for ACT. For simple tasks you can reduce it to 30,000; for complex tasks you can increase it to 100000\+. Watch how the loss converges.

> **⚠️ Note 2 (resuming after an interruption)**: After an interruption, rerunning **the same command with the same parameters** continues from the last checkpoint.

> **⚠️ Note 3 (wandb)**: To visualize the loss curve, enable `--wandb.enable=true` (requires `wandb login`). It is disabled by default.

> **⚠️ Note 4 (memory/VRAM)**: If VRAM is insufficient, add `--policy.batch_size=8` (reduce the batch size); if memory is insufficient for video decoding, reduce `width/height`.

---

Once this stage is complete, proceed to Stage 6: Deployment and Evaluation.

---

## Troubleshooting

|Symptom|Cause|Solution|
|---|---|---|
|`CUDA: False`|CPU build of torch|Reinstall the CUDA build of torch|
|Out of VRAM (OOM)|Batch size too large|`--policy.batch_size=8` or lower|
|Dataset not found|repo\_id/root mismatch|Confirm `--dataset.repo_id` and `--dataset.root` are exactly the same as when recording|
|Training is slow|CPU training|Use a GPU; or reduce `--steps`|
|`wandb` error|Not logged in|`--wandb.enable=false` or `wandb login`|

